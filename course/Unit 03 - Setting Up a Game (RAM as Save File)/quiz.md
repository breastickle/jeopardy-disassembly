# Quiz — Unit 3

1. How much general-purpose RAM does the CPU have, and what address range is it?
2. Name the three special sub-regions of RAM and what each is for.
3. Why does the engine keep its busiest variables in **zero page**?
4. This cartridge has no battery. What is the practical consequence for "saving" a
   game?
5. Which RAM address holds the player/opponent **mode**, and where is a contestant
   **name** stored?
6. What is a **parallel array**, and how is it different from a struct-per-player?
   Give the stride used for names.
7. What is `$6E`, and what does the engine do with it on every main-loop pass?
8. Write the index math the dispatcher uses to turn `$6E` into a table entry.
9. In FCEUX, describe how you'd find the "number of players" byte if nobody told
   you its address.
10. True/False: RAM contains zeros at power-on, so uninitialized variables are
    safely 0.

<details>
<summary>Answer key & scoring</summary>

1. **2 KB**, at **`$0000-$07FF`**. *(§ "The whole memory")*
2. **Zero page `$00-$FF`** (fast 1-byte addressing), **stack `$0100-$01FF`**
   (returns/pushes), **OAM page `$0200-$02FF`** (sprite shadow). *(§ same)*
3. Zero-page addressing is **one byte shorter and a cycle faster**. *(§ "Zero page
   is precious")*
4. **No persistence** — all state is in RAM and is lost at power-off; there's no
   continue/save. *(§ "The whole memory")*
5. Mode in **`$05B4`**; name in **`$05AF + seat*6`** (6-byte record). *(§ "What
   Setup actually does")*
6. Parallel arrays store **one array per field, indexed by seat** (columns), vs one
   record per player (rows). Names use **stride 6**. *(§ same + glossary)*
7. `$6E` is the **scene/script state**; each pass the engine **dispatches** through
   the `$8901` jump table to that scene's handler. *(§ "The spine")*
8. `index = $6E * 2` (`LDA $6E / ASL / TAY`), then read `$8901,Y` / `$8902,Y`.
   *(§ "The spine")*
9. **RAM Search**: snapshot, choose 2 players, search for value `2`, repeat to
   narrow to one address; freeze it to confirm. *(§ "FCEUX Lab")*
10. **False** — RAM is **garbage** until the program writes it; nothing is free-zeroed.
    *(§ "What to watch for")*

**Scoring:** 8-10 → Unit 4. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
