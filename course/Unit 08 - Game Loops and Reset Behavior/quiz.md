# Quiz — Unit 8

1. There's no classic `while(true)` loop. Describe how the main thread and the NMI
   together form "the game loop."
2. What two zero-page locations coordinate the hand-off between main thread and NMI?
3. Name five pieces of RAM that together define "a game in progress."
4. Why is there no "continue" feature?
5. True/False: pressing Reset runs a different boot routine than power-on.
6. Does the boot routine clear all 2 KB of RAM? What *does* it clear?
7. Explain, accurately, why RAM "survives" a soft reset.
8. Why does a cold power-on effectively start fresh even though hardware doesn't
   wipe RAM either?
9. What would a **warm-boot signature check** look like in code, and do we expect to
   find one here?
10. In FCEUX, how do you demonstrate the soft-reset-vs-power-on RAM difference?

<details>
<summary>Answer key & scoring</summary>

1. The **main thread** dispatches the current `$6E` scene then **idles in the spin**
   at `$93A3`; the **NMI** fires each vblank, commits graphics, bumps `$01`, and
   **resumes** the main thread via `JMP ($0005)`. *(§ "cooperative state machine")*
2. The **resume pointer `$05/$06`** and the **NMI flag `$AA`**. *(§ same)*
3. Any five of: scores `$25,X`, names `$05AF`, mode `$05B4`, round `$03D2`,
   contestant `$70`, board `$063C`, cell flags `$05D6`, DD cells `$9F/$A0`, RNG
   `$02/$03`. *(§ "What a game is")*
4. **No battery/save** — all state is RAM, lost at power-off. *(§ same)*
5. **False** — both run the same `RESET` → `$8021`. *(§ "The reset myth")*
6. **No.** It clears only `$AD`, `$AA`, **OAM** (to `$F8`), and `$0300` — not
   `$0000-$07FF`. *(§ same)*
7. SRAM **physically keeps its bits** through a reset pulse, and the boot **doesn't
   wipe** it — so old values linger until per-screen init overwrites them.
   *(§ same)*
8. Cold RAM is **indeterminate garbage/fill**, different each power-up, so there's
   nothing meaningful retained. *(§ same)*
9. A `LDA $xxxx / CMP #magic / BEQ` that trusts old RAM only if a signature survives;
   we **expect none** — the game re-inits per state. *(§ same)*
10. **Reset** keeps current RAM (note bytes survive); **Power** re-applies FCEUX's
    fill pattern (old values gone). *(§ "FCEUX Lab")*

**Scoring:** 8-10 → Unit 9. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
