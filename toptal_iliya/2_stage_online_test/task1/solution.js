// you can write to stdout for debugging purposes, e.g.
// console.log('this is a debug message');

function solution(S) {
    const sentences = S.split(/[.?!]/);
    let max = 0;

    for (const sentence of sentences) {
        const words = sentence.split(" ").filter(w => /[a-zA-Z]/.test(w));
        if (words.length > max) {
            max = words.length;
        }
    }

    return max;
}

module.exports = solution;
