# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")

def solution(S):
    stripped = S.lstrip('0')
    if not stripped:
        return 0
    length = len(stripped)
    ones = stripped.count('1')
    return length + ones - 1
