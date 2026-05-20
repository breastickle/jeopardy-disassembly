# Screen 00 — Boot Title · Depart

This screen always departs at about **frame 424**:

- **Frame 424** — black screen.
- **Frame 439** — proceeds to **Screen 01 — Main Menu**.

This is a fixed, unattended timeout — no player input is required to leave.

> **ROM correlation:** a timed auto-advance keyed off the NMI frame counter `$01`
> (the same counter the contestant intro choreography keys off — `LDA $01 / CMP #$nn`
> checkpoints, e.g. `$8F23`). Pinning the exact compare value that fires the
> Screen 00 → Screen 01 transition is a good first tracing exercise.
