// you can write to stdout for debugging purposes, e.g.
// console.log('this is a debug message');

function solution(A) {
    const dominoes = [];
    for (let i = 0; i < 12; i += 2) {
        dominoes.push([A[i], A[i + 1]]);
    }

    // Pyramid layout (indices into placed[]):
    //          [0]
    //        [1] [2]
    //      [3] [4] [5]
    //
    // Each domino half above must equal the half directly below it:
    //   placed[0][0] == placed[1][1]   (top-left  == mid-left-right)
    //   placed[0][1] == placed[2][0]   (top-right == mid-right-left)
    //   placed[1][0] == placed[3][1]   (mid-left-left  == bot-left-right)
    //   placed[1][1] == placed[4][0]   (mid-left-right == bot-mid-left)
    //   placed[2][0] == placed[4][1]   (mid-right-left == bot-mid-right)
    //   placed[2][1] == placed[5][0]   (mid-right-right == bot-right-left)

    const used = new Array(6).fill(false);
    const placed = new Array(6);

    function valid(pos) {
        if (pos === 0) return true;
        if (pos === 1) return placed[0][0] === placed[1][1];
        if (pos === 2) return placed[0][1] === placed[2][0];
        if (pos === 3) return placed[1][0] === placed[3][1];
        if (pos === 4) return placed[1][1] === placed[4][0] && placed[2][0] === placed[4][1];
        if (pos === 5) return placed[2][1] === placed[5][0];
        return true;
    }

    function solve(pos) {
        if (pos > 0 && !valid(pos - 1)) return false;
        if (pos === 6) return true;

        for (let i = 0; i < 6; i++) {
            if (used[i]) continue;
            used[i] = true;

            placed[pos] = dominoes[i];
            if (solve(pos + 1)) return true;

            if (dominoes[i][0] !== dominoes[i][1]) {
                placed[pos] = [dominoes[i][1], dominoes[i][0]];
                if (solve(pos + 1)) return true;
            }

            used[i] = false;
        }

        return false;
    }

    return solve(0) ? "YES" : "NO";
}

module.exports = solution;
