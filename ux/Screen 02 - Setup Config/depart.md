# Screen 02 — Setup Config · Depart

This screen runs a **mandatory sequence** that always occurs in the same order:

1. **Number of (human) players** — 1, 2, or 3.
2. **Skill Level** — 1, 2, or 3.
   - If 1 or 2 players: **Vs the Computer?** (yes / no).
3. **Human Player 1 — Input Name** (A–N, O–Z, backspace, end).
   - 6 characters max.
   - Fewer characters will try to center the input, leaning left on a rounding
     fraction.
4. **Would you like a new character?** (yes / no)
   - **Yes** — changes the player character/sprite.
     - 8 models; each loop also changes the palette.
   - **No** — confirms the player selection.
     - **1 human player** → fill the remaining 2 podiums with random selection.
     - **2 human players** → fill the remaining 1 podium with random selection.
5. **"Contestants, Let's play Jeopardy"** → proceeds to **Screen 03 — Game Board
   Setup**.

> **ROM correlation (well supported):**
> - **"6 characters max"** matches the name storage exactly: the name pool at
>   `$8DF9` holds **6-character records**, and a chosen name is copied to
>   `$05AF + seat*6`. The left-leaning centering is the text codec
>   (`tile = char − $2C`, comma `$2C` = blank). See [`../../docs/npc-ai.md`](../../docs/npc-ai.md).
> - **"8 models, each loop changes the palette"** matches the per-seat appearance
>   picker at `$8F0C` (attributes in `$05CF,X` / `$0620,X`).
> - **"Fill remaining podiums with random selection"** matches the CPU name/face
>   draws (`Npc_PickName $8E5C`, `Npc_PickFace $8F0C`), each a random draw with a
>   **no-repeat re-roll** so opponents differ.
>
> **ROM correlation (candidate, unconfirmed):** the **Skill Level (1–3)** most
> likely shifts the CPU **reaction-time** lookup (table `$A80D`, indexed by
> difficulty `$9B`) — i.e. it biases how often the CPUs "know it" and how fast
> they buzz. Confirming where skill is stored and how it feeds that index is a
> high-value tracing target.
