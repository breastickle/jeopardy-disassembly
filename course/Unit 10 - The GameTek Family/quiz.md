# Quiz — Unit 10

1. Why do sibling games from the same studio tend to share internal patterns?
2. Predict how Wheel of Fortune's **wheel spin** randomness most likely works, based
   on *Jeopardy*.
3. What kind of construct should you expect for a sibling's **CPU opponent**, and
   what sentinel value would hint at it?
4. What single RAM byte + structure embodies the **scene/state machine**, and what's
   its analog called when you go looking in another game?
5. Name two patterns besides RNG and AI that should transfer to a sibling.
6. What mapper family and CHR setup is likely across these GameTek titles?
7. Why is it valuable to **write predictions down before** disassembling a sibling?
8. On an idle screen, what observable behavior fingerprints the RNG?
9. When a sibling **differs** from the house style, why is that a *good* outcome?
10. How would you adapt our `verify.py` to a different cartridge?

<details>
<summary>Answer key & scoring</summary>

1. Studios **reuse people and tools**, so they reuse code patterns. *(§ "The house
   style")*
2. A small RNG **churned every frame while the wheel spins**, **sampled when you
   stop it**, then reduced by mask/modulo — the *Jeopardy* idiom. *(§ "Predicting")*
3. A **table-driven** decision (delays/odds indexed by skill) — an `$FF`-style
   "doesn't know / miss" sentinel hints at it. *(§ same)*
4. A **single state byte (`$6E` here) → jump/pointer table**; you look for the
   "byte that changes once per screen" + its table. *(§ "The house style" / "Lab")*
5. Any two: **text codec**, **parallel-array RAM**, **AOROM + trampoline**,
   **podium/Press-Start flow**, **random bag**. *(§ table)*
6. **AOROM-family banking with CHR-RAM** (coarse 32 KB banks, duplicated bank-tail
   glue). *(§ "Predicting" / table)*
7. It makes confirmation **scientific** — you test predictions instead of
   rationalizing after the fact. *(§ "Predicting")*
8. A **zero-page byte that changes every frame** though nothing is happening.
   *(§ "Lab")*
9. A genuine **difference** is something interesting unique to that title — worth
   studying. *(§ "Predicting Wheel of Fortune")*
10. **Swap in that dump's headerless SHA-1/CRC32** (and size) as the targets.
    *(§ "Lab")*

**Scoring:** 8-10 → Unit 11. 5-7 → re-read flagged sections. 0-4 → redo the lab.
</details>
