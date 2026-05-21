# Unit 7 — Sound and Vision

> *"Five sound channels, 64 sprites, one shared screen — and a 1/60 s budget."*

## Learning objectives

1. Name the APU's five channels and how music (BGM) differs from sound effects
   (SFX).
2. Explain the sprite system: OAM, the 64/8-per-scanline limits, and metasprites.
3. Explain the background (nametable) and how it differs from sprites here.
4. See where graphics work is allowed — the vblank/NMI budget.

## Sound: the APU's five channels

The 2A03's APU has **five** voices, controlled by registers `$4000-$4013`, enabled
by `$4015`, with a frame sequencer at `$4017`:

| Channel | Registers | Typical use |
| --- | --- | --- |
| Pulse 1 | `$4000-$4003` | melody |
| Pulse 2 | `$4004-$4007` | harmony / counter-melody |
| Triangle | `$4008-$400B` | bass line |
| Noise | `$400C-$400F` | percussion, whooshes, buzzers |
| DMC | `$4010-$4013` | sampled audio (often unused) |

You saw these get **silenced then enabled** at boot (`STA $4000…$4017`, then
`LDA #$0F / STA $4015`).

**BGM vs SFX — the key distinction.** Both ultimately write the same APU registers,
but:

- **BGM (music)** is a *sequence*: a data "score" the sound engine steps through
  frame by frame, updating pitch/volume across several channels to play Themes 01,
  02, 03.
- **SFX** are *short, event-driven* sounds (board fill blip, buzz-in, countdown tick,
  confirm, out-of-time). An SFX often **steals a channel** from the music for its
  duration via a priority scheme, then hands it back. That's why a sound effect can
  briefly punch through the theme.

The sound engine's exact entry points are an **open trace** in this ROM — your lab
finds them by breakpointing the APU registers.

## Vision part 1: sprites (OAM)

A **sprite** here is a hardware object, not a generic image (see the glossary). Rules
worth memorizing:

- **64 sprites** max on screen; each is **4 bytes**: Y, tile, attributes, X.
- **8 sprites per scanline** max — exceed it and sprites drop/flicker.
- The CPU writes a **shadow copy** of all 64 in RAM at **`$0200-$02FF`**, then the
  NMI **DMA-copies** it to the PPU in one shot: `LDA #$02 / STA $4014`.
- A visible character bigger than 8×8 (a contestant) is a **metasprite** — several
  hardware sprites positioned together.

`ClearOAM $9203` parks unused sprites offscreen by writing **`$F8`** to their Y
bytes — the standard "hide it" trick.

## Vision part 2: the background (nametable)

The board grid, category text, and scores are **background**, not sprites. The
background is a **nametable**: a grid of tile indices the PPU reads to paint the
screen, plus an attribute table for color. Because this cart has **no CHR-ROM**, the
tiles themselves are **CHR-RAM**, uploaded from PRG at boot.

*Jeopardy* uses **single-screen mirroring** (Unit 8 / mapper doc): there's one
nametable visible at a time, and the engine flips between page **A** and **B**
(`$8000` bit 4) when it needs to repaint — the NMI forces page A each frame.

## The 1/60-second budget

You can only safely write the PPU during **vertical blank** — the ~2,273 CPU cycles
between frames when the PPU isn't drawing. That's why all the heavy PPU work lives
in the **NMI** (`$92BE`): OAM DMA, the palette flush (`$44-$63` → `$3F00`), and any
queued tile updates. Overrun the budget and you get visible glitches on the next
frame. The main thread *prepares* data; the NMI *commits* it. (This is the "parallel"
illusion from the glossary — two jobs interleaved on one core.)

## FCEUX Lab

1. **Find the sound engine.** Add **Write** breakpoints on `4002` and `4003` (Pulse
   1 pitch). Let a theme play → you break in the music routine. Trace a few frames to
   see it step a sequence. Then trigger an SFX (buzz in) and watch a channel get
   commandeered.
2. **See the sprites.** Open `Debug → PPU Viewer` (tiles + palettes) and the **Name
   Table Viewer**. Watch the contestant metasprites move while the board sits in the
   background. Open the Hex Editor on `$0200` and watch the OAM shadow update.
3. **Watch the DMA.** Breakpoint the `STA $4014` in the NMI; each hit is one frame's
   sprite upload.
4. **Catch the mirroring flip.** Write breakpoint on `$8000`; during a board repaint
   you'll see `#$10` (page B) and the NMI's `#$00` (page A) — single-screen mirroring
   in action.

## What to watch for

- A **music sequence** stepping each frame vs a **one-shot SFX** stealing a channel.
- The **`$F8` offscreen-Y** trick for unused sprites.
- **Background = nametable**, characters = **metasprites** — different systems.
- All PPU writes happening **inside the NMI** (the vblank budget).

## Key takeaways

- The APU has **five channels**; **BGM is a stepped sequence**, **SFX are
  channel-stealing one-shots**.
- Sprites are **OAM objects** (64 / 8-per-line), shadowed at `$0200`, DMA'd each
  frame; big characters are **metasprites**.
- The **background** is a CHR-RAM nametable with single-screen mirroring; PPU work is
  confined to the **NMI's vblank budget**.

Next: [Unit 8 — Game Loops & Reset Behavior](../Unit%2008%20-%20Game%20Loops%20and%20Reset%20Behavior/lesson.md).
