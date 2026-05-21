# Quiz — Unit 11

1. State the core discipline this unit teaches for judging an old design decision.
2. Why is AOROM a **keep** for this game rather than a limitation to fix?
3. Why does the parallel-array RAM layout still hold up today?
4. Give one "change" and name the **1989 constraint** that no longer binds.
5. Why is "the CPU can be wrong" a reasonable modern change but was a reasonable
   omission in 1989?
6. How few bytes, roughly, does it take to make Skill Level matter, and where would
   it hook?
7. Name two designs you should **resist** changing, and why.
8. What distinguishes an "improvement" from "a different game"?
9. For a proposed change, what makes it *actionable* in this project's workflow?
10. Pick any "keep" from the lesson and defend it in one sentence.

<details>
<summary>Answer key & scoring</summary>

1. Judge by **constraint, not taste**: ask what 1989 constraint made it right and
   whether that constraint still exists. *(§ "The discipline")*
2. The board **never scrolls**; single-screen mirroring + coarse banks are exactly
   enough — more mapper is over-engineering. *(§ "What's perfect")*
3. Column-wise per-seat data makes **"do X to every player"** a tight indexed loop;
   still the right layout. *(§ same)*
4. Any row: e.g. **seeded boards** — the dead constraint is "a seed UI costs ROM /
   players didn't expect one." *(§ "What we'd change")*
5. Modern: space/tooling cheap and "buzz ⇒ correct" feels off. 1989: a **second AI +
   animation system** cost ROM and effort. *(§ table)*
6. A **few bytes**, hooking the **reaction-time table `$A80D`** index (difficulty
   `$9B`). *(§ table)*
7. Any two: don't add scrolling to a static board; don't add deep strategy AI; don't
   force a heavy RNG if keeping the party feel — each **erases character**.
   *(§ "The trap")*
8. An improvement **preserves the game's character**; replacing that character makes
   it a different game. *(§ "The trap")*
9. Stated as a **testable spec** and filed as a **tagged** entry in
   `ROMHACK-IDEAS.md`. *(§ "Exercise" / "discipline")*
10. Any defensible keep (e.g., "the frame counter is one elegant, debuggable clock
    for every timer"). *(§ "What's perfect")*

**Scoring:** 8-10 → Unit 12. 5-7 → re-read flagged sections. 0-4 → redo the exercise.
</details>
