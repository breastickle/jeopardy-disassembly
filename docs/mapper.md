# The mapper — AOROM (iNES mapper 7), as this ROM actually uses it

This is focus area #1. Everything below was read out of the stock dump
with `tools/disasm6502.py` (cart SHA-1 `317FB395…`) and is byte-verified.
Addresses are CPU addresses; `file 0x…` are offsets into the `.nes`
(16-byte iNES header included).

## What AOROM is

AOROM (the "AxROM" family, iNES mapper 7) is about the simplest PRG
banking the NES has. There is **one register**: any write to
`$8000-$FFFF` latches a single byte. On this board only three things in
that byte matter:

```
   7  bit  0
   ---- ----
   xxxM xPPP
      |  |||
      |  +++- bits 0-2: select the 32 KB PRG bank at $8000-$FFFF
      +------ bit 4   : select the 1 KB nametable (single-screen A / B)
```

- **Bits 0-2 = PRG bank.** 128 KB PRG ÷ 32 KB = **4 banks**, so only the
  low two bits are ever meaningful here; the board does not wire enough
  bank lines for bit 2 to reach anything.
- **Bit 4 = nametable.** AOROM has no four-screen or scrolling-mirroring
  hardware — it gives you *single-screen* mirroring and lets you pick
  which 1 KB page (A or B) the whole screen shows. The game uses this
  (below).
- **Bit 3 is electrically ignored** on a 4-bank board. The reset code
  nonetheless writes `#$08` (bit 3 set) — see "Developer decisions."

There is no CHR-ROM (`CHR count = 0` in the header) — 8 KB of CHR-RAM is
filled from PRG at runtime. AOROM has no scanline IRQ, no CHR banking, no
PRG-RAM. The ROM uses none of those, so this document does not discuss
them.

## The whole-image layout

| AOROM bank | File range | PRG (16 KB) file banks | Vectors NMI / RESET / IRQ |
| --- | --- | --- | --- |
| 0 | `0x00010-0x0800F` | 0+1 | `$92BE` / `$FF94` / `$FDF8` |
| 1 | `0x08010-0x1000F` | 2+3 | `$FEA1` / `$FF94` / `$FEA0` |
| 2 | `0x10010-0x1800F` | 4+5 | `$FE77` / `$FF94` / `$FE9E` |
| 3 | `0x18010-0x2000F` | 6+7 | `$FE85` / `$FF94` / `$FE94` |

Because the entire 32 KB window swaps at once, the 6502 vectors
(`$FFFA-$FFFF`) live in *whichever* bank is mapped. RESET is identical in
all four banks; NMI and IRQ differ because each bank runs its own mode.
Bank 0 is the engine/home bank; banks 1-3 are mostly Huffman-compressed
clue data with a thin shell of code around it.

## Boot: how the machine gets into bank 0

`RESET` (`$FF94`, same bytes in every bank):

```asm
FF94  SEI                  ; no IRQs during boot
FF95  LDA #$08             ; bank 0  (bits 0-2 = 0; bit 3 ignored)
FF97  STA $8000            ; *** AOROM latch: map bank 0, nametable A
FF9A  JMP $8021            ; -> cold-boot in bank 0
```

`$8021` is the real cold start: zero the stack, `PPUCTRL=$10`,
`PPUMASK=0`, two `PPUSTATUS` polls to wait out PPU warm-up, silence the
APU (`$4000-$4017`), then bring graphics up through a series of
cross-bank calls (next section). It ends by falling into the main loop
via `JMP $925A` (`$80CD`).

## The cross-bank call mechanism (the "trampoline tax")

Code in bank 0 constantly needs routines and data that live in banks 1-3.
Switching banks is dangerous: the instant you write `$8000`, the bytes
under the program counter change. AOROM games solve this by putting the
switch code at the **same address in every bank**, so execution survives
the swap. This ROM's solution has three parts, all in the shared bank
tail (`$FF80-$FFFF`, identical in all four banks):

### 1. The dispatcher at `$8000`

```asm
8000  JMP ($0007)          ; every bank begins with this
```

`$8000` in *every* bank is an indirect jump through zero-page `$07/$08`.

### 2. A jump table at `$8003+` in each switchable bank

Right after the dispatcher, banks 1-3 carry a table of `JMP`s to their
real entry points. Bank 1, for example:

```asm
8003  JMP $818E            ; entry index $03
8006  JMP $819B            ; entry index $06
8009  JMP $818B            ; entry index $09
800C  JMP $808D            ; …
…
```

So a routine in another bank is named by the **low byte of its table
slot** (`$03`, `$06`, `$09`, …). Bank 1 has ~20 such slots; bank 3 has
only 6 (it is almost entirely clue data).

### 3. The far-call trampoline at `$FF80`

