# Screen 05 — Player Podium · Depart

**This screen departs after a fixed number of frames spent on the relevant
animation:**

- The buzzing-in player plays their **excited** animation.
- The incorrect-response player plays their **disappointed** animation, and their
  score is **subtracted** from.
- The correct-response player plays their **success** animation, and their score
  is **added** to.
- The players look at each other for the current **lead** between Jeopardy and
  Double Jeopardy.
- The **final results** are shown at the end of the game.

> **ROM correlation:** these are timed branches off the frame counter `$01`; the
> score add/subtract operates on the per-seat digit array `$25,X`. Because the CPU
> AI uses a **"buzz ⇒ correct"** model (a CPU only rings in when it "knows it"),
> the *disappointed / score-subtracted* path is normally reached by **human**
> players. See [`../../docs/npc-ai.md`](../../docs/npc-ai.md).
