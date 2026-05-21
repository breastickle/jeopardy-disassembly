# Quiz — Unit 4

1. *Jeopardy* has no clock or hardware RNG. Where does the randomness in the board
   actually come from?
2. Name the RNG routine's address and the zero-page byte that holds its output.
3. Why does the idle loop at `$93A3` matter to randomness?
4. There is no "enter a seed" screen. What does that imply for two players who want
   the **same** board?
5. How many categories does the bag draw, and what guarantees **no repeats**?
6. What is stored in `$063C`, and why is `$FC` the "full" sentinel?
7. What are the six bytes at `$8375`, and what are they for?
8. Translate to plain English: `CMP #$06 / BCS retry`.
9. Which flag does `AND $063C,X / BNE retry` test, and what does taking the branch
   mean here?
10. In FCEUX, describe an experiment that **proves** the board depends on input
    timing.

<details>
<summary>Answer key & scoring</summary>

1. From **time/timing** — the frame counter `$01` folded into the RNG, sampled at
   the frame the player presses a button. *(§ "Randomness without a clock")*
2. **`$9027`**; output in **`$02`**. *(§ same)*
3. It **calls the RNG forever while idle**, so the state is a moving target sampled
   on input. *(§ same)*
4. They essentially **can't** force it — there's no seed; the board is as random as
   their button timing. *(§ same)*
5. **Six**; two rejection loops force the slot to **0-5** and **redraw** any slot
   already used. *(§ "The random bag")*
6. The **per-cell used-slot bitmask** (one byte per board cell); `$FC` = `11111100`
   = all six slot-bits set = full. *(§ same)*
7. `80 40 20 10 08 04` — the **six single-bit slot masks**. *(§ same)*
8. "**If A ≥ 6, branch back to retry.**" *(§ "if/then forks")*
9. The **Z flag**; taking `BNE` means **some of those bits were set** (slot already
   used) → draw again. *(§ same)*
10. Press Start; note the board. Reset, use **Frame Advance** to press Start a few
    frames later; the board differs though nothing else changed. *(§ "FCEUX Lab")*

**Scoring:** 8-10 → Unit 5. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
