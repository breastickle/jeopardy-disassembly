# Unit 4 — Randomization and Board Building

> *"Where does 'random' come from on a machine with no clock and no entropy?"*

## Learning objectives

1. Read *Jeopardy*'s RNG and explain where its randomness actually comes from.
2. Follow the **random bag** that fills six categories with no repeats.
3. Read 6502 **flags and branches** — the `if/then` forks that wire it all together.

## Randomness without a clock

A 6502 has no clock, no `/dev/urandom`, no time-of-day. So how is the board random?
*Jeopardy*'s generator at **`$9027`** is a **"stir the pot" accumulator** — it mixes
its own state with live game RAM and the frame counter:

```asm
9027  LDA $02            ; the running RNG byte
9029  ADC $19 / ADC $1B / ADC $20    ; + live game state
902F  SBC $03D3 / SBC $049E          ; - more live RAM
9035  AND #$48 / ADC #$38            ; mask + bias
9039  ASL / ASL                      ; shift
903B  ROL $FE / ROL $03 / ROL $02    ; rotate a 3-byte state chain
9041  INC $02
9043  LDA $02 / ADC $01 / STA $02    ; + the frame counter $01
```

The real entropy is **time**. Two facts make that work:

1. `$01` (the frame counter) is folded in every call.
2. The idle/wait loop **calls the RNG forever** while you sit on a screen:
   ```asm
   93A3  JSR $9027
   93A6  JMP $93A3        ; churn until the NMI redirects on input
   ```

So `$02` is a blur the whole time you're reading the board, and the value present
**the exact frame you press a button** seeds what happens next. Press Start one
frame later → a different board. There is **no seed and no "new game code"** — the
randomness is your timing. (This is also why a tool-assisted run that presses on the
same frame gets the *same* board — see Unit 9.)

> Full write-up: [`../docs/randomizer.md`](../../docs/randomizer.md).

## The random bag (six categories, no repeats)

A Jeopardy board has **six categories**. The engine fills them by **drawing without
replacement** — the "bag." The board scratch array is **`$063C`** (one byte per cell;
bits 7..2 mark which of six slots are filled, so `$FC` = "full"). The per-slot bit
masks are **`$8375` = `80 40 20 10 08 04`**.

The outer loop runs six times:

```asm
82B8  STY $11            ; draw counter 0..5
...   JSR $830C          ; draw one category into a cell
8307  CPY #$06 / BNE $82B8   ; six categories
```

And the inner draw (`$830C`) is a textbook **uniform pick + rejection**:

```asm
; uniform cell index = (RNG mod $12) + base $0F
830C  JSR $9027 / LDA $02
8311  CMP $12 / BCC + / SBC $12 / BCS   ; modulo by repeated subtraction
8319  ADC $0F / TAX
; pick an unused slot 0..5 within that cell
8344  AND #$07 / CMP #$06 / BCS retry   ; only 0..5 allowed
834B  LDA $8375,Y / AND $063C,X / BNE retry   ; reject if slot already used
8356  ORA $063C,X / STA $063C,X               ; else mark it used
```

Two rejection loops = a real bag: values are forced into **0-5**, and a slot already
taken is **redrawn**. Each of the six categories lands exactly once.

## The if/then forks: 6502 flags & branches

"Many if/then routine forks" *is* 6502 control flow. There are no `if` statements —
only **flags** set by the last operation, and **branches** that test them. The four
you'll see constantly:

| Flag | Set when… | Tested by |
| --- | --- | --- |
| **Z** (zero) | result was 0 | `BEQ` (=0) / `BNE` (≠0) |
| **C** (carry) | unsigned overflow / `CMP` ≥ | `BCS` (≥) / `BCC` (<) |
| **N** (negative) | bit 7 of result set | `BMI` / `BPL` |
| **V** (overflow) | signed overflow | `BVS` / `BVC` |

`CMP #$06 / BCS retry` reads as *"if A ≥ 6, go back."* `AND $063C,X / BNE retry`
reads as *"if any of those bits are set, go back."* Once you see flags-then-branch,
the densest fork in the game becomes legible.

## FCEUX Lab

1. **Watch the pot stir.** Add `$02` and `$03` to RAM Watch. Sit on any screen and
   watch them change **every frame** — that's the idle churn.
2. **Prove timing entropy.** From the menu, press Start; note the board. Reset and
   press Start **a few frames later** (use Frame Advance to vary it). Different
   board — the only thing you changed was *when*.
3. **Watch the bag fill.** Execute breakpoint at `82B1` (`Board_RandomBag`). In the
   Hex Editor, watch the 30 bytes at `$063C` go from empty toward `$FC` as each
   category is placed. Step the inner draw `$830C` and watch a slot get rejected and
   redrawn.
4. **Read a fork.** Single-step through `$8344-$8351` and narrate each branch:
   which flag, taken or not, and why.

## What to watch for

- `$02`/`$03` **never settling** while idle — that's the entropy source.
- `$063C` bytes **accumulating bits**; `$FC` meaning "this cell is full."
- **Rejection retries** in the inner draw (a branch jumping *backwards*).
- The grammar **operation → flag → branch** everywhere.

## Bonus exercise

Write a tiny Python script that reads `../src/jeopardy.sym.json` and emits FCEUX
`.nl` name-list files (`yourrom.nes.0.nl`, …) so the debugger shows `Rng_Advance`
and `Board_RandomBag` instead of bare addresses. (Format per line: `$ADDR#Name#`.)

## Key takeaways

- The RNG is a **timing-seeded** stir of state + frame counter; **no stored seed**.
- The six categories are a **draw-without-replacement bag** using a bitmask
  (`$8375`) over a per-cell used-array (`$063C`).
- 6502 "if/then" = **set a flag, then branch**; learn the four flags and the game
  reads itself.

Next: [Unit 5 — Huffman, Text, Answer Checking, Scoring](../Unit%2005%20-%20Huffman,%20Text,%20Answer%20Checking,%20Scoring/lesson.md).
