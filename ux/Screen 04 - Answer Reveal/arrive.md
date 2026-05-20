# Screen 04 — Answer Reveal · Arrive

**This screen is shown:**

- When a player has selected a category and dollar value.
- After returning from **Screen 05** following an **incorrect response**.

With a sound effect timed to a **counting-down timer**.

> **ROM correlation:** revealing the clue is what arms the CPU opponents. The
> reaction roll at `$A7F2` sets each CPU's buzz-in countdown (`$8F`, `$90`) from
> the reaction-time table `$A80D`, indexed by the clue difficulty `$9B` plus a
> 2-bit RNG jitter. A table entry of `$FF` means that CPU "doesn't know it" and
> will stay silent. See [`../../docs/npc-ai.md`](../../docs/npc-ai.md).
