# Disassembling *Jeopardy!* (NES) — a self-paced course

A hands-on course that uses one small, friendly GameTek cartridge to teach **6502
assembly and NES internals** the way you actually learn them: by watching a real
game run, one frame at a time, in a debugger.

You will not just *read* about the engine — you'll set breakpoints on the routines
in [`../docs/`](../docs/), watch the random bag deal six categories, catch the CPU
opponents rolling their reaction times, and trace the bank-switch trampoline as it
fires. By the end you'll be able to open an unfamiliar NES ROM and find your way
around.

## Who this is for

You can write a little code and aren't afraid of hexadecimal. You do **not** need
prior assembly experience — Unit 1 starts at power-on. If a term trips you up,
check [`../GLOSSARY.md`](../GLOSSARY.md): many words (bank, core, script, vector,
sprite, parallel…) mean something *different* here than in modern programming, and
the glossary calls out each "false friend."

## What you need

| Thing | Why | Where |
| --- | --- | --- |
| The ROM (your own legal dump) | the subject | confirm with `python ../tools/verify.py your.nes` → must print `MATCH` |
| **FCEUX** (2.6+) | the lab bench (debugger, hex, PPU viewer) | fceux.com |
| Python 3 | run our disassembler | `../tools/disasm6502.py` |
| The docs | the answer key behind the labs | [`../docs/`](../docs/), [`../ux/ROADMAP.md`](../ux/ROADMAP.md) |

## How the course works

Twelve units, each a folder with:

- **`lesson.md`** — the concepts, grounded in *this* ROM, plus an **FCEUX Lab**
  (do-this-now steps) and a **What to watch for** list.
- **`quiz.md`** — 10 questions with a hidden answer key and a scoring rubric.

**Scoring rubric (every quiz):**

| Score | Verdict |
| --- | --- |
| **8-10** | You've got it — move to the next unit. |
| **5-7** | Re-read the sections flagged next to the answers you missed, then move on. |
| **0-4** | Redo the unit's lab; the concepts haven't landed yet. |

Work in order — each unit assumes the last. It's self-paced; there's no clock.

---

## FCEUX primer (read once, refer back often)

FCEUX is a NES emulator with a real debugger. Everything below is on the **Debug**
and **Tools** menus.

### Open and confirm
- **File → Open ROM** loads the game. (Verify the dump first with our `verify.py`.)
- The title says the mapper FCEUX detected — it should read **AOROM / mapper 7**.

### The Debugger — `Debug → Debugger…`
Your main tool. It shows live disassembly, the registers (A, X, Y, P, SP, PC), and
breakpoints.
- **Breakpoints:** click **Add**, type an address (e.g. `9027`), tick **Execute**
  (run when PC reaches it), **Read**, or **Write** (run when that address is
  read/written). You can give a **range** (e.g. `0200`-`02FF`). Write-breakpoints
  on RAM are how you discover *who* changes a variable.
- **Step Into / Over / Out**, **Run**, and **Seek PC** behave like any debugger.
- Tip: a Write breakpoint on `4016` (the controller latch) is how you'll solve a
  Unit 2 mystery.

### Hex Editor — `Tools → Hex Editor`
The **View** menu switches what you're looking at:
- **NES Memory** — the CPU map `$0000-$FFFF` (RAM `$0000-$07FF`, registers, and the
  currently-mapped ROM bank at `$8000-$FFFF`).
- **PPU Memory** — nametables and the palette at `$3F00`.
- **ROM File** — raw file offsets (this is what the `file 0x…` numbers in our docs
  mean). Right-click a byte to **freeze** it or jump to it in the debugger.

### Watches & search
- **RAM Watch** (`Tools → RAM Watch`) — add addresses to see their values update
  live. Load the **standing watch list** below before any lab.
- **RAM Search** — narrow down an unknown address by how its value changes
  ("I scored, which byte went up?").

### Seeing the machine think
- **Trace Logger** (`Debug → Trace Logger`) — records every instruction executed.
  Start it, do one action, stop it: you now have the exact code path.
