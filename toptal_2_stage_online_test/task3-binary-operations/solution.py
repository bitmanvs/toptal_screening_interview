def solution(S):
    S = S.lstrip("0") or "0"
    if S == "0":
        return 0
    ops = 0
    for i in range(len(S) - 1, 0, -1):
        ops += 1
        if S[i] == "1":
            ops += 1
    return ops + 1
