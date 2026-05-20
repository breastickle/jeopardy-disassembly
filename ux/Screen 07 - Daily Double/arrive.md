# Screen 07 — Daily Double · Arrive

**This screen is shown:**

- When **1 random clue** in Jeopardy or **2 random clues** in Double Jeopardy are
  revealed.

With a special sound effect upon reveal and a timer-countdown sound.

**Two wager formats:**

- **Format 1 — player has over the minimum wager amount:**
  - Numerical display, backspace, end buttons.
- **Format 2 — player score below threshold:**
  - Choice of pre-fab wagers (A, B, C, D, E).

> **ROM correlation (well supported):** this matches the Daily Double placement
> routine at `$9A7F`/`$9A89` precisely — it draws **one** random board cell (0–29)
> into `$9F`, and a **second** non-colliding cell into `$A0` **only when the round
> mode `$03D2` indicates Double Jeopardy**. So "1 in Jeopardy, 2 in Double
> Jeopardy" is literally what the code does. See [`../../docs/npc-ai.md`](../../docs/npc-ai.md).
>
> **Open:** how a **CPU** chooses its Daily Double wager (the wager AI) is not yet
> located — a good tracing target, alongside the Format 1 vs Format 2 threshold.
