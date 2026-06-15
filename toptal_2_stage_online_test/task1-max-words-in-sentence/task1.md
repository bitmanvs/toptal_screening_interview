# Task 1 — Maximum Words in a Sentence

## Problem

Given text `S`, split into sentences on `.`, `?`, `!`. Split each sentence into tokens on spaces. A **word** is a token with at least one letter (`a`–`z` or `A`–`Z`). Empty sentences are allowed (0 words). Return the maximum word count over all sentences.

## Examples

| Input | Max words | Why |
|-------|-----------|-----|
| `we test coders. Give us a try?` | 4 | Sentences: 3, 4, 0 words |
| `Forget CVS..Ah! Now I can...` style | 2 | Multiple sentences; several have 2 words |

## Approach

1. Scan `S` left to right, building the current sentence buffer.
2. On `.`, `?`, or `!`, evaluate the buffer as one sentence, then clear it.
3. After the loop, evaluate the trailing buffer (text after the last delimiter, or whole string if none).
4. For each sentence: `split()` on spaces; count tokens where `any(c.isalpha() for c in word)`.
5. Return the maximum count.

## Files

- `solution.py` — `solution(S)` entry point and `count_words` helper.

## Complexity

- Time: O(N) over string length (one pass + word checks per sentence).
- Space: O(N) for the current sentence buffer in the worst case.

## Edge cases

- Consecutive delimiters (`..`) → empty sentence, 0 words.
- Punctuation-only tokens (no letters) → not counted as words.
- Sentence with only spaces → 0 words.
- No delimiters → entire string is one sentence.
