# Unit 5 — Huffman, Text, Answer Checking, Scoring

> *"110 KB of trivia in a 128 KB cart — something has to give."*

## Learning objectives

1. Explain why the clues are **Huffman-compressed** and how a bit-stream decoder
   works at a high level.
2. Distinguish the game's **two text systems** and read the renderers.
3. Reason about how a typed answer is **judged** and how scores are kept **without
   decimal mode**.

## Why compress at all

A season of *Jeopardy* is a *lot* of text. The cart is 128 KB, and after the engine,
graphics, and sound, the clues get whatever's left — roughly **110 KB across four
blobs / 29 blocks** in banks 1-3. Stored as raw bytes they wouldn't fit, so the text
is **Huffman-compressed**.

**Huffman in one paragraph:** frequent letters get **short** bit codes, rare ones get
**long** codes, and the codes form a binary tree. To decode, you read the bit
stream one bit at a time, walking left/right down the tree; when you reach a leaf,
you emit that character and jump back to the root. There are **no byte boundaries** —
a character can be 3 bits or 11 — which is exactly why you can't just read it in a
hex editor. *Jeopardy* uses **per-group trees** (about four per compile), with the
tree tables living near `$9D6A` / `$9DCC` in bank 0. Format details:
[`../../Jeopardy/SCRIPT_FORMAT_NOTES.md`](../../../Jeopardy/SCRIPT_FORMAT_NOTES.md).

> The bank arithmetic matters: the blobs are in banks 1-3, so the decoder runs
> through the **far-call trampoline** (Unit 1's `$FF80`) to reach them. Compression
> *and* banking are working together here.

## Two text systems (don't confuse them)

This game draws text two different ways:

1. **Immediate UI strings** — `DrawString $921E` and friends. The string record
   carries its **own destination PPU address** then characters, terminated by a set
   high bit. Mapping is `tile = char − $2C` (so comma `$2C` = blank). Used for menus,
   names, labels. See [`../../docs/text-format.md`](../../docs/text-format.md).
2. **Buffered dynamic text** — `$FD20`. It reads a **RAM buffer at `$0534`** and
   translates each byte through a table at **`$B6BC`** before writing to the PPU,
   honoring control codes (`$2B`, `$0D`, `$7E`):
   ```asm
   FD24  LDA $0534,Y / CMP #$0D / BEQ ...   ; control codes
         CMP #$7E / BEQ ... / CMP #$2B / BEQ ...
   FD33  TAX / LDA $B6BC,X / STA $2007      ; translate -> tile -> PPU
   ```
   This is the path the **decompressed clue** takes: Huffman → fill `$0534` → `$FD20`
   renders it. Connecting the decoder's output to this buffer is your lab.

## Judging a typed answer

When a human answers (Screen 06), the typed text must be compared to the stored
**reply**. The Jeopardy family uses a forgiving match with sentinel conventions
(`+`, `~`, lowercase wildcards) so "WASHINGTON" and "George Washington" can both
pass — the reply-symbology rules are shared across the sibling tools
(`REPLY_VALIDATION_LOGIC.md`). The **exact compare routine in this ROM is not yet
mapped** — it's one of the best Open-Question targets, and you have the tools to
find it (breakpoint the transition out of Screen 06 and trace).

## Scoring without decimal mode

The 2A03's **decimal mode is disabled**, so the game can't lean on BCD `ADC`. Scores
live as **per-seat digit arrays at `$25,X` (stride 5 → up to 5 digits)**. Adding a
clue value means **multi-digit add with manual carry** (add a column, if it exceeds
9 subtract 10 and carry into the next column) — or a binary store that's converted to
digits only for display. Either way, you'll see explicit compare-and-carry, not a
single `SED; ADC`.

## FCEUX Lab

1. **See the buffer fill, then render.** Execute breakpoint at `$FD20`. Reveal a
   clue. When you break, look at `$0534…` in the Hex Editor — it holds the decoded
   clue text (translated through `$B6BC`). Scroll the PPU **Name Table Viewer** to
   watch it land on screen.
2. **Catch the decoder.** Set a **Read** breakpoint on the tree region (around
   `$9D6A`) or step backward from the moment `$0534` gets written; you're looking
   for the bit-walk loop that fills the buffer.
3. **Find the judge.** Type an answer on Screen 06 and press End. Trace (Trace
   Logger) the path that decides right/wrong; watch which RAM holds your typed text
   and what it's compared against.
4. **Watch a score change.** Add `$25,X` (5 bytes) to RAM Watch. Answer correctly
   and watch the digits update — note whether you see decimal digits or a binary
   value, and whether carry propagates column to column.

## What to watch for

- Clue text that's **invisible in a ROM hex view** (it's a bit stream) but **plain**
  in `$0534` at runtime — the difference compression makes.
- The **two** text paths (immediate vs buffered) — don't mistake one for the other.
- **No `SED`** anywhere — scoring is manual decimal or binary, never hardware BCD.

## Key takeaways

- Clues are **Huffman bit streams** decoded with per-group trees; that's why they're
  unreadable statically and need the bank trampoline to reach.
- **`$FD20`** renders the decoded buffer `$0534` via table `$B6BC`; UI text uses the
  separate `char − $2C` path.
- **Answer judging** is an open trace; **scoring** is manual (no decimal mode) over
  the `$25,X` digit arrays.

Next: [Unit 6 — The Daily Double & Design Decisions](../Unit%2006%20-%20The%20Daily%20Double%20and%20Design%20Decisions/lesson.md).
