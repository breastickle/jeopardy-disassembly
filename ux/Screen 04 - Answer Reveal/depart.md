# Screen 04 — Answer Reveal · Depart

**This screen is departed when:**

- Any **non-locked-out** player rings in, **or**
- Some number of frames after the Answer Reveal timer reaches zero.
  - An "out of time" sound effect is played.

> **ROM correlation:** the per-frame buzz poll at `$9733` ticks the CPU timers
> (`$8F`, `$90`) on alternate frames and lets the first to reach zero ring in;
> human buzzes are read from the controllers. "Non-locked-out" maps to the
> per-seat buzz/lockout flags (`$AE,X`, `$85,X`). The timeout path is gated by the
> frame counter `$01`. See [`../../docs/npc-ai.md`](../../docs/npc-ai.md).
