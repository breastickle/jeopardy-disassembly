# Unit 3 — Setting Up a Game (RAM as Save File)

> *"With no battery, the 2 KB of RAM **is** the save file — until you power off."*

## Learning objectives

1. Read the 2 KB RAM map: zero page, stack, the OAM page, and game variables.
2. Explain why a game with no battery keeps *all* its state in RAM.
3. Follow the Setup screen as it writes the player's choices into specific RAM
   locations.
4. Understand the **scene/script** variable `$6E` as the spine of the game.

## The whole memory the program gets

The CPU sees 2 KB of RAM, `$0000-$07FF`, with three special regions:

| Range | Name | Why it's special |
| --- | --- | --- |
| `$0000-$00FF` | **zero page** | 1-byte addressing → smaller, faster code; used for hot variables |
| `$0100-$01FF` | **stack** | `JSR`/`RTS` return addresses and `PHA`/`PLA`; `SP` starts at `$FF` |
| `$0200-$02FF` | **OAM page** | the sprite shadow that gets DMA'd to the PPU each frame |
| `$0300-$07FF` | game variables | everything else the game needs |

There is **no battery and no save RAM** on this cartridge (`.gitignore` even
excludes `*.sav` for nothing — there are none). So "a game" — scores, names, who's
in control, the board state — exists **only** in these 2 KB. Power off and it's
gone; that's why there's no "continue."

## Zero page is precious

Because zero-page addressing is one byte shorter and a cycle faster, the engine
puts its busiest variables there. You've already met several:

- `$01` frame counter, `$02/$03` RNG, `$05/$06` NMI resume pointer,
  `$07/$08` dispatch pointer, `$44-$63` palette mirror,
- `$6E` **scene/script state**, `$70` current contestant, `$8F/$90` CPU buzz timers,
  `$9B` difficulty, `$AA` NMI flag.

Full list: [`../docs/ram-map.md`](../../docs/ram-map.md).

## What "Setup" actually does (Screen 02)

The Setup sequence (Screen 02) is, underneath the menus, a series of **writes to
RAM**. As you answer each prompt, a variable gets set and stays set for the rest of
the game:

| Choice | Lands in RAM |
| --- | --- |
| Number of players / vs-CPU | `$05B4` (mode) |
| Player name (≤ 6 chars) | `$05AF + seat*6` (6-byte record per seat) |
| Character / appearance | `$05CF,X`, `$0620,X` |
| (later) score | `$25,X` (5 digits per seat) |

Notice the **`seat*6`** and **`,X`** patterns: this is the **parallel-array** layout
from the glossary — one array per field, indexed by seat number, *not* a struct per
player. (Unit 4 and 7 lean on this.)

## The spine: `$6E`

Everything the game does is gated by **`$6E`**, the scene/script state. The main
loop reads it, multiplies by two, and jumps through the table at **`$8901`**:

```asm
88BA  LDA $6E / ASL / TAY        ; index = $6E * 2
88BE  LDA $8901,Y / STA $07      ; pointer low
88C3  LDA $8902,Y / STA $08      ; pointer high
88C8  JSR $8000                  ; JMP ($0007) -> the scene handler
```

So **your Screens 00-08 are values of `$6E`.** Setup writes the player's choices;
then `$6E` advances to the board state and the game proper begins. Mapping every
`$6E` value to a handler is Open Question #1 in [`../ux/ROADMAP.md`](../../ux/ROADMAP.md).

## FCEUX Lab

1. **Watch state get written.** Add `$05B4`, `$6E`, and the name region `$05AF`
   (watch 6 bytes) to RAM Watch. Walk through Setup and see each choice land.
2. **Find "number of players" cold.** Use **RAM Search**: before choosing, snapshot;
   pick "2 players"; search for the value `2`. Narrow it to confirm it's `$05B4`
   (or whatever your dump shows) — this is the core skill of *finding* a variable
   you weren't told about.
3. **Freeze to prove meaning.** Freeze a score byte (`$25,X`) mid-game in the Hex
   Editor (right-click → Freeze) and watch the score stop changing — proof you
   found the right address.
4. **Read the names.** In the Hex Editor (NES Memory view), look at `$05AF…` — the
   stored name reads almost like ASCII (recall the codec is `tile = char − $2C`).

## What to watch for

- **Zero-page density** — the hottest variables cluster in `$00-$FF`.
- The **`seat*6` / `,X` stride** of per-seat data (parallel arrays).
- `$6E` changing **once per screen** — it's the state machine's program counter.
- RAM that's **garbage until written** — nothing here is zero-initialized for free.

## Key takeaways

- The 2 KB RAM is the **entire** mutable state; no battery means no persistence.
- **Zero page** holds the hot variables for speed/size.
- Setup is just **writes to RAM**; the parallel-array layout stores per-seat data
  in columns.
- **`$6E` is the script/scene state**, dispatched through `$8901` — the backbone of
  every later unit.

Next: [Unit 4 — Randomization & Board Building](../Unit%2004%20-%20Randomization%20and%20Board%20Building/lesson.md).
