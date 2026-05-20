# Gameboard randomization — the RNG and the "random bag"

This is focus area #2. The Jeopardy board shows six categories; the
engine fills them by drawing from a pool **without repeats** — the
"random bag" pattern the maintainer recognises from other GameTek
titles. There are two pieces: a **random-number generator** (`$9027`)
and a **draw-without-replacement bag** (`$82B1`/`$830C`). All addresses
are byte-verified against the stock dump with `tools/disasm6502.py`.

## 1. The RNG at `$9027` — a "stir the pot" generator

This game has no clean LFSR. Its generator is an accumulator that mixes
its own state with live game RAM and the frame counter, then rotates a
multi-byte state chain:

```asm
9027  LDA $02            ; A = primary RNG accumulator
9029  ADC $19            ; + live game-state bytes (entropy from play)
902B  ADC $1B
902D  ADC $20
902F  SBC $03D3          ; - more live RAM
9032  SBC $049E
9035  AND #$48           ; mask to two bits (%01001000)
9037  ADC #$38           ; bias
9039  ASL A              ; shift the result up
903A  ASL A
903B  ROL $FE            ; rotate the carry through a 3-byte state chain
903D  ROL $03            ;   $FE -> $03 -> $02
903F  ROL $02
9041  INC $02            ; nudge the accumulator
9043  LDA $02
9045  ADC $01            ; + the frame counter  (timing entropy)
9047  STA $02            ; new state in $02 (output byte)
9049  RTS
```

State lives in **`$02`** (the output/accumulator), **`$03`** and
**`$FE`** (carry-chain bytes). The output is read as `$02` (or `$03` for
a differently-mixed bit pattern — see the bag below).

### Where the entropy actually comes from

`$01` is a **free-running frame counter** — the bank-0 NMI does
`INC $01` at the very end of every vblank (`$938B`) before
`JMP ($0005)`. The RNG folds `$01` in on every call.

More importantly, **the generator is called continuously while the game
waits.** The idle/wait spin at `$93A3` is literally:

```asm
93A3  JSR $9027          ; churn the RNG …
93A6  JMP $93A3          ; … forever, until the NMI redirects via ($0005)
```

and the per-frame main loop also calls it (`$8890`). So `$02` is a
moving target the whole time the player is reading the board or deciding
what to do; the value in play at the instant a button is pressed is what
seeds the next draw. This is the classic GameTek approach: **randomness
is tied to player timing**, not to a saved seed. Two playthroughs that
press Start on different frames get different boards; a tool-assisted run
that presses on the same frame every time gets the *same* board.

RNG call sites (all of bank 0): `$830C`, `$832E`, `$8890`, `$8F0C`,
`$93A3`, `$9542`, `$9733`, `$9A89`.

### The draw primitive

Consumers reduce the RNG to a range two ways:

- **Masking** — `LDA $03 / AND #$07` for a 0-7 value (e.g. `$9542` then
  indexes table `$A819`), or `LDA $01 / LSR / AND #$0F` to drive the
  16-step palette cycle at `$8F93`.
- **Modulo with rejection** — the bag's uniform draw (next section).

## 2. The random bag at `$82B1` — six categories, no repeats

The board populator loops **six times** (once per category column) and
draws each column's source from a pool, marking what it takes so nothing
repeats. The pool/board scratch array is **`$063C`** — one byte per cell,
where bits 7..2 track which of the six slots are filled. Note `#$FC`
(`11111100`) is therefore the "all six slots used / full" sentinel.

The per-slot bit table is **`$8375` = `80 40 20 10 08 04`** — exactly six
single-bit masks.

### Outer loop (`$82B1`-`$830B`)

```asm
82B1  LDX $82A4,Y        ; base offset for this round (table below)
82B4  STX $0F            ; $0F = base index into $063C
82B6  LDY #$00
82B8  STY $11            ; $11 = draw counter (0..5)   <-- loop top
82BA  LDX $0F
82BC  LDY $12            ; $12 = pool size for this round
82BE  LDA $063C,X        ; find a cell that isn't full (#$FC)
82C1  CMP #$FC
82C3  BNE $82D5          ;   found one -> draw into it
82C5  INX / DEY / BNE $82BE
…                        ; (if every cell is full, reset the run to 0)
82D5  JSR $830C          ; draw a slot into the cell (up to 4 tries)
82D8  BNE $8304
82DA  JSR $830C
…
8304  LDY $11 / INY / CPY #$06 / BNE $82B8   ; six categories
830B  RTS
```

