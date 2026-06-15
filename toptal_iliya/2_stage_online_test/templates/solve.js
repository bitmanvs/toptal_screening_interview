/**
 * Local practice template — Node stdin/stdout.
 * Many online judges pipe input; this reads all stdin then parses.
 * Replace parse/solve for your problem shape.
 */

const readline = require("readline");

function solve(lines) {
  // Example placeholder — replace with real parsing + logic
  const t = Number(lines[0]);
  const out = [];
  let i = 1;
  for (let k = 0; k < t; k += 1) {
    const n = Number(lines[i++]);
    out.push(String(n * 2));
  }
  return out.join("\n");
}

async function main() {
  const lines = [];
  const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of rl) {
    lines.push(line);
  }
  while (lines.length && lines[lines.length - 1] === "") lines.pop();
  process.stdout.write(solve(lines));
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
