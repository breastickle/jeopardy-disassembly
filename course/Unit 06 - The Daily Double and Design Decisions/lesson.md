# Unit 6 — The Daily Double and Design Decisions

> *"Now that you can read the code, you can start asking **why**."*

## Learning objectives

1. Read the Daily Double placement and the fork that diverts a clue to the wager
   screen.
2. Explain the two wager-entry formats and the condition that picks between them.
3. Practice forming and **testing** "why did GameTek build it this way?" hypotheses
   from code + UX evidence.

## Placing the Daily Double(s)

Real Jeopardy hides **one** Daily Double in the Jeopardy round and **two** in Double
Jeopardy. *Jeopardy* (NES) does exactly that, at random cells, in `$9A7F`/`$9A89`:

```asm
9A7F  LDA #$01 / LDX #$1D / STA $05D6,X / DEX / BPL   ; init 30 per-cell flags
9A89  JSR $9027                ; RNG
9A8C  LDA $02 / AND #$1F       ; 0..31
9A90  CMP #$1E / BCC + / EOR #$04   ; fold back into 0..29 (30 cells)
9A96  STA $9F                  ; first Daily Double cell
9A9C  LDA $03D2 / BEQ ...      ; if Double Jeopardy:
9AA1  ... second random cell, deduped against $9F
9AB3  STA $A0                  ; second Daily Double cell
```

So `$9F` (and `$A0` in Double Jeopardy, mode flag `$03D2`) hold the hidden cells,
chosen 0-29 over the 6×5 board with a **dedup** so the two never collide. When the
in-control player later selects a cell, the engine compares it against `$9F`/`$A0`;
a match diverts **Screen 03 → Screen 07** (the wager) instead of straight to the
clue. *(The compare site itself is Open Question #2 in the roadmap.)*

## Two ways to wager

Your Screen 07 notes record two formats:

- **Format 1 — score above the minimum:** a **numeric entry** (digits, backspace,
  end).
- **Format 2 — score below a threshold:** a **menu of prefab wagers (A-E)**.

The selector is a **score comparison**. That single `CMP` is a design decision with
a player-experience payoff — which is the real subject of this unit.

## Asking "why?" like an engineer

You can now read the machine; the next skill is reading the **intent**. A good
design-decision claim is a *hypothesis with evidence*, not a vibe. Use this loop:

1. **Observe** something specific in code or UX (e.g. "low scores get prefab
   wagers").
2. **Hypothesize** a reason ("typing a wager you can't afford is frustrating /
   error-prone; prefabs keep it legal and fast").
3. **Find the constraint** that made it cheap or necessary (RAM? ROM? the 1989
   audience? hardware limits? faithfulness to the TV show?).
4. **Look for the counter-evidence** (would a different choice have cost more bytes,
   more bugs, more confusion?).
5. **Mark confidence** — "confirmed by code," "plausible," or "speculation."

Worked examples for *Jeopardy*:

| Decision (observed) | Likely "why" | Confidence |
| --- | --- | --- |
| Prefab wagers for low scores | avoids illegal/frustrating entry; faster on a d-pad | plausible |
| **Buzz ⇒ always correct** for CPUs (Unit 7/AI doc) | one system instead of two; no wrong-answer AI/animation to write | strongly supported (no second roll exists) |
| 1 DD in round 1, 2 in round 2 | **faithful to the TV show**, ~free to implement | confirmed by code (`$03D2` gate) |
| Final Jeopardy answered **privately** per player | couch multiplayer without spoilers | supported by UX + per-player loop |
| Timing-seeded RNG, **no seed screen** (Unit 4) | entropy is free; a seed UI costs ROM and 1989 players didn't expect one | plausible |

The goal isn't to be right every time — it's to make claims you could **test**, and
to separate "the code proves it" from "I'd have done it that way."

## FCEUX Lab

1. **Find the hidden cells.** Add `$9F` and `$A0` to RAM Watch. Start a round; note
   the values (0-29). Cross-reference to a board position (cell = row×6 + column, or
   column×5 + row — work out the layout from where the DD actually appears).
2. **Catch the divert.** Set an Execute breakpoint where the selected cell is
   tested; select the DD cell and confirm the branch to Screen 07. (Finding that
   compare is the exercise.)
3. **Trip the format switch.** Tank a player's score low, trigger a Daily Double,
   and confirm you get the **prefab** wagers; with a high score, confirm **numeric**
   entry. Then hunt the `CMP` that decides — what threshold value?
4. **Write one design note.** Pick a decision, run the 5-step loop above, and add a
   tagged entry to [`../ux/ROMHACK-IDEAS.md`](../../ux/ROMHACK-IDEAS.md) if it
   suggests a hack.

## What to watch for

- `$9F`/`$A0` set **once per round**; `$03D2` gating the second one.
- The **dedup** branch (the second cell rerolls if it equals the first).
- A **score `CMP`** standing between the two wager UIs.

## Key takeaways

- Daily Doubles are **random board cells** (`$9F`/`$A0`), one or two by round mode,
  deduped — code that mirrors the TV rules.
- The wager UI **forks on score**, a small decision with a real UX reason.
- "Why" questions become rigorous when you tie them to **code evidence and the
  constraints of 1989 hardware**, and you mark your confidence.

Next: [Unit 7 — Sound & Vision](../Unit%2007%20-%20Sound%20and%20Vision/lesson.md).