The base table `$82A4` selects where in the `$063C` pool each round
draws from: `00 00 3A 3A 3A 1D` (`$3A` = 58, `$1D` = 29) — different
rounds (Jeopardy / Double Jeopardy / etc.) start at different offsets so
they pull different category sets.

### Inner draw (`$830C`) — uniform pick + bag rejection

```asm
; --- pick a random cell in the pool: X = (RNG mod $12) + base $0F ---
830C  JSR $9027          ; advance RNG
830F  LDA $02
8311  CMP $12            ; modulo by repeated subtraction:
8313  BCC $8319          ;   while A >= range,
8315  SBC $12            ;     A -= range
8317  BCS $8311
8319  ADC $0F            ; + base
831B  TAX                ; X = chosen cell index into $063C
831C  LDA $063C,X
831F  CMP #$FC           ; cell already full? bail to caller
8321  BEQ $8374

; --- pick a random *unused slot* 0..5 within that cell (the bag) ---
832E  JSR $9027
8331  LDA $02
8333  AND #$03           ; build a candidate from RNG bits
8335  STA $07
8337  LDA $02 / AND #$04 / LSR / ADC $07 / STA $07
8340  DEC $07            ; <-- retry point
8342  LDA $07
8344  AND #$07
8346  CMP #$06           ; reject values >= 6  (only six categories)
8348  BCS $8340          ;   retry
834A  TAY                ; Y = slot 0..5
834B  LDA $8375,Y        ; that slot's bit mask
834E  AND $063C,X        ; already taken in this cell?
8351  BNE $8340          ;   yes -> draw a different slot
8353  LDA $8375,Y
8356  ORA $063C,X        ; mark the slot used
8359  STA $063C,X
835C  TYA …              ; record the chosen category slot
```

Two independent rejection loops make this a true bag:

1. `CMP #$06 / BCS retry` keeps the slot in **0-5** (six categories).
2. `LDA $8375,Y / AND $063C,X / BNE retry` rejects a slot already drawn
   for this cell, then `ORA/STA` marks it — so each of the six categories
   is placed exactly once.

## What this means in play

- The six board categories (and the order they fill) are a
  **without-replacement shuffle** of a per-round pool, indexed off
  `$82A4` and sized by `$12`.
- The shuffle is driven entirely by `$9027`, whose state is stirred by
  the frame counter and live RAM and **sampled at the moment of input**.
  There is no stored seed and no "new game seed" screen — the board is as
  random as the player's timing.
- This is the same "random bag + timing entropy" shape seen across
  GameTek's NES catalog; the structure here is a clean, compact example
  of it.

## Developer decisions (kept brief)

- **No real PRNG.** A 6502 LFSR is ~15 bytes and gives a long, flat
  period. The developers instead reused live game RAM as an entropy
  stir and leaned on input timing. It costs almost nothing and is
  "random enough" for a quiz board — but it is *not* reproducible, which
  is why there is no seed/code feature.
- **Bag over shuffle-in-place.** Drawing-with-rejection into a bitmask
  (`$063C` + `$8375`) avoids needing a scratch array of indices to
  shuffle; the cost is the occasional retry when a slot collides. For six
  items the retries are negligible.

## Open / not yet pinned

- Exactly where `$12` (pool size) and the `$82A4` index are set for each
  round, and how the chosen *episode/block* (1 of 29) maps into the
  `$063C` pool, still needs tracing from the round-setup state handlers.
- Whether the clue *values* within a category are themselves drawn or are
  fixed per episode.

## Reproduce

```sh
ROM="../jeopardy-nescard-ips/Clean ROM for Python Probe.nes"
python tools/disasm6502.py "$ROM" --bank 0 --linear 9027 904A   # the RNG
python tools/disasm6502.py "$ROM" --bank 0 --linear 82B1 830C   # bag outer loop
python tools/disasm6502.py "$ROM" --bank 0 --linear 830C 835D   # bag inner draw
python tools/disasm6502.py "$ROM" --bank 0 --dump   8375 837B   # slot bit table
python tools/disasm6502.py "$ROM" --bank 0 --find "20 27 90"    # every RNG call
```
