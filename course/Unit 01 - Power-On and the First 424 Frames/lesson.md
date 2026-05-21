# Unit 1 — Power-On and the First 424 Frames

> *"What is a computer, and which one are we even talking about?"*

## Learning objectives

By the end you can:

1. Name the chips in an NES and say what each does.
2. Explain what happens at power-on / reset and why the CPU starts where it does.
3. Read the cold-boot routine and explain the PPU "warm-up" wait.
4. Describe the frame counter and how the title screen auto-advances after ~424
   frames with no input.

## The machine in one page

The NES is three chips and a cartridge:

- **CPU — Ricoh 2A03.** A **6502 core** (8-bit, ~1.79 MHz NTSC) with two twists:
  its **decimal mode is disabled** (binary-only `ADC`/`SBC`), and it has an
  **integrated APU** (sound) plus a **DMA** unit. This is the chip our disassembly
  is written for.
- **PPU — 2C02.** The Picture Processing Unit draws the screen on its own: a
  tile-based **background** (the *nametable*) and up to 64 **sprites**. It has its
  own memory and its own palette at `$3F00`. The CPU talks to it only through a
  handful of registers (`$2000-$2007`).
- **RAM — 2 KB.** The CPU's work memory, `$0000-$07FF`. That's *all* the
  general-purpose RAM the program gets.
- **The cartridge.** Holds **PRG-ROM** (program) and graphics. *Jeopardy* has
  **128 KB PRG** and **no CHR-ROM** — instead it has **8 KB CHR-RAM** that the
  program fills with tiles at runtime. A chip on the cart, the **mapper**
  (here **AOROM**), decides which 32 KB slice of PRG is visible at `$8000-$FFFF`.

> See [`../GLOSSARY.md`](../../GLOSSARY.md) — "core" here means the resident
> engine, **not** a CPU-core count; there is exactly one core.

## What happens when you flip the switch

A 6502 doesn't "start at the beginning." On power-on **and** on the Reset button,
it reads a fixed 16-bit address — the **RESET vector** at `$FFFC/$FFFD` — and jumps
there. In *Jeopardy* that vector is **`$FF94`** (the same in all four banks, because
AOROM swaps the whole window — Unit 8 revisits this).

`RESET` does almost nothing itself:

```asm
FF94  SEI              ; ignore IRQs for now
FF95  LDA #$08
FF97  STA $8000        ; AOROM latch: map bank 0
FF9A  JMP $8021        ; -> the real cold boot
```

## Cold boot — `$8021`

This is the "bring the machine to a known state" routine. The shape is the same in
almost every NES game:

```asm
8021  LDA #$00 / STA $AD     ; clear a state byte
8025  SEI / CLD              ; no IRQs; clear decimal (habit — 2A03 ignores it)
8027  LDX #$FF / TXS         ; set the stack pointer to the top of $01xx
802A  LDA #$00 / STA PPUCTRL ; (after #$10) NMI off
802F  LDA #$00 / STA PPUMASK ; rendering off
8034  LDA PPUSTATUS / BPL    ; wait for vblank  ┐ PPU "warm-up":
8039  LDA PPUSTATUS / BPL    ; wait for vblank  ┘ poll $2002 twice
803E  ... STA $4000..$4017   ; silence the APU
8054  LDA #$0F / STA $4015   ; enable the 4 main sound channels
8057  JSR ... ; clear OAM, upload graphics via cross-bank calls
...   STA $AA               ; arm the NMI
80CD  JMP $925A             ; into the main loop
```

**Why poll `$2002` twice?** The PPU needs about **one to two frames** after power
before it's stable. Bit 7 of `$2002` (PPUSTATUS) is the vblank flag. Each
`LDA $2002 / BPL` loop waits for one vblank; doing it twice guarantees the PPU is
warmed up before the game writes to it. Skip this and you get garbage or a
hardware-dependent boot. This is a piece of NES *folklore made code*.

## The heartbeat: the frame counter

Once the cold boot arms the **NMI** (Non-Maskable Interrupt), the PPU pulls it
**~60 times per second**, once per vertical blank. The bank-0 NMI handler lives at
`$92BE`; the very last thing it does before returning is:

```asm
938B  INC $01          ; <-- frame counter, +1 every frame
938D  JMP ($0005)      ; resume the main thread
```

So **`$01` counts frames**. Almost every timed thing in the game — the title's
auto-advance, countdown timers, animation beats — is "wait until `$01` reaches N."

Your UX notes say the title (Screen 00) departs at about **frame 424**, going black,
and reaches the Main Menu by frame **439**, with **no input required**. That's a
timed transition: somewhere a comparison against the frame count flips the scene
variable. Finding that comparison is your lab.

## FCEUX Lab

1. **Catch the boot.** Open the ROM. `Debug → Debugger`. Add an **Execute**
   breakpoint at `8021`. Press the NES **Reset**. You'll stop at cold boot.
2. **Single-step** with *Step Into*. Watch `SEI`, `CLD`, `LDX #$FF / TXS`, then the
   two `LDA $2002 / BPL` warm-up loops, then the `STA $4015` that turns sound on.
3. **Watch the heartbeat.** Add `$01` to **RAM Watch**. Run, then `Emulation →
   Pause`. Use **Frame Advance** (`\`) and confirm `$01` goes up by exactly one each
   press.
4. **Find the title timeout.** Add `$6E` (the scene variable) to RAM Watch. Reset,
   let the title play, and watch `$6E` change as it flips to the menu (~frame 439).
   Bonus: set a **Write** breakpoint on `$6E` to catch the instruction that advances
   the scene, and look at what it compared against.

## What to watch for

- The **two `$2002` polls** — that's the warm-up wait, not a mistake.
- `STA $4015` with `#$0F` — sound channels coming online.
- `$01` ticking once per frame; `$AA` (NMI-enable flag) becoming non-zero.
- `$6E` changing exactly once at the title→menu transition.

## Key takeaways

- The 6502 boots through the **RESET vector**; the game's `$8021` brings the PPU,
  APU, and stack to a known state.
- The **PPU warm-up wait** (two `$2002` reads) is mandatory NES boot hygiene.
- **`$01` is the frame clock**; "wait N frames" is the engine's main timing idiom,
  including the unattended title→menu hop.

Next: [Unit 2 — The Controller & Pressing Start](../Unit%2002%20-%20The%20Controller%20and%20Pressing%20Start/lesson.md).
Related docs: [`../docs/mapper.md`](../../docs/mapper.md), [`../docs/ram-map.md`](../../docs/ram-map.md).
