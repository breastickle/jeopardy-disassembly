# The NPC contestants — names, looks, and the "limited AI"

This is focus area #3. The two computer opponents are cheap to run and
intentionally simple: they are picked a random name and face, and they
"play" through a single mechanic — a **reaction-time roll** that doubles
as a knows-it / doesn't-know-it check. All addresses are byte-verified
against the stock dump with `tools/disasm6502.py`.

## Per-contestant state

The three seats (you + two CPU) are indexed by **`$70`** (current
contestant; copies live in `$77`, `$78`). Most per-seat data is a small
array indexed by that seat number or a 6× multiple of it:

| RAM | Meaning |
| --- | --- |
| `$70` / `$77` / `$78` | current contestant index (0-2) |
| `$05AF + seat*6` | the seat's 6-character name (copied from `$8DF9`) |
| `$05CF,X`, `$0620,X` | appearance / portrait attributes |
| `$8F`, `$90` | CPU buzz-in countdown timers (seats 2 and 3) |
| `$AE,X`, `$85,X`, `$84` | per-seat buzz/lockout flags |
| `$05B4`, `$03D2` | opponent count / round mode |
| `$9B` | selected clue difficulty (board row), drives the AI |

## Names — a random draw with no repeats

The name pool is plain text at **`$8DF9`** (file `0x0E09`), comma-
delimited (`$2C`), six characters per slot: `ALEX` (the host), then
`GEORGE`, `VERNON`, `NORM`, `ROGER`, `BLAKE`, `HARRIS`, `IRIS`, `LORI`,
`ALEXIS`, `LIZ`, `BONNIE`, `JENNY`, `HELENE`, `TONI`, … Each name is
rendered with the engine's text codec (`tile = char − $2C`; see
`text-format.md`).

The picker (`$8E5C`) turns an RNG byte into a slot, copies six bytes, and
**re-rolls if the name is already taken** by another seat:

```asm
8E63  LDA $03 / AND #$0E / LSR / ORA $0F / STA $16   ; $16 = name index from RNG $03
8E6C  LDA $16 … TAY                                  ; Y = $16 * 6  (6-byte records)
8E75  LDA $70 … TAX                                  ; X = seat  * 6
8E82  LDA #$06 / STA $11                             ; copy six characters …
8E86  LDA $8DF9,Y / SBC #$2C … STA $05AF,X           ;   decode + store to the seat
8E96  DEC $11 / BNE $8E86
8E9E  JSR $8B76 …                                    ; is this name already used?
8EA1  BEQ $8EB7                                      ;   yes -> re-roll
…
8EB7  LDA $02 / AND #$03 … ADC $16 / AND #$07 …      ; nudge to a new slot
8ECC  JMP $8E6A                                      ;   and try again
```

Same "draw, reject collisions, retry" shape as the board bag in
`randomizer.md` — the two CPUs never share a name.

## Faces — random, also de-duplicated

Portraits/attributes are rolled the same way (`$8F0C`), with a dedup
against `$05D1` so the opponents don't look identical:

```asm
8F0C  JSR $9027
8F0F  LDA $02 / AND #$08 / STA $0F
8F15  LDA $03 / AND #$08 / ADC $0F
8F1C  ORA $05CF,X / STA $0620,X     ; appearance attribute, per seat
```

The little "contestants walk on" intro is choreographed off the frame
counter `$01` (`CMP #$14`, `CMP #$40` checkpoints at `$8F23`), not by any
AI.

## The AI: one reaction-time roll per clue

When a clue is revealed (`$9E0D` and `$A514` call it), the engine rolls a
buzz-in delay for **each** CPU seat from a table, indexed by the clue's
difficulty plus a little random jitter:

```asm
A7F2  LDA $02 / AND #$03      ; 2-bit random jitter
A7F6  CLC / ADC $9B           ; + clue difficulty (board row)
A7F9  TAY
A7FA  LDA $A80D,Y             ; look up a reaction delay …
A7FD  STA $8F                 ;   seat-2 buzz timer
A7FF  LDA $03 / AND #$03      ; independent jitter for seat 3
A804  ADC $9B
A807  LDA $A80D,Y
A80A  STA $90                 ;   seat-3 buzz timer
```

The table is **`$A80D` = `FF FF 88 5C 48 FF FF 6E 24 FF FF 38`**. Two
kinds of entry:

- **`$FF` → "doesn't know it."** The countdown code refuses to run a
  timer `>= $D8` (see below), so an `$FF` seat simply never buzzes on
  this clue.
- **anything smaller → a reaction delay in frames** (`$24`=36 ≈ 0.6 s,
  `$88`=136 ≈ 2.3 s). Smaller = quicker on the buzzer.

Because `$9B` (difficulty) shifts the starting index and the 2-bit RNG
jitter slides within it, harder clues land on table regions seeded with
more `$FF`s — so the CPUs miss more of the expensive clues. The two seats
draw from independent RNG bytes (`$02`, `$03`), so they compete with
different reaction times each clue.

### Counting down and buzzing (`$9740`)

Each frame (throttled to odd frames via `$01 AND #$01`), the live timers
tick down; the first to hit zero buzzes:

```asm
973A  LDA $01 / AND #$01 / BEQ …      ; only count on alternate frames
9740  LDA $8F / CMP #$D8 / BCS $9751  ; seat 2: $D8+ means "won't buzz"
9746  DEC $8F / BNE $9751             ; tick; not zero yet -> wait
974A  LDX #$02 …                      ; reached 0 -> seat 2 buzzes in
9751  LDA $90 / CMP #$D8 / BCS …      ; seat 3: same
9757  DEC $90 / BNE …
975B  LDX #$03 …                      ; seat 3 buzzes in
```

### What the model is (and isn't)

- **Knows-it is the reaction roll.** A non-`$FF` delay *is* the CPU
  "knowing" the clue; it then counts down and rings in. There is no
  separate "CPU rang in but answered wrong" path in this loop — a CPU
  that buzzes is treated as correct, and a CPU that "doesn't know"
  (`$FF`) just stays silent. That is the whole of the limiting: a lookup
  table of reaction times salted with misses, weighted by clue value.
- **No learning, no board strategy.** The CPUs do not reason about which
  category to pick or hunt Daily Doubles; selection-turn behaviour is
  driven by the same timers and the round state machine, not by any
  evaluation of the board.
- **Difficulty is positional.** "Harder" simply means a higher board row
  (`$9B`), i.e. the higher-dollar clues — not anything about the clue
  text, which the engine never inspects.

## Daily Double placement (related randomness)

The Daily Doubles are hidden in random board cells by `$9A89`: it draws a
cell `0-29` (`AND #$1F`, folded back into range by `CMP #$1E / EOR #$04`)
into `$9F`, and a second non-colliding cell into `$A0` for Double
Jeopardy. The 30 per-cell answered-flags live at `$05D6,X` (X = 0-29 =
6 columns × 5 rows).

## Developer decisions (kept brief)

- **A table, not a model.** Twelve bytes (`$A80D`) plus two RNG draws is
  the entire opponent "intelligence." It is cheap, deterministic to tune
  (edit the delays / `$FF`s to make the CPUs easier or harder), and good
  enough to feel like two opponents of differing speed. A scoring/strategy
  AI would have cost far more ROM and RAM for a party quiz game that
  didn't need it.
- **Buzz ⇒ correct.** Folding "knows it" into the buzz roll avoids a
  second correctness system and a wrong-answer animation path for the
  CPUs. The trade is that computer opponents never give a wrong response
  on the buzzer — a simplification most players never notice.

## Open / not yet pinned

- **Wagering AI** for Daily Double and Final Jeopardy (how a CPU chooses
  a bet relative to its score) was not located in this pass; it is a
  separate routine to trace from the Daily Double / Final Jeopardy
  states.
- The exact pixel-to-`$9B` mapping at `$8DD6` (which board rows yield
  which table indices) needs the board cursor geometry to be confirmed.

## Reproduce

```sh
ROM="../jeopardy-nescard-ips/Clean ROM for Python Probe.nes"
python tools/disasm6502.py "$ROM" --bank 0 --linear A7F2 A80D   # the reaction roll
python tools/disasm6502.py "$ROM" --bank 0 --dump   A80D A819   # reaction-time table
python tools/disasm6502.py "$ROM" --bank 0 --linear 9736 975C   # buzz countdown
python tools/disasm6502.py "$ROM" --bank 0 --linear 8E5C 8ED0   # name picker
python tools/disasm6502.py "$ROM" --bank 0 --dump   8DF9 8E5C   # name pool text
```
