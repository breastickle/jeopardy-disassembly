# Jeopardy! 25th Anniversary Edition (NES) — disassembly research notes

Consolidated from the sibling Jeopardy projects (QZR palette-randomizer probe,
the JEOPADRY attract-logo relabel, and the ROM-hack research). Everything here
is a starting map for the disassembly, not a finished symbol table.

## Provenance & verification

Most offsets below were originally measured against the QZR working ROM
(`JeopardyNesTextTool/Clean ROM for Python Probe.nes`, cart SHA-1
`C67BEFB8…`), which is a **clue-data variant** — it shares the engine but
~63 % of its bytes differ from stock (all inside the Huffman clue blobs).

**Every code/table offset in this document was then re-verified byte-identical
against the stock No-Intro dump** (cart SHA-1 `317FB395…`, found at
`jeopardy-nescard-ips/Clean ROM for Python Probe.nes` and `…- BACKUP.nes`).
The disassembly target is the **stock dump**. When you reach the clue-data
regions, re-measure on stock — those offsets are *not* guaranteed to match the
QZR variant.

Notation: `file 0xNNNNN` = offset into the .nes file (16-byte iNES header
included, as FCEUX's ROM-file view shows). `$NNNN` = 6502 CPU address.
`file→CPU`: subtract `0x10`, then for bank *b* the in-bank offset maps to
`$8000 + (prg_off mod 0x8000)`.

## ROM identity

- iNES header: `4E 45 53 1A 08 00 70 00 00 00 00 00 00 00 00 00`
- **Mapper 7 (AOROM)**, horizontal/single-screen, no trainer, no battery.
- **PRG 128 KB** = 8×16 KB = **4×32 KB AOROM banks**.
- **CHR-RAM 8 KB** (PRG-resident tile data, DMA'd to CHR-RAM at runtime — no
  CHR-ROM to disassemble, but large PRG regions are tile data).
- File size 131,088 = `0x10` header + `0x20000` PRG.

## Mapper 7 (AOROM) behaviour

- `$8000-$FFFF` is **one switchable 32 KB window**. A write anywhere in
  `$8000-$FFFF` latches: **bits 0-2 = 32 KB PRG bank** (0-3 here), **bit 4 =
  single-screen nametable select (A/B)**.
- Reset/NMI/IRQ vectors live in the tail of *whichever* 32 KB bank is mapped, so
  the vectors are replicated per bank (see table). `RESET` is the same in all
  four; `NMI`/`IRQ` differ per bank because each bank runs its own mode.
- Cross-bank calls pay a per-bank **trampoline / return-thunk tax (~150-175 B)**.
  The clue-blob expansion analysis in
  `jeopardy-study-rando/docs/qzr-romhack-research.md` and
  `jeopardy-nescard-ips/MMC1_MIGRATION_PRECEDENT.md` works this out in detail —
  read those before assuming any bank's free space.

## 32 KB bank map & vectors

| Bank | File range | Vectors (NMI / RESET / IRQ) |
| --- | --- | --- |
| 0 | `0x00010-0x0800F` | `$92BE` / `$FF94` / `$FDF8` |
| 1 | `0x08010-0x1000F` | `$FEA1` / `$FF94` / `$FEA0` |
| 2 | `0x10010-0x1800F` | `$FE77` / `$FF94` / `$FE9E` |
| 3 | `0x18010-0x2000F` | `$FE85` / `$FF94` / `$FE94` |

Vector words are at the bank tail `$FFFA-$FFFF` (file `0x?7FFA`). Start the
disassembly at `RESET $FF94` and bank-0 `NMI $92BE`.

## RAM / memory map (discovered so far)

- **Zero-page palette mirror, `$44-$63` (32 bytes):** `$44-$53` = background
  palette shadow, `$54-$63` = sprite palette shadow. The engine writes the live
  palette here, then a vblank routine copies it to PPU `$3F00`.
- **zp `$0B`/`$0C`:** indirect pointer used by some PPU-upload loops
  (`LDA ($0B),Y` / `STA $2007`).
- PPU registers used the usual way: `$2006`/`$2007` for VRAM address+data,
  `$2000`/`$2001` control/mask, `$4014` OAM DMA (to confirm during disasm).

## Known code routines (bank 0 unless noted)

| CPU | File | What it does |
| --- | --- | --- |
| `$92BE` | `0x012CE`* | Bank-0 NMI (vblank) handler; includes the palette flush below. |
| `$92D7` | `0x012E7` | **Palette flush:** set PPU addr `$3F00`, then copy zp `$44`,`$45`,… to `$2007`. The single writer of palette RAM. |
| `~$9116` | `0x01126` | **Palette upload/init:** `STA $2006`/`$2006`; loop `LDA $9139,X` / `STA $2007` / `STA $0044,Y` ×16 (BG); a second loop at `0x01139` does the 16 sprite entries → `$0054`. |
| `~$8849` | `0x00859` | Loads palette table B (`$BB57`) via `LDA $BB57,Y` into a zp buffer. |

*NMI entry `$92BE` = file `0x012CE`; the flush body begins a few bytes later at
`$92D7`. There are **157 `STA $2007` (`8D 07 20`) sites in bank 0** alone — most
are tight upload loops; a handful are one-off register pokes.

## Known data tables

| CPU / file | Size | Contents |
| --- | --- | --- |
| `$9139` / `0x01149` | 96 B | **Palette table A** — several 16-byte BG+SP frames, universal backdrop `0x0F`. Consumed by the upload loop at `0x01126`/`0x01139`. |
| `$BB57` / `0x03B67` | 96 B | **Palette table B** — same shape, backdrop `0x0F`. Consumed via `0x00859`. |
| — / `0x074B0` | 16 B | Palette-*shaped* (`0F`-backdrop pattern) but **no code xref found** — treat as CHR tile data, not a palette, until proven otherwise. |
| bank 1 `$98C8` / `0x98D8` | 6 B | Attract-screen "JEOPARDY" logo, row A (R/D column strip). |
| bank 1 `$98FA` / `0x990A` | 6 B | Attract-screen logo, row B. Swapping these two rows' R/D strips relabels the attract logo to "JEOPADRY" — see `JeopardyClueWizard/tools/jeopadry_patch.py`. The **title-screen green logo** and the **in-game board header** share letter-boundary nametable columns and can't be relabelled by a byte swap (need new CHR). |
| (clue blobs) | ~110 KB | 4 Huffman-encoded clue blobs, **29 blocks total**. Approx file ranges *on the QZR variant* (re-measure on stock): `0xA047-0xEC97`, `0xF38A-0xFEB0`, `0x10211-0x17E87`, `0x1908C-0x1FE95`. Per-group Huffman trees (4 per compile). Format: `Jeopardy/SCRIPT_FORMAT_NOTES.md` + the QZR huffman docs. |
| (pronoun table) | — | Nibble-packed pronoun index (0-15); see the pronoun-mapping notes referenced in the QZR project. |

## Palette gotcha (carry into any palette work)

NES colors in columns `D`/`E`/`F` of every luma row (`0x0D 0x0E 0x0F 0x1D …
0x3F`) render as black. The engine uses `0x0F` as **structural black**, and some
*non-backdrop* palette slots hold `0x0F` for graphics meant to be invisible
against the black background. Any hue/brightness transform that rotates such a
slot into a visible color makes those elements pop into view (the "random orange
box" seen during QZR palette randomization). Preserve structural blacks. The
working implementation is `jeopardy-study-rando/scripts/probes/palette_probe.py`.

## Authoritative source documents (sibling folders)

- `jeopardy-study-rando/docs/qzr-romhack-research.md` — clue-blob bank layout,
  trampoline tax, PRG free-space and expansion options.
- `jeopardy-study-rando/scripts/probes/palette_probe.py` — palette-table
  scan/verify + the transform/black-preservation logic.
- `JeopardyClueWizard/tools/jeopadry_patch.py` — attract-logo relabel as an IPS;
  good worked example of locating + verifying logo bytes.
- `jeopardy-nescard-ips/MMC1_MIGRATION_PRECEDENT.md` — AOROM bank/trampoline
  disassembly groundwork.
- `Jeopardy/SCRIPT_FORMAT_NOTES.md` — Huffman script format for the clue blobs.

## Open questions for the disassembly

- Confirm the AOROM bank-latch write sites (where does the engine pick banks 1-3
  to read the four clue blobs?).
- Map the full NMI path in bank 0 around `$92BE` (OAM DMA? scroll? the palette
  flush is only part of it).
- Identify the CHR-RAM upload routine(s) and the PRG ranges they treat as tiles
  (so the disassembler marks them as data, not code).
- Re-measure the four clue-blob ranges on the **stock** dump.