- **Code/Data Logger / CDL** (`Debug → Code/Data Logger`) — as you play, marks each
  ROM byte as *code* or *data*. Run it through a whole game and you've separated the
  engine from the clue blobs — the runtime complement to our static `--trace`.
- **PPU Viewer** (`Debug → PPU Viewer`) — the pattern tables (tiles) and the 8
  palettes, live.
- **Name Table Viewer** (`Debug → Name Table Viewer`) — the background as the PPU
  sees it; watch single-screen mirroring flip between page A and B.

### Symbolic debugging (make the disassembly readable in FCEUX)
FCEUX reads **name-list** files next to the ROM: `yourrom.nes.0.nl`,
`yourrom.nes.1.nl`, … one per bank. Each line is `$ADDR#Name#Comment`. Porting our
[`../src/jeopardy.sym.json`](../src/jeopardy.sym.json) into `.nl` files makes the
debugger show `Rng_Advance` instead of `$9027`. (Building that converter is a
bonus exercise in Unit 4.)

### Pausing time
- **Emulation → Pause** (or the Pause key) freezes the game.
- **Frame Advance** (default key **`\`**) runs exactly one frame — essential when
  you're counting frames (Units 1, 2, 6).
- Turn on the on-screen frame counter via `Config → Display`.

> **Address note:** because AOROM swaps the whole `$8000-$FFFF` window, the
> debugger's disassembly at those addresses is *whatever bank is mapped right now*.
> Bank 0 (the engine) is mapped most of the time. For bytes in banks 1-3, use the
> Hex Editor's **ROM File** view with the `file 0x…` offsets from our docs.

---

## Standing watch list (add these in RAM Watch on day one)

These are the variables you'll meet again and again (full map:
[`../docs/ram-map.md`](../docs/ram-map.md)).

| Addr | What | First appears |
| --- | --- | --- |
| `$01` | frame counter (NMI `INC`) | Unit 1 |
| `$02` `$03` | RNG state / output | Unit 4 |
| `$6E` | **scene / script state** (→ jump table `$8901`) | Unit 3 |
| `$70` | current contestant (0-2) | Unit 3 |
| `$8F` `$90` | CPU buzz-in timers | Unit 4 / 7 |
| `$9B` | selected clue difficulty (row) | Unit 4 |
| `$9F` `$A0` | Daily Double board cells | Unit 6 |
| `$AA` | NMI-enable flag (bit 7) | Unit 1 |
| `$44`-`$63` | palette mirror | Unit 7 |
| `$05B4` | player/opponent mode | Unit 3 |
| `$063C` | random-bag working array | Unit 4 |
| `$0200` | OAM (sprite) shadow | Unit 7 |

## The map of the course

| Unit | Title | You'll be able to… |
| --- | --- | --- |
| 1 | Power-On & the First 424 Frames | explain the NES chips and trace the boot to the title |
| 2 | The Controller & Pressing Start | read a joypad in 6502 and follow input to acknowledgment |
| 3 | Setting Up a Game (RAM as Save File) | track game variables in RAM with no battery to lean on |
| 4 | Randomization & Board Building | follow the RNG and the six-category random bag |
| 5 | Huffman, Text, Answer Checking, Scoring | see compressed clues become pixels and judged answers |
| 6 | The Daily Double & Design Decisions | reason about *why* GameTek built it this way |
| 7 | Sound & Vision | read the APU and the sprite/background split |
| 8 | Game Loops & Reset Behavior | explain soft- vs hard-reset and per-game state |
| 9 | Bugs & Exploits | hunt for and reason about defects |
| 10 | The GameTek Family | recognize shared engine DNA (esp. Wheel of Fortune) |
| 11 | If We Built It Today | judge what to change and what's already perfect |
| 12 | The Ultimate Cartridge | combine the romhack ideas into one coherent build |

Start with [Unit 1](Unit%2001%20-%20Power-On%20and%20the%20First%20424%20Frames/lesson.md).
