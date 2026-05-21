# Unit 12 — The Ultimate Cartridge (Capstone)

> *"Any one hack is a patch. All of them together is a **build** — and builds have
> dependencies."*

## Learning objectives

1. Combine the romhack ideas into **one coherent cartridge** without them fighting.
2. Order the work by **dependency**, and resolve the **conflicts** between features.
3. Produce a real **spec + test matrix** — the capstone deliverable.

This unit uses everything: the mapper (U1), input (U2), RAM (U3), RNG/bag (U4),
text/scoring (U5), Daily Double (U6), sound/sprites (U7), loops/reset (U8), bugs
(U9), the family (U10), and your change/keep judgment (U11).

## The keystone: capacity unlocks the rest

Look at the wish list ([`../ux/ROMHACK-IDEAS.md`](../../ux/ROMHACK-IDEAS.md)) and one
thing dominates the dependency graph: **most ambitious features want more ROM**, and
AOROM's per-bank trampoline tax + 128 KB ceiling fight you (U1). So the **keystone**
is a **mapper upgrade** — the deferred **MMC1** migration in
[`../../jeopardy-nescard-ips/MMC1_MIGRATION_PRECEDENT.md`](../../../jeopardy-nescard-ips/MMC1_MIGRATION_PRECEDENT.md).

MMC1 gives a **fixed bank** — the community's *core* (recall the glossary; AOROM has
none). That single change:

- **removes the duplicated trampolines** (one copy in the fixed bank),
- **frees ~450-525 B** of bank-tail glue, and
- **adds 16 KB-granular switchable banks** for new content.

Do this first and everything downstream gets cheaper.

## A dependency-ordered build

```
        ┌─────────────────────────────┐
   1.   │ MMC1 mapper upgrade (core)   │  ← keystone: fixed bank, capacity
        └──────────────┬──────────────┘
            ┌──────────┼───────────────┬───────────────┐
   2.  more clues   3. seeded RNG   4. tunable + wrong  5. QoL: faster
       (expansion)     (improve)       -answer CPU AI      fills / skip
            │             │            (mechanical)        lockout (qol)
            └─────────────┴──────┬─────┴───────────────────┘
   6.                    Rebrand / art pass (art change)
   7.                    Test matrix + verify (every step)
```

- **Stage 1 — Mapper (keystone).** Header rewrite, replace AOROM latches with MMC1
  register writes, consolidate the trampolines into the fixed bank, re-pack the clue
  blobs to 16 KB granularity. High risk, silent bugs — lean on FCEUX trace logging.
- **Stage 2 — Clues (expansion).** With capacity unlocked, add episodes/packs.
- **Stage 3 — Seeded RNG (improvement).** See the conflict below.
- **Stage 4 — CPU AI (mechanical).** Wire Skill Level to the `$A80D` index (U11) and
  add a post-buzz correctness roll (U6/U9). Additive; low risk.
- **Stage 5 — QoL (quality of life).** Faster board fill, optional lockout skip,
  instant Start (U1/U2/U4 anchors). Small, low risk.
- **Stage 6 — Art (art change).** Title rebrand / logo (U7, QZR notes). Cosmetic;
  last so it doesn't churn during engine work.

## Resolving the conflicts

- **Seeded RNG vs timing RNG (U4 vs U9).** They appear to clash. **Resolution:** make
  the seed *optional* — "if the player enters a seed, load it into `$02/$03/$FE` and
  bypass the idle churn; otherwise keep timing entropy." Both behaviors coexist; you
  gain shareable boards **and** the classic feel.
- **QoL speedups vs game feel (U11).** Make them **options**, not defaults, so you
  don't erase the original character.
- **Wrong-answer AI vs "buzz ⇒ correct" assumptions (U6).** Adding a correctness roll
  means the **disappointed-CPU path** must exist — confirm that animation/score path
  is reachable for CPUs, or add it. This is the one mechanical change with real reach
  into other systems.
- **Mapper change vs existing patches (U8).** A mapper-converted ROM is a **new
  base**; distribute as "converted base + content patch," not as an IPS over stock.

## The test matrix (run after every stage)

From the migration precedent, the minimum runtime verification:

| Check | Pass condition |
| --- | --- |
| Cold boot & soft reset | reaches title; RAM behaves per U8 |
| Every screen 00-08 | each scene renders and transitions |
| Clue display (all 4 blobs) | text decodes & renders from every bank |
| Daily Double (1 and 2) | placement, both wager formats |
| Final Jeopardy | per-player private wager + answer + results |
| Scoring | add/subtract correct at digit limits (U9) |
| `verify.py` (if byte-exact goal) | hash discipline on unchanged regions |

Two emulators (Mesen + FCEUX) catch mapper-timing divergence (U1/U8).

## Capstone deliverable

Write **`ULTIMATE-CART.md`** (a spec, not code) containing:

1. The **feature list**, each line tagged (`expansion` / `improvement` /
   `mechanical change` / `quality of life` / `art change`).
2. The **dependency graph** (why the mapper is first).
3. The **conflict resolutions** (seed-optional RNG, options-not-defaults QoL, the
   wrong-answer path).
4. The **test matrix** above, with a column for "verified in Mesen / FCEUX."
5. A **risk register**: which stage is most likely to introduce silent bugs and how
   you'll catch them (trace logs, savestate regression, the CDL).

That document *is* the graduation: it proves you can read the machine (U1-8), find
its edges (U9), see it in its family (U10), judge its design (U11), and **plan a
real build** that respects all of it.

## What to watch for

- A feature that **silently depends on capacity** → it belongs after the mapper.
- Two features that **touch the same RAM/UI** → sequence them, don't parallelize.
- Defaults that **erase the original feel** → make them options.

## Key takeaways

- The **mapper upgrade is the keystone**; capacity unlocks the ambitious features.
- Order by **dependency**, resolve **conflicts** explicitly (seed-optional RNG is the
  model), and make character-changing features **opt-in**.
- A combined hack is a **build with a spec and a test matrix** — produce
  `ULTIMATE-CART.md` and you've completed the course.

You've finished. Loop back to [the course README](../README.md) or open the
[disassembly docs](../../docs/) and start closing the roadmap's open questions.
