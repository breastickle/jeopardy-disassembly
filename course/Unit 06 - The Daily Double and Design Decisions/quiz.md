# Quiz — Unit 6

1. How many Daily Doubles are placed in the Jeopardy round vs Double Jeopardy, and
   which RAM byte gates the difference?
2. Which two addresses hold the Daily Double cell(s)?
3. The board has 30 cells. How does `$9A89` force a random byte into the range
   0-29?
4. Why does the second Daily Double placement include a dedup check?
5. What player-facing event happens when a selected cell matches `$9F`/`$A0`?
6. Describe the two wager-entry formats and the condition that chooses between them.
7. List the five steps of the "ask why like an engineer" loop.
8. Which design decision in the table is **confirmed by code** rather than merely
   plausible, and why?
9. Why is "the CPUs are always right when they buzz" a *cheap* decision for GameTek?
10. In FCEUX, how would you confirm which wager format a given score produces?

<details>
<summary>Answer key & scoring</summary>

1. **1** in Jeopardy, **2** in Double Jeopardy; gated by **`$03D2`** (round mode).
   *(§ "Placing the Daily Double(s)")*
2. **`$9F`** and **`$A0`**. *(§ same)*
3. `AND #$1F` (0-31), then `CMP #$1E / BCC / EOR #$04` folds 30/31 back into range.
   *(§ same)*
4. So the **two Daily Doubles don't land in the same cell**. *(§ same)*
5. The clue **diverts to Screen 07 (the wager)** instead of revealing directly.
   *(§ same)*
6. **Numeric entry** when score is above the minimum; **prefab A-E** when below a
   threshold; a **score comparison** selects. *(§ "Two ways to wager")*
7. Observe → hypothesize → find the constraint → look for counter-evidence → mark
   confidence. *(§ "Asking why")*
8. **1 DD vs 2 DD by round** — the `$03D2` gate is right there in code. *(§ table)*
9. It needs **one system, not two** — no separate correctness roll, wrong-answer AI,
   or disappointed-CPU animation path. *(§ table)*
10. Tank a score and trigger a DD (expect prefab); raise the score and retrigger
    (expect numeric); then find the `CMP` threshold. *(§ "FCEUX Lab")*

**Scoring:** 8-10 → Unit 7. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
