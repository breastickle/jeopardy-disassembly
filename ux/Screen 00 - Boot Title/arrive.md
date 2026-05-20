# Screen 00 — Boot Title · Arrive

**This screen is shown:**

- Immediately upon **boot**.
- Immediately upon **reset**.
- After completing the Final Jeopardy segment with final results, returning from
  **Screen 05 — Player Podium**.

This screen has an intro theme designated **Theme 01**.

> **ROM correlation:** `RESET` (`$FF94`, identical in all four AOROM banks) latches
> bank 0 and jumps to cold boot at `$8021`, which warms up the PPU, silences the
> APU, uploads graphics via cross-bank calls, and falls into the main loop
> (`JMP $925A`). From here on the NMI increments the frame counter `$01` every
> vblank — the clock the timed departure below runs on. See [`../../docs/mapper.md`](../../docs/mapper.md).
