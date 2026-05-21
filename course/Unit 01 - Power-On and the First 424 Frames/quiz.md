# Quiz — Unit 1

Ten questions. Answer before opening the key. Rubric at the bottom.

1. The NES CPU is a Ricoh 2A03. Name **two** ways it differs from a textbook 6502.
2. What address does the 6502 read on power-on/reset to learn where to start, and
   what value does *Jeopardy* put there?
3. Why does cold boot read `PPUSTATUS` (`$2002`) in a `BPL` loop **twice** before
   touching the PPU?
4. What does `SEI` do, and why is it the first real instruction at `$8021`?
5. `CLD` appears at boot even though the 2A03 ignores decimal mode. Why is it
   there anyway?
6. Which zero-page address is the **frame counter**, and which instruction (in
   which handler) increments it?
7. The title screen advances to the menu after ~424 frames **with no button
   press**. In one sentence, what mechanism does that?
8. What does `STA $4015` with `#$0F` accomplish during boot?
9. True/False: the NES has no general-purpose RAM beyond 2 KB.
10. In FCEUX, what breakpoint would you set to stop the emulator the instant the
    cold-boot routine begins?

<details>
<summary>Answer key & scoring</summary>

1. **Decimal mode disabled** (binary-only `ADC`/`SBC`) and an **integrated APU**
   (plus DMA). *(Lesson: "The machine in one page")*
2. The **RESET vector at `$FFFC/$FFFD`**; *Jeopardy* stores **`$FF94`** there.
   *(§ "What happens when you flip the switch")*
3. The PPU isn't stable until ~1-2 frames after power; each loop waits one vblank,
   so two loops guarantee warm-up. *(§ "Why poll `$2002` twice")*
4. `SEI` **sets the interrupt-disable flag** so IRQs can't fire during the fragile
   boot. *(§ "Cold boot")*
5. **Habit / portability** — it's standard 6502 boot hygiene; harmless here.
   *(§ "Cold boot")*
6. **`$01`**, incremented by **`INC $01` at `$938B` in the bank-0 NMI handler**.
   *(§ "The heartbeat")*
7. A **comparison against the frame counter `$01`** flips the scene variable `$6E`
   to the menu state. *(§ "The heartbeat")*
8. It **enables the four main APU channels** (turns sound on). *(§ "Cold boot")*
9. **True** — 2 KB at `$0000-$07FF` is all the CPU RAM. *(§ "The machine")*
10. An **Execute breakpoint at `8021`**. *(§ "FCEUX Lab")*

**Scoring:** 8-10 → Unit 2. 5-7 → re-read the flagged sections. 0-4 → redo the lab.
</details>
