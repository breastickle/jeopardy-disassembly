# Quiz — Unit 5

1. Why are the clues stored Huffman-compressed instead of as plain text?
2. In one or two sentences, how does a Huffman decoder turn a bit stream into
   characters?
3. Why can't you just read the clue text in a ROM hex editor?
4. The clue blobs live in banks 1-3. What engine feature must the decoder use to
   reach them, and which unit covered it?
5. Name the game's two text systems and one thing that distinguishes them.
6. What does `$FD20` do, and what RAM buffer does it render from?
7. What is table `$B6BC` used for in the buffered text path?
8. The 2A03 lacks working decimal mode. What does that mean for how scores are
   added?
9. Where are per-seat scores stored, and what does the stride of 5 suggest?
10. Which two things in this unit are **not yet reverse-engineered** (good
    open-question targets)?

<details>
<summary>Answer key & scoring</summary>

1. The text (~110 KB) **wouldn't fit** alongside engine/graphics/sound in 128 KB
   uncompressed. *(§ "Why compress at all")*
2. Read bits one at a time, walking a **binary tree** left/right; at a **leaf**, emit
   that character and return to the root. *(§ same)*
3. Codes are **variable-length with no byte boundaries**, so the bytes don't map to
   characters until decoded. *(§ same)*
4. The **far-call trampoline (`$FF80`)** / bank switching — **Unit 1** (and the
   mapper doc). *(§ "Why compress" note)*
5. **Immediate UI strings (`$921E`, `char − $2C`)** vs **buffered dynamic text
   (`$FD20` from `$0534` via `$B6BC`)**; the first carries its own PPU address, the
   second renders a RAM buffer. *(§ "Two text systems")*
6. It **renders the RAM text buffer at `$0534`** to the PPU, translating bytes and
   honoring control codes. *(§ same)*
7. It's the **byte→tile translation table** for the buffered text. *(§ same)*
8. Scores are added with **manual multi-digit carry** (or binary then converted) —
   no hardware BCD `SED`. *(§ "Scoring without decimal mode")*
9. **`$25,X`**; stride 5 suggests **up to 5 decimal digits per seat**. *(§ same)*
10. The **answer-judging routine** and the **exact Huffman decoder loop / score
    math** — both are open traces. *(§ "Judging" / "Scoring" / takeaways)*

**Scoring:** 8-10 → Unit 6. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
