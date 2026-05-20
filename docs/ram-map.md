# RAM / memory map (discovered so far)

Consolidated from the subsystem analyses (`mapper.md`, `randomizer.md`,
`npc-ai.md`, `text-format.md`). Every entry is byte-verified against the
stock dump. This is a living map — unknown locations are omitted rather
than guessed.

## Zero page

| Addr | Name / role | Where seen |
| --- | --- | --- |
| `$00` | far-call return-bank scratch | `FarCall` `$FF82` |
| `$01` | **frame counter** — `INC` each NMI (`$938B`); RNG + timing entropy | NMI, `Rng_Advance` |
| `$02` | **RNG accumulator / output byte** | `Rng_Advance $9027` |
| `$03` | RNG state byte (second output tap) | `Rng_Advance`, bag, AI |
| `$05`/`$06` | NMI resume pointer — NMI ends `JMP ($0005)` | NMI `$938D` |
| `$07`/`$08` | dispatcher pointer — `Dispatcher` `JMP ($0007)`; `$08` forced `$80` | `$8000`, `FarCall` |
| `$0B`/`$0C` | string/PPU-upload source pointer | `DrawString $921E` |
| `$0D` | scroll-Y shadow | cold boot `$80DA` |
| `$0F` | general scratch (base index, counts, palette idx) | bag, palette, text |
| `$11` | bag draw counter (0-5) / copy count | `Board_RandomBag` |
| `$12` | bag pool size (modulus for the uniform draw) | bag, `$8E80` |
| `$16` | name-pool slot index | `Npc_PickName` |
| `$19`-`$1C` | live state bytes (mixed into RNG; `$1A` = cursor/dir bits) | RNG, `State_BoardCursor` |
| `$20` | live state byte (mixed into RNG) | `Rng_Advance` |
| `$25,X` | per-seat score digits (5 wide, stride 5) | `$A84E` |
| `$3C` | state/sub-state scratch | cold boot, `$80B2` |
| `$3F` | requested next state id | `$979C`, `$9AC9` |
| `$44`-`$53` | **background palette mirror** (16 bytes) | `PaletteFlush`, `LoadPalette` |
| `$54`-`$63` | **sprite palette mirror** (16 bytes) | `PaletteFlush`, `LoadPalette` |
| `$68`/`$69` | request flags (draw / refresh) | many |
| `$6A` | board cursor Y (pixels) → difficulty `$9B` | `State_BoardCursor` |
| `$6E` | **current game-state index** (×2 → `StateJumpTable`) | main loop `$88BA` |
| `$70`/`$77`/`$78` | **current contestant index** (0-2) and copies | NPC, name/face |
| `$84`,`$85,X`,`$AE,X` | per-seat buzz / lockout flags | `Turn_BuzzPoll` |
| `$8F` | **CPU seat-2 buzz-in countdown timer** | AI |
| `$90` | **CPU seat-3 buzz-in countdown timer** | AI |
| `$9A` | "intro done / board ready" flag | `$8F2B`, main loop |
| `$9B` | **selected clue difficulty** (board row) — indexes AI table | `State_BoardCursor`, `Npc_RollReaction` |
| `$9F`/`$A0` | **Daily Double board cell(s)** (0-29) | `DailyDouble_Place` |
| `$AA` | **NMI mode flag** (bit 7 = full vblank update enabled) | NMI, boot |
| `$AC` | timer scratch | `$9AC2` |
| `$C6` | countdown timer (board animation) | main loop `$8897` |
| `$FE` | RNG carry-chain byte | `Rng_Advance $903B` |

## Main RAM ($0200+)

| Addr | Role |
| --- | --- |
| `$0200-$02FF` | **OAM shadow** (sprite DMA source; `$4014 <- #$02`); cleared to `$F8` by `ClearOAM` |
| `$0300` | PPUMASK shadow (rendering-enable value) |
| `$05AF + seat*6` | per-seat **contestant name** (6 chars, copied from `NamePool`) |
| `$05B4` | opponent count / player mode |
| `$05CF,X`,`$0620,X` | per-seat **appearance / portrait** attributes |
| `$05D1` | appearance dedup reference |
| `$05D6,X` (X=0-29) | **per-cell answered flags** (6 cols × 5 rows board) |
| `$063C,X` | **random-bag working array** — per-cell used-slot bitmask (`$FC` = full) |
| `$0632`-`$0634`, `$0633` | board build scratch |
| `$03D2` | round mode (0 = Jeopardy, else Double) |
| `$03D3`,`$049E` | live RAM mixed into the RNG |
| `$03D5` | misc state flag |

## Notes

- The palette mirror (`$44-$63`) is the single source the NMI flushes to
  PPU `$3F00`; nothing else writes the palette directly. (Carried from
  `research-notes.md`; confirmed in `PaletteFlush`.)
- `$01` does triple duty: frame timing waits, RNG entropy, and small
  animation phases (`LDA $01 / LSR / AND #$0F` palette cycle at `$88D1`).
- Seat indexing is inconsistent on purpose: some code uses the raw seat
  number (`$AE,X`), some uses `seat*6` (name records) or `seat*5` (score
  digits `$25,X`). Watch the stride when reading a per-seat access.
