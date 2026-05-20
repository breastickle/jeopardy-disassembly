# Screen 05 — Player Podium · Arrive

**This screen is shown:**

- When a player **rings in** from **Screen 04**.
- When a player **inputs a response** from **Screen 06**.
- Between Jeopardy and Double Jeopardy, to show the current lead.
- After all players have finished responding to Final Jeopardy, to reveal the
  final results.

## Design notes

- This is likely the **same scene as Screen 03**, just repurposed during
  gameplay. If so, this game would have a tidy **8 scenes — one for each bit of
  the NES**.

> **ROM correlation:** the state machine (`$6E` → jump table `$8901`) is built
> from a *small, repeating* set of handler addresses (the table cycles through a
> handful of targets such as `$89C8` / `$8F46` / `$8FC1`), which is exactly what
> "one scene reused for several screens" would look like. Confirming that Screen 03
> and Screen 05 dispatch to the **same handler** is the cleanest way to test your
> 8-scenes hypothesis — see [`../ROADMAP.md`](../ROADMAP.md). Scores shown here are
> the per-seat digit array `$25,X` (stride 5).
