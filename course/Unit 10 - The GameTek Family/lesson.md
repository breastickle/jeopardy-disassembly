# Unit 10 — The GameTek Family

> *"You didn't just learn one game. You learned a house style."*

## Learning objectives

1. Recognize the shared engine DNA across GameTek's NES game-show titles.
2. Use your *Jeopardy* knowledge to **predict** how a sibling (esp. **Wheel of
   Fortune**) works before disassembling it.
3. Run a quick "is this the same engine?" probe on another cartridge.

## The house style

GameTek shipped a string of TV-game-show adaptations on the NES (Jeopardy and its
editions, **Wheel of Fortune** and its editions, and others), several built by the
same hands (Rare's AOROM lineage shows up across this era — Battletoads, R.C. Pro-Am,
…). When studios reuse people and tools, they reuse **patterns**. You've now read the
patterns; they transfer:

| Pattern you learned in *Jeopardy* | What to expect in a sibling |
| --- | --- |
| **Timing-seeded RNG** that free-runs in an idle spin (Unit 4) | a small RNG churned while waiting; sampled on input. Wheel's wheel-spin "randomness" is a prime suspect. |
| **Random bag** drawing without replacement (Unit 4) | puzzle/category/prize selection by the same draw-and-mark trick |
| **Reaction-time table** AI; `$FF` = "doesn't know" (NPC doc) | CPU opponents as a **table of delays/odds**, not a thinking AI |
| **Scene/script state** `$6E` → jump table (Unit 3) | a single state variable dispatched through a pointer table |
| **`char − const` text codec** + a buffered renderer (Unit 5) | a simple tile-offset text system for UI; compressed data for the bulk |
| **AOROM + per-bank trampoline** (Unit 1) | coarse 32 KB banking, duplicated bank-tail glue, CHR-RAM |
| **Parallel-array** per-player RAM (Unit 3) | one array per field, indexed by player |
| **Podium / Press-Start** presentation flow (UX roadmap) | the same boot → menu → setup → play → results spine |

## Predicting Wheel of Fortune

Before opening it, write down predictions — that's the scientific way to confirm a
shared engine:

- **The wheel spin** is almost certainly the *Jeopardy* RNG idiom: a value churned
  every frame while the wheel graphic spins, **sampled when you press to stop**. Look
  for an idle loop calling a small generator, and a result reduced by `AND mask` or
  modulo (like `$830C`).
- **Letter picking by the CPU** should be a **table-driven** decision (frequency
  weights / a reaction-style table), not language modeling — the same "limited AI"
  philosophy as the buzz table.
- **Puzzle text** likely uses a simple codec for the board letters and a
  compressed/encoded store for the puzzle bank.
- **Money/scoring** in **parallel arrays**; **state** in a single `$6E`-like
  dispatcher.
- **Mapper**: a good chance of AOROM/CHR-RAM, with the same trampoline tax.

Then disassemble and check. Where it **matches**, you've confirmed the house style;
where it **differs**, you've found something genuinely interesting about that title.

## FCEUX Lab (bring your own legal Wheel of Fortune dump)

1. **Fingerprint the cart.** Note the mapper FCEUX reports. Adapt `../tools/verify.py`
   (swap the hashes) to recognize your specific dump.
2. **Hunt the RNG.** Find an idle screen; in the Debugger watch for a zero-page byte
   that **changes every frame while nothing happens** — the same tell as `$02` in
   *Jeopardy*. Breakpoint its writer; is it a stir-the-pot accumulator?
3. **Hunt the AI table.** When a CPU contestant acts, look for a **table read**
   indexed by difficulty/skill — the analog of `$A80D`. `$FF`-like sentinels are a
   strong signal.
4. **Hunt the state machine.** Find the byte that changes once per screen (the `$6E`
   analog) and the **jump table** it indexes.
5. **Diff the philosophy.** Write a short note: which patterns matched, which didn't.

## What to watch for

- A zero-page byte **never settling** on an idle/spin screen → the RNG.
- A **table read indexed by skill/value** → the opponent "AI."
- A **single state byte → pointer table** → the scene dispatcher.
- **Bank-tail glue duplicated** across banks → AOROM trampoline.

## Key takeaways

- GameTek's game-show NES titles share a **house style**; *Jeopardy* taught you its
  vocabulary.
- You can **predict** a sibling's internals (Wheel's spin, CPU letter choice, text,
  banking) before reading a byte — then confirm by disassembly.
- The transferable skill is **pattern recognition across a developer's catalog** —
  exactly how real reverse-engineers move fast on a new ROM.

Next: [Unit 11 — If We Built It Today](../Unit%2011%20-%20If%20We%20Built%20It%20Today/lesson.md).
