# Screen 08 — Final Jeopardy · Arrive

**This screen is shown:**

- With a theme.
- After the leader is shown following Double Jeopardy, from **Screen 05**.
- Depending on various conditions:
  - With an **instructions** text blob.
  - **Per each player:**
    - With a Screen 07-styled **wager entry** screen.
    - With a multiplayer-sensitive screen saying **which player should respond**.
- After a player has completed **Screen 06** and there are remaining players.

## Design notes

- This was thoughtful for players who wanted to play multiplayer at home but not
  get **spoiled by each other's answers** — each player wagers and answers in turn,
  privately.

> **ROM correlation:** the per-player loop iterates the contestant index `$70`
> (seats 0–2), reusing the wager UI from Screen 07 and the answer UI from Screen 06
> once per remaining player. How a **CPU** opponent wagers and answers in Final
> Jeopardy is part of the still-unmapped **wager AI** (see [`../ROADMAP.md`](../ROADMAP.md)).
