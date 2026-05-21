# Unit 8 — Game Loops and Reset Behavior

> *"The myth: 'soft reset keeps your RAM.' The truth is more interesting."*

## Learning objectives

1. Describe the main loop and how it cooperates with the NMI.
2. List what state defines "a game" and where it lives.
3. Explain — accurately — why a **soft reset** seems to retain RAM while a **cold
   boot** starts fresh, and what the hardware vs the game each contribute.

## The game loop is a cooperative state machine

There's no `while(true){ update(); render(); }` with a render call. Instead:

- The **main thread** (from `$925A`) reads `$6E`, dispatches to the current scene's
  handler via the `$8901` jump table, prepares data, and then drops into the **idle
  spin** at `$93A3` (`JSR $9027 / JMP $93A3`) — churning the RNG while it waits.
- The **NMI** (`$92BE`) fires each vblank, commits graphics (OAM DMA, palette flush),
  bumps the frame counter `$01`, and **resumes the main thread** via `JMP ($0005)`.

So "the loop" is really *main-thread setup* + *NMI heartbeat*, coordinated through
the resume pointer `$05/$06` and the NMI-enable flag `$AA`. Scene changes are just
writes to `$6E` (Units 3, the roadmap).

## What "a game" is, in bytes

Everything that makes *your* game *yours* is the RAM you met in Unit 3:

- scores `$25,X`, names `$05AF+seat*6`, appearance `$05CF,X`,
- mode `$05B4`, round `$03D2`, current contestant `$70`,
- board scratch `$063C`, per-cell flags `$05D6,X`, Daily Doubles `$9F/$A0`,
- RNG state `$02/$03/$FE`.

No battery, no save — so this is the entire "game in progress."

## The reset myth, debunked

A common belief: *"the game keeps RAM on a soft reset and clears it on a hard boot."*
The reality:

1. **Both** power-on and the Reset button make the CPU run the **same** `RESET`
   vector → `$8021`. There is no separate "reset path."
2. **Neither event clears RAM in hardware.** The console's work RAM is static RAM; a
   reset **pulse** doesn't erase it, and the boot routine only clears **specific**
   things — `$AD`, the NMI flag `$AA`, OAM (to `$F8` via `ClearOAM $9203`), `$0300`
   (via `$91F2`). It does **not** wipe `$0000-$07FF`.
3. So after a **soft reset**, last session's RAM is **still physically there** until
   the per-screen init overwrites the bytes it cares about. After a **cold power-on**,
   RAM is **indeterminate** — garbage/patterns from cold silicon, different machine
   to machine — so there's nothing meaningful to "keep."

**The punchline:** retention is **hardware physics + the game not bothering to wipe
RAM**, *not* a deliberate "remember my game" feature. (As far as we've mapped, there's
no warm-boot **signature check** — no "is this magic byte still here? then trust the
old RAM." The game just re-initializes what each screen needs.) Verifying that
absence is your lab — and the leftover RAM it implies is exactly the surface Unit 9
pokes at.

> Emulator note: FCEUX *chooses* a power-on RAM fill (all-`$00`, all-`$FF`, or a
> pattern) because real cold RAM is unpredictable. Its **Reset** keeps current RAM;
> its **Power** re-applies the fill. That lets you see both behaviors deliberately.

## FCEUX Lab

1. **Watch the heartbeat hand off.** Breakpoint the NMI (`$92BE`) and the idle spin
   (`$93A3`). Step and narrate: main thread spins, NMI preempts, `JMP ($0005)` hands
   control back.
2. **Prove soft-reset retention.** Mid-game, note a few RAM bytes (a score `$25,X`,
   a name char at `$05AF`). `Emulation → Reset`. In the Hex Editor, confirm those
   bytes are **still there** right after reset — *before* the title re-inits them.
3. **Prove cold-boot difference.** `Emulation → Power` (or set a different power-on
   RAM fill in `Config`). Confirm RAM comes up as the **fill pattern**, not your old
   values.
4. **Look for a warm-boot check.** Step through `$8021` watching for a `LDA $xxxx /
   CMP #magic / BEQ` that decides whether to trust old RAM. Report what you find (we
   expect: none — it re-inits per state).

## What to watch for

- The **same `$8021`** running on both power and reset.
- The boot clearing **only** OAM, `$0300`, and a few flags — **not** all of RAM.
- RAM **surviving** a soft reset until overwritten; **garbage/fill** on cold boot.

## Key takeaways

- The "loop" is a **cooperative state machine** (main thread + NMI heartbeat) keyed
  on `$6E`.
- "A game" is entirely the **RAM variables** from Unit 3 — no persistence.
- Soft-reset "memory" is **SRAM physics plus an incomplete wipe**, not a feature; the
  leftover bytes are real and pokeable (Unit 9).

Next: [Unit 9 — Bugs & Exploits](../Unit%2009%20-%20Bugs%20and%20Exploits/lesson.md).
