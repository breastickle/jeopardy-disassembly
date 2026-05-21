# Unit 11 — If We Built It Today

> *"Maturity is knowing which 'flaws' are actually the right call."*

## Learning objectives

1. Separate decisions that are **dated by 1989 constraints** from decisions that are
   **timelessly good**.
2. Justify each "change" with the constraint that no longer applies, and each "keep"
   with why it still holds.
3. Turn that judgment into concrete, tagged proposals.

## The discipline: constraint, not taste

A junior reverse-engineer says "this is bad, I'd do X." A senior one asks: *what
constraint made this the right call in 1989, and does that constraint still exist?*
If the constraint is gone (ROM size, no tooling, a CRT audience), it's a fair
**change**. If the design is good **regardless** of era, it's a **keep**. Tag every
proposal so it's actionable ([`../ux/ROMHACK-IDEAS.md`](../../ux/ROMHACK-IDEAS.md)).

## What's actually perfect (keep)

- **AOROM for a static board.** A quiz board never scrolls; single-screen mirroring
  and coarse 32 KB banks are *exactly enough*. Paying for MMC3 here would be
  over-engineering. **Keep** — unless you need capacity (Unit 12).
- **Parallel-array RAM.** Column-wise per-seat data is cache-irrelevant on a 6502 and
  makes "do X to every player" a tight indexed loop. Still how you'd lay it out.
  **Keep.**
- **The frame counter as the clock.** One `INC $01` driving every timer is elegant
  and debuggable. **Keep.**
- **Faithful Daily Double rules** (1 then 2, random cells). Correct *and* cheap.
  **Keep.**
- **Private per-player Final Jeopardy.** Genuinely thoughtful couch-multiplayer
  design that holds up today. **Keep.**

## What we'd change (and the dead constraint)

| Change | The 1989 constraint… | …that's gone now |
| --- | --- | --- |
| **Seeded / shareable boards** | a seed UI costs ROM; players didn't expect one | trivial ROM today; online sharing/competition is the norm |
| **CPU can be wrong** (add a correctness roll) | a second AI system costs ROM + animation work | space and tooling are cheap; "buzz ⇒ correct" feels off to modern players |
| **Skill level that actually bites** | tight ROM, simple tuning | a few bytes wire skill into the reaction table `$A80D` |
| **More clue capacity** | 128 KB AOROM ceiling | bigger ROMs / a mapper change unlock far more clues |
| **QoL: faster fills, skip lockout** | matched TV pacing / CRT feel | modern players (and speedrunners) value snappiness |
| **Accessibility / save** | no battery, simple UI | flash saves and options menus are expected |

Notice the column on the right is always *"a constraint that no longer binds."* That
is the whole method.

## The trap: changing what was right

Resist "modernizing" the things that are fine:

- Don't bolt on a heavyweight RNG if you keep the party-game feel — *unless* you also
  want determinism (then it's a deliberate trade, Unit 12).
- Don't replace single-screen mirroring with scrolling for a board that doesn't move.
- Don't add a deep strategy AI to a game whose charm is three quick contestants.

A change that erases the game's character isn't an improvement; it's a different
game.

## Exercise (no FCEUX needed)

For each of the six "change" rows: write one sentence naming the **dead
constraint**, and one sentence on the **risk** of the change (what it might break or
cost). Then pick the **two** you'd actually ship and say why. File the survivors as
tagged entries in `ROMHACK-IDEAS.md`.

## What to watch for (in your own judgment)

- Are you changing it because the **constraint died**, or because of **taste**?
- Does the change **preserve the game's character** or replace it?
- Can you state the change as a **testable** spec (Unit 9's rigor)?

## Key takeaways

- Judge old design by its **constraints**, not modern habits.
- *Jeopardy* got a lot **right** (AOROM fit, parallel arrays, frame clock, faithful
  rules, private Final) — those are **keeps**.
- The honest **changes** are the ones whose 1989 constraint no longer binds —
  capacity, determinism, fairer/tunable AI, QoL — and each must preserve the game's
  character.

Next: [Unit 12 — The Ultimate Cartridge](../Unit%2012%20-%20The%20Ultimate%20Cartridge/lesson.md).
