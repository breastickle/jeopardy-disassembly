# Quiz — Unit 2

1. What kind of chip is inside an NES controller, and what does "parallel-in /
   serial-out" mean for how the CPU reads it?
2. Write the two-step **strobe** sequence (in words or asm) and say what the "5 V
   latch" physically does.
3. List the eight buttons in the order they clock out of `$4016`.
4. Which register is controller 2, and at what address does *Jeopardy* read it?
5. What goes wrong if you read `$4016` **without** strobing first?
6. Give the boolean expression for **newly-pressed** buttons in terms of this
   frame's and last frame's reads.
7. Why do menus act on "newly pressed" rather than "held"?
8. In FCEUX, what breakpoint catches the **read** of player 1's pad, and what
   breakpoint catches the **strobe**?
9. Besides bit 0, why can the other bits of a `$4016` read be unreliable?
10. Trace the chain: pressing Start on the Main Menu causes which three things?

<details>
<summary>Answer key & scoring</summary>

1. A **CD4021 shift register**; the CPU loads all 8 buttons in parallel on the
   strobe, then reads them out **one bit at a time** over successive reads.
   *(§ "The controller is a shift register")*
2. **Write 1 to `$4016`, then write 0.** While the strobe is high the eight button
   contacts are latched into the register in parallel. *(§ "Step 1 — strobe")*
3. **A, B, Select, Start, Up, Down, Left, Right.** *(§ "Step 2 — read 8 bits")*
4. **`$4017`**; *Jeopardy* reads it at **`$9089`**. *(§ "Where Jeopardy reads")*
5. You read a **stale or mid-shift** value — the register wasn't reloaded with the
   current button state. *(§ "Step 1")*
6. `newly = buttons AND (NOT previous_buttons)`. *(§ "Held vs newly pressed")*
7. So one physical press = **one** action; holding wouldn't repeat-fire the menu.
   *(§ "Held vs newly pressed")*
8. **Read** breakpoint on `4016` (stops at `$9083`); **Write** breakpoint on `4016`
   (stops at the strobe instruction). *(§ "FCEUX Lab")*
9. The upper bits are **open bus**, and **DPCM/DMA** can corrupt the read; robust
   code masks bit 0 or reads twice. *(§ "Step 2" note)*
10. It registers as **newly-pressed Start**, plays an **acknowledgment sound**, and
    flips **`$6E`** toward Screen 02. *(§ "Following Start")*

**Scoring:** 8-10 → Unit 3. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
