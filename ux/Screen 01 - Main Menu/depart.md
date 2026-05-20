# Screen 01 — Main Menu · Depart

**This screen will not depart until:**

- The game is reset, **or**
- **Player 1 presses Start** after the screen has been displayed for some number
  of frames.
  - Player input is **ignored** until that many frames have elapsed.
  - If the player inputs on the first possible frame, the screen goes black by
    **frame 607** total from boot.

> **ROM correlation:** a "press Start" wait — the main loop polls controller 1
> (`JOY1 $4016`) and only acts once a frame-counter (`$01`) gate has opened, which
> is the input-lockout you observed. This is one of two scenes with a Press Start
> prompt; the other is **Screen 08 — Final Jeopardy**.
