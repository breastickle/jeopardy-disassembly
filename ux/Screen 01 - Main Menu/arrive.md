# Screen 01 — Main Menu · Arrive

**This screen is shown:**

- After **Screen 00** clears the PPU and loads the graphics for Screen 01.

This screen has the title theme designated **Theme 02**.

> **ROM correlation:** the main loop dispatches the current scene through the
> game-state index `$6E` into the jump table at `$8901` (handler = `$8901 + $6E*2`).
> Screen 01 is one such state; identifying its `$6E` value and handler address is
> the anchor for everything this scene does. See [`../../docs/ram-map.md`](../../docs/ram-map.md).
