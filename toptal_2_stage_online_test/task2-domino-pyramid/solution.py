def solution(A):
    dom = [(A[i], A[i + 1]) for i in range(0, 12, 2)]
    slots = [(0, 1), (1, 2), (2, 3), (2, 3), (3, 4), (4, 5)]
    used = [False] * 6
    values = {}

    def go(pos):
        if pos == 6:
            return len(values) == 6
        left, right = slots[pos]
        for idx in range(6):
            if used[idx]:
                continue
            u, v = dom[idx]
            for a, b in ((u, v), (v, u)):
                if left in values and values[left] != a:
                    continue
                if right in values and values[right] != b:
                    continue
                backup = dict(values)
                values[left] = a
                values[right] = b
                used[idx] = True
                if go(pos + 1):
                    return True
                used[idx] = False
                values.clear()
                values.update(backup)
        return False

    return "YES" if go(0) else "NO"
