# Screen 06 — Answer Input · Depart

**This screen departs:**

- After the Answer Timer reaches **0**, **or**
- When the in-control player selects **"End"**.

With a confirmation sound.

> **ROM correlation:** the timeout is a frame-counter (`$01`) branch; the "End"
> commit is a controller read. Both routes hand off to **Screen 05 — Player
> Podium** to judge the typed response and animate the score change.
