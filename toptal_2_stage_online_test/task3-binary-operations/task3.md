# Task 3 — Binary Reduction Operations

## Problem

Binary string `S` (big-endian) encodes `V`. Repeat until `V = 0`:

- `V` odd → subtract 1
- `V` even → divide by 2

Return the number of operations.

## Examples

| S | V | Answer |
|---|-----|--------|
| `011100` | 28 | 7 |
| `111` | 7 | 5 |
| `1` × 400000 | huge | 799999 |

## Idea

Strip leading zeros (they do not change `V`). Scan from least significant bit to the bit before the MSB:

- Each position costs at least one divide (shift right).
- A `1` at that position also needs one subtract (carry/borrow before divides clear lower bits).

Add one final step for the remaining MSB.

## Algorithm

1. `S = S.lstrip('0')` or `'0'`.
2. If `S == '0'`, return `0`.
3. For `i` from `len(S)-1` down to `1`: `ops += 1`; if `S[i] == '1'`, `ops += 1`.
4. Return `ops + 1`.

## Why it works

Right-to-left, each bit index matches how many halvings happen after lower bits are cleared; each `1` (except handled by MSB finale) forces one extra odd subtract in that column. The MSB contributes exactly one more operation (`+1`).

## Complexity

- Time: O(N)
- Space: O(N) for the stripped string (can be O(1) with index scan only; current code is fine for N ≤ 400000).

## Files

- `solution.py` — `solution(S)`

## Edge cases

- `S = "0"` or all zeros → `0`
- `S = "1"` → `1`
- Leading zeros → ignored
