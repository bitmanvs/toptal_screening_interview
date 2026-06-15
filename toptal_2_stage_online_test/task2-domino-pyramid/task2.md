# Task 2 — Domino Pyramid

## Problem

Six dominoes (12 integers in `A`, pairs per domino). Build a 3-level pyramid: 3 bottom, 2 middle, 1 top, centered. Each domino may be flipped. Vertically adjacent halves must show the same spot count (not horizontal neighbors).

Return `"YES"` or `"NO"`.

## Pyramid layout

Six positions (bottom-left, middle-left, bottom-center, top, middle-right, bottom-right) with six shared values `v0…v5`:

| Slot | Domino | Oriented pair |
|------|--------|---------------|
| 0 | bottom-left | `(v0, v1)` |
| 1 | middle-left | `(v1, v2)` |
| 2 | bottom-center | `(v2, v3)` |
| 3 | top | `(v2, v3)` |
| 4 | middle-right | `(v3, v4)` |
| 5 | bottom-right | `(v4, v5)` |

Top and bottom-center both use `(v2, v3)` on different physical dominoes. Middle-right uses `(v3, v4)` (not a repeat of top’s right alone as a new chain step).

## Approach

1. Parse six dominoes from `A`.
2. Try every permutation into slots and every flip mask (`6! × 2^6`).
3. For each slot, enforce the oriented pair for indices `(i, j)` in `SLOTS`; reuse already-fixed `vi`, `vj` when the same index appears again.
4. Success when all six values are consistent → `"YES"`.

## Files

- `solution.py` — `solution(A)`.

## Complexity

- Time: O(6! × 2^6) ≈ 46k checks per test — fine for N=6.
- Space: O(1) aside from input.

## Example

`A = [4,3,3,4,1,2,2,3,6,5,4,5]` → rotate/use dominoes as `(3,4),(3,4),(1,2),(2,3),(5,6),(4,5)` on the spine → `"YES"`.