```asm
FF80  STX $07              ; X = low byte of target ($80xx table slot)
FF82  STY $00              ; Y = bank to return to (saved)
FF84  LDX #$80
FF86  STX $08              ; $07/$08 now = $80xx in the target bank
FF88  STA $8000            ; *** latch: switch to target bank (A)
FF8B  JSR $8000            ; -> JMP ($0007) -> the table slot -> real code
FF8E  LDA $00              ; recover the return bank
FF90  STA $8000            ; *** latch: switch back
FF93  RTS
```

**Calling convention** (verified at 52 call sites in bank 0):

| Reg | Meaning |
| --- | --- |
| `A` | target AOROM bank (0-3) |
| `X` | low byte of the `$80xx` jump-table slot in that bank |
| `Y` | bank to return to after the call |

A typical site from cold boot:

```asm
805D  LDX #$3C             ; -> bank 1 slot $803C
805F  LDA #$01             ; bank 1
8061  LDY #$00             ; return to bank 0
8063  JSR $FF80            ; far-call bank1:$803C, come back to bank 0
```

This is the "~150-175 B per-bank trampoline tax" the sibling QZR/IPS
notes describe: the dispatcher, the table, and the trampoline are
*duplicated in every bank* because AOROM has no fixed bank to keep them
in. (A 16 KB-granular mapper with a fixed bank would not need the
duplication — see "Developer decisions.")

A second small thunk lives at `$FFE0` (`STA $8000` / `JSR $FF9D` /
`LDA #$00` / `STA $8000` / `RTS`); `$FF9D` is a `DEX/BNE/DEY/BNE` delay
loop. It switches bank, spins a timed delay, and returns to bank 0. It is
not called from bank 0.

## Single-screen mirroring (bit 4) in practice

AOROM shows one nametable at a time. To paint a full screen the engine
writes one page, flips bit 4, and writes the other. You can see the flip
in the cold-boot graphics setup:

```asm
8091  STA PPUCTRL          ; A = #$10
8094  STA $8000            ; latch #$10 -> bank 0, NAMETABLE B
8097  JSR $904A            ;   upload …
809A  STA $8000            ; (re-latch)
809D  JSR $904A            ;   upload …
…
80AD  STA $8000            ; #$10 -> nametable B again
```

The bank-0 **NMI** then latches `#$00` (`$92C9`) at the top of every
vblank — forcing **bank 0 + nametable A** before it runs OAM DMA and the
palette flush. This guarantees the vblank handler always executes against
known code and a known display page no matter which bank the main thread
was using when the frame interrupt hit.

## Every bank-latch site (where `$8000` is written)

| Site | Bank context | Value | Effect |
| --- | --- | --- | --- |
| `$FF97` | all (RESET) | `#$08` | map bank 0 at boot |
| `$8094`,`$809A`,`$80AD`,`$80D2` | 0 (cold boot) | `#$10` | bank 0, nametable B (screen paint) |
| `$92C9` | 0 (NMI) | `#$00` | force bank 0 + nametable A each vblank |
| `$FF88`,`$FF90` | all (far-call) | A / `$00` | switch to callee bank / back |
| `$FFE0`,`$FFE8` | all (delay thunk) | A / `#$00` | switch out / back to bank 0 |

`STA $8000` (`8D 00 80`) is the only latch encoding the ROM uses; it
never writes the latch through an index or a different address, which
keeps the bank state easy to follow.

## Developer decisions (kept brief)

- **`#$08` at reset, not `#$00`.** Bit 3 is a don't-care on a 4-bank
  AOROM board, so `#$08` and `#$00` both select bank 0. The choice is
  cosmetic; the latch hardware ignores the extra bit.
- **AOROM at all.** AOROM is the cheapest mapper that gives 128 KB +
  CHR-RAM, and Rare used it across its NES catalog (Battletoads, R.C.
  Pro-Am, Marble Madness, …). The cost is the per-bank trampoline tax and
  the loss of hardware scrolling mirroring; for a static, single-screen
  quiz board that trade is almost free. A fixed-bank mapper (MMC1) would
  have removed the duplicated trampolines, but at more board cost and
  more code — not worth it for this game's needs.
- **Single-screen by design.** The Jeopardy board never scrolls, so
  single-screen mirroring with a manual A/B flip is enough; the engine
  spends no bytes on a scrolling-nametable mirroring scheme it would
  never use.

## Reproduce

```sh
ROM="../jeopardy-nescard-ips/Clean ROM for Python Probe.nes"
python tools/disasm6502.py "$ROM" --bank 0 --linear FF80 FFFA   # trampoline + RESET
python tools/disasm6502.py "$ROM" --bank 0 --linear 8000 80E0   # dispatcher + cold boot
python tools/disasm6502.py "$ROM" --bank 1 --linear 8000 8040   # bank-1 jump table
python tools/disasm6502.py "$ROM" --bank 0 --find "8D 00 80"    # every latch site
```
