# Screen 08 — Final Jeopardy · Depart

**This screen departs:**

- After "**get ready to answer**" is displayed for some frames.

Play then proceeds to **Screen 06 — Answer Input** for that player's response;
when the last player has answered, results are revealed on **Screen 05**, and the
game returns to **Screen 00**.

## Design notes

- This screen is similar to **Screen 07** in many ways: it uses a bordered
  full-screen layout and presents a lot of text information.
- It is the **only other screen with a Press Start prompt**, like **Screen 01**.

> **ROM correlation:** the Press Start prompt is the same controller-poll +
> frame-gate idiom as Screen 01 (`JOY1 $4016`). The shared bordered-text layout
> with Screen 07 again points at handler reuse in the `$6E`/`$8901` state machine.
