# jeopardy-disassembly

A work-in-progress, byte-exact 6502 disassembly of **Jeopardy! 25th Anniversary
Edition** (NES, USA).

The goal is a clean, commented, *reassemblable* source for the game engine, so
the sibling projects (the QZR randomizer, the IPS patch, the Clue Wizard editor)
can stand on a real source-level understanding of the ROM instead of one-off
offset probing. Most of what's in `docs/research-notes.md` was already learned
the hard way by those projects; this repo collects it and turns it into a
disassembly.

## Legal / ROM

This repository contains **no ROM and no copyrighted game data**. *Jeopardy! 25th
Anniversary Edition* is © its respective rights holders. You must supply your own
legally-dumped copy to build or test anything here. `.gitignore` excludes `*.nes`
specifically so a ROM can never be committed by accident.

**Target image — the No-Intro USA dump:**

| Property | Value |
| --- | --- |
| Cartridge SHA-1 (headerless) | `317FB395B4D408F3A4BEF73DD54C92FBB7748F4D` |
| Cartridge CRC32 (headerless) | `0BDD8DD9` |
| File size | 131,088 bytes (16-byte iNES header + 131,072 PRG) |

> The cart hash is authoritative on NES; iNES-header byte drift is normal and
> doesn't affect emulation. Verify your dump's *headerless* hash matches before
> relying on any offset in `docs/`.

## ROM at a glance

- **Mapper 7 (AOROM)** — one switchable 32 KB bank at `$8000-$FFFF`.
- **128 KB PRG** = 8×16 KB = **4×32 KB banks**. **8 KB CHR-RAM** (no CHR-ROM —
  tiles are uploaded from PRG at runtime). Single-screen mirroring.
- **RESET = `$FF94`** in every bank. Bank-0 **NMI = `$92BE`** (its vblank handler
  flushes the palette — see notes).

Full memory map, vectors, known routines, and data tables are in
[`docs/research-notes.md`](docs/research-notes.md).

## What's documented

The three subsystems the project set out to understand are reverse-
engineered and byte-verified against the stock dump:

| Doc | Covers |
| --- | --- |
| [`docs/mapper.md`](docs/mapper.md) | **AOROM (mapper 7)** as actually used: boot, the per-bank far-call trampoline + `$8000` dispatcher + jump tables, single-screen mirroring, every bank-latch site. |
| [`docs/randomizer.md`](docs/randomizer.md) | **Gameboard randomization**: the `$9027` "stir-the-pot" RNG (seeded by frame timing) and the `$82B1` six-category **random bag** (draw-without-replacement). |
| [`docs/npc-ai.md`](docs/npc-ai.md) | **NPC contestants**: random name/face draws (with no-repeat re-rolls) and the "limited AI" — a 12-byte reaction-time table where `$FF` = "doesn't know it." |
| [`docs/text-format.md`](docs/text-format.md) | The UI text codec (`tile = char − $2C`, bit-7 terminator) and the string-draw routines. |
| [`docs/ram-map.md`](docs/ram-map.md) | Consolidated zero-page / RAM variable map. |
| [`docs/research-notes.md`](docs/research-notes.md) | Original consolidated findings (banks, vectors, palette, clue blobs). |

## Status

**Subsystems mapped.** The mapper, board randomizer, and NPC AI are
disassembled, documented, and reproducible from the ROM via the tools
below. A reproducible Python disassembler (`tools/disasm6502.py`) and an
accumulating symbol file (`src/jeopardy.sym.json`) back all of it. Full
byte-exact ca65 reassembly of the whole image is the next milestone (the
`ld65` layout is staged in `src/jeopardy.cfg`; cc65 is not yet installed
here, so end-to-end reassembly is not yet verified).

## Tools (work now, no install needed — Python 3 only)

```sh
ROM="path/to/your.nes"                    # supply your own legal dump
python tools/verify.py "$ROM"             # confirm it's the stock dump
python tools/gen_listings.py "$ROM"       # -> build/listings/documented.lst
# ad-hoc exploration:
python tools/disasm6502.py "$ROM" --bank 0 --syms src/jeopardy.sym.json --linear 9027 904A
python tools/disasm6502.py "$ROM" --bank 0 --trace        # code-coverage from vectors
python tools/disasm6502.py "$ROM" --bank 0 --find "8D 00 80"   # byte search
```

Generated listings are ROM-derived, so they are treated as build output
(git-ignored under `build/`). The repo commits only authored material —
the disassembler, the symbol/label file, and the analysis in `docs/`.

## Toolchain

- **`tools/disasm6502.py`** — the working disassembler used for all the
  analysis here. Dependency-free Python 3; full 256-entry 6502 matrix
  (undocumented opcodes flagged, which doubles as a data detector);
  models the AOROM banks; `--trace` / `--linear` / `--find` / `--xref` /
  `--dump` / `--refs`. Reads `src/jeopardy.sym.json` for annotations.
- **cc65 suite** (`ca65` + `ld65`) — for the eventual byte-exact
  reassembly (layout staged in `src/jeopardy.cfg`). Not yet installed
  here; reassembly is the next milestone, not a finished feature.
- **Mesen2 / FCEUX** — runtime debugging, PPU/event viewer, ROM-file hex.

Iterative workflow: grow `src/jeopardy.sym.json` (mark code vs. data, add
labels/comments) → `python tools/gen_listings.py` to re-emit annotated
listings → eventually `ca65`/`ld65` and diff against the stock dump until
byte-identical. The mapper, randomizer, and NPC AI are already done this
way; start new work from a vector or a `--trace` coverage gap.

## Layout

```
jeopardy-disassembly/
├─ README.md  LICENSE  .gitignore
├─ docs/                     # the analysis (mapper, randomizer, npc-ai, …)
├─ src/
│  ├─ jeopardy.sym.json      # authored labels/comments/data ranges
│  └─ jeopardy.cfg           # ld65 AOROM layout (reassembly groundwork)
├─ tools/
│  ├─ disasm6502.py          # the disassembler
│  ├─ gen_listings.py        # ROM -> build/listings/documented.lst
│  └─ verify.py              # confirm a dump is the stock image
└─ build/                    # generated, git-ignored (ROM-derived listings)
```

## Related projects (same workspace)

See the workspace map in `../AGENTS.md`. In short: **jeopardy-study-rando**
(QZR randomizer), **jeopardy-nescard-ips** (IPS deliverable),
**JeopardyNesTextTool/JeopardyClueWizard** (editor), **Jeopardy/** (shared format
reference). `docs/research-notes.md` cites the specific source documents in those
folders.

## Glossary (NES Jeopardy family)

ROM = Season · Block = Episode · Topic = Category · Clue = Answer · Reply = Question.

## Version control

The maintainer owns all git actions (per the workspace `AGENTS.md`). This
bootstrap only created files — do the initial `git init` / commit yourself.
