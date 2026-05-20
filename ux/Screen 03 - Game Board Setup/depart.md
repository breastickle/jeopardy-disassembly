# Screen 03 — Game Board Setup · Depart

**This screen departs:**

- After the in-control player selects a **category and dollar value**.

## Design notes

- Selection of a category is **non-reversible**.

> **ROM correlation:** the board cursor lives in the state handler at `$8DA2`
> (`State_BoardCursor`). The cursor's vertical position `$6A` is converted to the
> selected **row / difficulty** in `$9B` (`($6A − $58) >> 3`) — and that row *is*
> the dollar value, which is also what later indexes the CPU reaction-time table.
> See [`../../docs/ram-map.md`](../../docs/ram-map.md).
