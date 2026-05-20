# Screen 03 — Game Board Setup · Arrive

**This screen is shown after a new game is set up:**

- Prevent player control.
- Display all categories.
- Play a sound effect (noise channel?).
- Some time goes by.
- Place a dollar value on the board **every 3rd frame** until the board is full.
- Player 1 gains exclusive control.
  - Controller is shared with Player 1 & 3.

**It is also shown:**

- After returning from **Screen 04** with **no buzz-in**.
- After returning from **Screen 04** with **all active players wrong**.
- After returning from **Screen 05** with a **correct response**.
- After returning from **Screen 05** with "*n* Player is in the lead" after the
  final clue is revealed in the Jeopardy round. In this case the board is rebuilt:
  - Prevent player control.
  - Display all categories.
  - Play a sound effect (noise channel?).
  - Some time goes by.
  - Place a dollar value on the board **every 3rd frame** until the board is full.
  - The **active player with the least score** gains exclusive control.
    - Controller is shared with Player 1 & 3.

> **ROM correlation (well supported):** the board is a **6 × 5 grid (30 cells)** —
> the per-cell answered flags live at `$05D6,X` (X = 0–29). The six **categories**
> are chosen by the random-bag routine at `$82B1` (draw-without-replacement; see
> [`../../docs/randomizer.md`](../../docs/randomizer.md)). The "every 3rd frame"
> fill pacing rides the NMI frame counter `$01`. "Least score gains control" is the
> real-Jeopardy trailing-player-picks rule; per-seat scores are the digit array at
> `$25,X` (stride 5).
