# Unit 2 — The Controller and Pressing Start

> *"How does a wire full of buttons become a `BNE`?"*

## Learning objectives

1. Explain how the NES reads a joypad: the shift register, the strobe ("5V latch"),
   and the serial bit order.
2. Read controller input in 6502 and tell **held** from **newly pressed**.
3. Locate *Jeopardy*'s controller read and follow Start to its acknowledgment.

## The controller is a shift register

Inside a standard NES pad is a **CD4021**: an 8-bit **parallel-in / serial-out
shift register**. The CPU can't read eight buttons at once over the few wires in
the cable, so it does this dance through two registers:

- **`$4016`** — controller 1 (write = strobe; read = next bit).
- **`$4017`** — controller 2 (read).

**Step 1 — strobe (the "latch").** Write **1** then **0** to `$4016`:

```asm
LDA #$01 / STA $4016    ; strobe HIGH: load all 8 button states into the register
LDA #$00 / STA $4016    ; strobe LOW: stop loading; register now holds a snapshot
```

While the strobe line is high (the **5 V latch** you asked about), the eight button
contacts are loaded *in parallel* into the register. Dropping it low freezes that
snapshot so you can clock it out one bit at a time. Forget to strobe and you read a
**stale or shifting** value — a classic beginner bug.

**Step 2 — read 8 bits.** Each **read of `$4016`** returns one button in **bit 0**
and shifts the next into place. The order is fixed:

| Read # | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Button | A | B | Select | Start | Up | Down | Left | Right |

The usual idiom packs them into one byte:

```asm
LDX #$08
loop: LDA $4016    ; bit 0 = this button
      LSR A        ; shift it into carry
      ROL buttons  ; carry -> bit 0 of the result byte
      DEX
      BNE loop
```

> Heads-up: `$4016` bit 0 is the button, but the upper bits are **open bus** and
> the DPCM sound channel can corrupt reads — robust games read twice or mask.

## Where *Jeopardy* reads the pad

The controllers are read here:

```asm
9083  LDA $4016    ; controller 1 (player 1)
9089  LDA $4017    ; controller 2 (player 2)
```

**A small mystery for the lab:** there is **no `STA $4016`** (`8D 16 40`) anywhere
in bank 0. So *where does the strobe happen?* It must be there — you can't read a
4021 without it — but it's encoded differently (e.g. `STX`/`STY $4016`) or reached
another way. You'll catch it with a Write breakpoint below.

## Held vs newly pressed

A menu must not advance ten times because you held Start for ten frames. The trick
is **edge detection**: keep last frame's buttons, and compute

```
newly_pressed = buttons AND (NOT previous_buttons)
```

A scene that acts on `newly_pressed` for Start fires **once** per press. Your UX
notes for Screen 01 add a second gate: input is **ignored entirely** until the
title has shown for some frames (so a mash on boot doesn't blow past the menu).

## Following Start to the "yes, I heard you"

On the Main Menu (Screen 01), once the input gate opens, pressing **Start**:

1. registers as a newly-pressed Start,
2. plays an **acknowledgment sound**, and
3. flips the scene variable `$6E` toward **Screen 02 — Setup Config** (Theme 03).

That's the whole input-to-reaction arc you'll trace.

## FCEUX Lab

1. **Catch the read.** `Debug → Debugger`, add a **Read** breakpoint on `4016`.
   Run, press any button → you stop at **`$9083`**. Read the loop that clocks out
   the 8 bits and note the RAM byte it `STA`s the result into (add it to RAM Watch).
2. **Solve the strobe mystery.** Remove that breakpoint; add a **Write** breakpoint
   on `4016`. Press a button. What instruction stops you? *That* is the strobe —
   note its opcode and confirm it writes 1 then 0.
3. **Edge detection.** Find where the game stores **last frame's** buttons (look
   for two adjacent button bytes, or an `AND`/`EOR` of the new read with a saved
   copy). Hold Start vs tap Start and watch the "newly pressed" byte.
4. **The acknowledgment.** On the menu, set an Execute breakpoint where `$6E`
   changes (you found it in Unit 1) and confirm Start is what trips it; listen for
   the confirm SFX.

## What to watch for

- **Strobe before read** — the write to `$4016` must precede the reads.
- The **bit order** A, B, Select, Start, Up, Down, Left, Right.
- A **held mask** vs a **pressed (edge) mask** — menus use the edge.
- The **input-lockout** window on the title before Start is accepted.

## Key takeaways

- A joypad read is **strobe (latch) then shift out 8 bits**; skipping the strobe is
  a real bug.
- *Jeopardy* reads at **`$9083`/`$9089`**; the strobe is hiding in a non-`STA`
  encoding — a perfect "find it yourself" exercise.
- **Edge detection** (`new AND NOT old`) is why one press = one action.

Next: [Unit 3 — Setting Up a Game](../Unit%2003%20-%20Setting%20Up%20a%20Game%20(RAM%20as%20Save%20File)/lesson.md).
