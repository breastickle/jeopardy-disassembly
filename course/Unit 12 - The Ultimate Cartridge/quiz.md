# Quiz — Unit 12 (Capstone)

1. Why is a **mapper upgrade** the keystone of the combined build rather than just
   one feature among many?
2. What does MMC1 give that AOROM doesn't, in the vocabulary of the glossary?
3. Roughly how much bank-tail space does dropping the per-bank trampolines reclaim?
4. Why must "more clues" come **after** the mapper stage?
5. Seeded RNG and timing-based RNG seem to conflict. State the resolution.
6. Adding a "CPU can be wrong" roll has a dependency other QoL hacks don't. What is
   it?
7. Why should QoL speedups ship as **options** rather than defaults?
8. Why can't the combined build be distributed as a simple IPS over the stock ROM?
9. List four checks from the post-stage test matrix.
10. Name the five sections your `ULTIMATE-CART.md` capstone must contain.

<details>
<summary>Answer key & scoring</summary>

1. Most ambitious features **need ROM capacity**, which AOROM's tax/ceiling block;
   the mapper unlocks them, so it gates the graph. *(§ "The keystone")*
2. A **fixed bank** — the **"core"** AOROM lacks — plus 16 KB-granular switchable
   banks. *(§ same)*
3. About **450-525 bytes** (one trampoline copy instead of per-bank). *(§ same)*
4. Capacity is unlocked **by the mapper**; adding clues first has nowhere to go.
   *(§ "dependency-ordered build")*
5. Make the seed **optional**: if entered, load `$02/$03/$FE` and bypass the idle
   churn; else keep timing entropy. *(§ "Resolving the conflicts")*
6. It needs the **disappointed-CPU / score-loss path** to exist for a CPU — reaching
   into the podium/scoring systems. *(§ same)*
7. So they **don't erase the original game feel** (U11). *(§ same)*
8. A mapper-converted ROM is a **new base**; an IPS over stock won't apply — ship as
   converted base + content patch. *(§ same)*
9. Any four: cold/soft reset, every screen 00-08, clue display from all 4 blobs,
   Daily Double (1 & 2), Final Jeopardy, scoring at limits, `verify.py`. *(§ "test
   matrix")*
10. **Feature list (tagged), dependency graph, conflict resolutions, test matrix,
    risk register.** *(§ "Capstone deliverable")*

**Scoring:** 8-10 → 🎓 you've completed the course. 5-7 → revisit the conflict and
dependency sections. 0-4 → re-read with Units 1, 4, 6, 8, 11 open alongside.
</details>
