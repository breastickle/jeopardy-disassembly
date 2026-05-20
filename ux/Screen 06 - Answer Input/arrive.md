# Screen 06 — Answer Input · Arrive

**This screen is shown:**

- Some frames after **Screen 05** shows which player rang in.
- After **Screen 08**'s "Player N, get ready to answer".
- After a Daily Double wager is completed in **Screen 07**.

With the same sound effect for the timer counting down.

> **ROM correlation:** the response is entered with the UI text codec
> (`tile = char − $2C`, bit-7 terminator; see [`../../docs/text-format.md`](../../docs/text-format.md)),
> the same alphabet used for name entry on Screen 02. The countdown rides the frame
> counter `$01`. Note this is a **human-input** screen: a CPU that buzzes is
> resolved as correct without typing, so the CPUs generally bypass Screen 06.
