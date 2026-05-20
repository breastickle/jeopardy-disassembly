# Screen 07 — Daily Double · Depart

**This screen departs:**

- When the player selects **End** (with a confirmation sound), **or**
- Some frames after the timer reaches **zero**.

Either way, play proceeds to **Screen 06 — Answer Input** for the response.

> **ROM correlation:** as with the other timed prompts, the timeout is a frame
> counter (`$01`) branch and the commit is a controller read. The wager amount
> entered here feeds the score math applied back on **Screen 05**.
