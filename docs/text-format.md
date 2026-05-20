# The on-screen text codec (UI / names / board labels)

This is the *interface* text format — distinct from the Huffman-
compressed **clue** blobs in banks 1-3 (those are documented in the
sibling `Jeopardy/SCRIPT_FORMAT_NOTES.md`). Menus, contestant names,
score labels and category headers all use this simpler scheme. Verified
with `tools/disasm6502.py`.

## Encoding

UI strings are stored close to **ASCII**, and the renderer maps a
character byte to a CHR tile index by subtracting `$2C`:

```
tile = char_byte − $2C
```

So `,` (`$2C`) → tile `$00` (the blank tile — which is why the name pool
uses commas as separators and padding), `A` (`$41`) → tile `$15`, and so
on. The clue/board renderer at `$923A` additionally rebases visible
glyphs by `+$AC` after the subtract, to reach a different tile page.

Strings are **bit-7 terminated**: the final character has `$80` OR'd in.
The drawing loop masks it off (`AND #$7F`) and stops when it sees the set
high bit.

## The string-draw routines (bank 0)

| CPU | Role |
| --- | --- |
| `$920E` | draw *N* strings: `$0F` = count, `$0B/$0C` = pointer; calls `$921E` per string |
| `$921E` | draw one string: read a 2-byte PPU address from `($0B),Y`, then emit `char − $2C` to `PPUDATA` until a byte with bit 7 set |
| `$923A` | board/label variant: `$00`-terminated, emits `(char − $2C) + $AC` (different tile page) |

```asm
; $921E — the core UI string writer
921E  LDA ($0B),Y / STA PPUADDR    ; destination high byte
9224  LDA ($0B),Y / STA PPUADDR    ; destination low byte
922A  LDA ($0B),Y / PHA            ; next char
922D  AND #$7F / SEC / SBC #$2C    ; strip terminator bit, map to tile
9232  STA PPUDATA
9236  PLA / BPL $922A              ; loop until the high bit was set
```

Each string record is therefore: `[PPU addr hi] [PPU addr lo] [chars…
last|$80]`, and `$920E` walks a run of them back-to-back.

## Why it matters here

- The **contestant name pool** at `$8DF9` is stored in this codec (commas
  = blanks/separators), which is why the NPC name picker can copy six raw
  bytes and feed them straight to the same renderer (see `npc-ai.md`).
- Recognising the `−$2C` rule lets `tools/disasm6502.py --dump` be read
  directly: a region whose bytes are mostly `$2C`-and-uppercase is UI
  text, not code or compressed data.

## Reproduce

```sh
ROM="../jeopardy-nescard-ips/Clean ROM for Python Probe.nes"
python tools/disasm6502.py "$ROM" --bank 0 --linear 920E 923A   # string writers
python tools/disasm6502.py "$ROM" --bank 0 --dump   8DF9 8E5C   # a text region
```
