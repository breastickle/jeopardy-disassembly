# Quiz — Unit 7

1. List the five APU channels and a typical use for each.
2. Which register **enables** the channels, and where did boot write it?
3. In your own words, how does BGM differ from SFX in how it's produced?
4. What does it mean that an SFX "steals a channel"?
5. How many bytes is one hardware sprite, and what are its four fields?
6. State the two hard sprite limits (total and per-scanline).
7. Where is the OAM shadow in RAM, and how does it reach the PPU each frame?
8. Why is `$F8` written to unused sprites' Y position?
9. Is the board grid a sprite or background? Why does the answer matter for CHR-RAM?
10. Why must PPU updates happen inside the NMI?

<details>
<summary>Answer key & scoring</summary>

1. **Pulse 1** (melody), **Pulse 2** (harmony), **Triangle** (bass), **Noise**
   (percussion/buzzers), **DMC** (samples). *(§ "Sound")*
2. **`$4015`**; boot wrote `#$0F`. *(§ same / Unit 1)*
3. BGM is a **sequence stepped frame-by-frame** across channels; SFX are **short,
   event-driven** sounds. *(§ "BGM vs SFX")*
4. The SFX **takes over a channel** the music was using (by priority) for its
   duration, then returns it. *(§ same)*
5. **4 bytes**: Y, tile, attributes, X. *(§ "sprites")*
6. **64 total**, **8 per scanline**. *(§ same)*
7. Shadow at **`$0200-$02FF`**, copied via **OAM DMA** (`STA $4014` with `#$02`) in
   the NMI. *(§ same)*
8. It **parks the sprite offscreen** (hides it). *(§ same)*
9. **Background (nametable)**; tiles come from **CHR-RAM** uploaded at boot (no
   CHR-ROM). *(§ "the background")*
10. PPU writes are only safe during **vblank**, which is when the NMI fires.
    *(§ "The 1/60-second budget")*

**Scoring:** 8-10 → Unit 8. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
