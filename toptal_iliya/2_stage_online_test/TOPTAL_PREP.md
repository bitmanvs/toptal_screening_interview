# Toptal technical assessment — prep pack (JavaScript)

This folder is set up for **timed algorithm screens** (often 90–120 minutes, multiple problems on platforms like Codility/HackerRank-style UIs). Use it to rehearse the *workflow*, not to memorize answers.

**Language:** All practice solutions and templates here use **JavaScript (Node.js)** only.

## What to expect (typical flow)

1. **Online coding screen** — 2–4 problems; correctness first, then time/space if constraints are tight.
2. **Live technical** (later stage) — you explain while you code; clarity beats cleverness.
3. **Test project** (later) — real delivery, scope, and communication.

Assumptions change by role (frontend vs backend vs data). Adjust depth: e.g. more array/string/graph for general SWE; more DOM/perf for FE.

## Strategy under time pressure

- **Read end-to-end** — constraints, input size, edge cases (empty, single element, duplicates, overflow).
- **Verbalize a plan** — brute force O(n²) or extra memory is fine as a starting point if it passes small tests.
- **Implement → run examples → fix** — do not optimize before something works unless the bound is obviously tiny.
- **Name things clearly** — `left`, `right`, `prefix`, `graph`, `inDegree` — reviewers read this in live rounds.
- **Complexity** — state Big-O when you change approach; match constraint tables (e.g. n ≤ 10⁵ → aim for O(n log n) or O(n)).

## Topics worth refreshing (medium level)

| Area | Patterns |
|------|----------|
| Arrays / strings | Two pointers, sliding window, prefix sums |
| Hash maps / sets | Frequency, dedup, complement lookups (`Map`, `Set`) |
| Trees / graphs | BFS/DFS, topo sort, shortest path basics |
| Sorting / heaps | Custom sorts, k-th element, scheduling |
| DP | 1D/2D states, when greedy fails |
| Bit tricks | Sets of flags, XOR tricks (where applicable) |

Practice sources: LeetCode **Medium** (JavaScript), Codility lessons, HackerRank **Algorithms** medium.

## Day-of checklist

- [ ] Stable internet; **wired** if possible.
- [ ] Browser: one profile with **ad blockers disabled** for the test tab if the platform breaks.
- [ ] **Node.js** ready: `node --version` (LTS recommended).
- [ ] **Quiet block** on calendar; phone on silent; second monitor only if rules allow.
- [ ] Water; clock visible; know **how much time per problem** you will allocate before starting.
- [ ] Read platform rules: copy/paste, external resources, allowed languages (select **JavaScript**).

## Files in this pack

| Path | Purpose |
|------|---------|
| `templates/solve.js` | Node.js stdin/stdout stub for local drills |
| `scripts/env-check.ps1` | Quick Node/npm check on Windows |

## Quick local drill (15 minutes)

1. Pick one Medium problem on your practice site (JavaScript).
2. Solve using **`templates/solve.js`** I/O style (stdin → stdout): `node templates/solve.js < input.txt`.
3. Time yourself; after, note **what slowed you down** (reading spec, edge cases, syntax).

Good luck — preparation is mostly **reps + calm execution**.
