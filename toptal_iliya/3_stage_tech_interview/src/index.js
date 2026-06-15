import { fileURLToPath } from "url";
import { dirname, join, resolve } from "path";
import { loadOrdersFromFile } from "./loadOrders.js";
import {
  formatSellerReport,
  formatDailyReport,
  formatOrdersList,
  averageAmountPerCustomer,
} from "./report.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const defaultDataPath = join(__dirname, "..", "data", "orders.json");

function parseArgs(argv) {
  let task = "all";
  let file = defaultDataPath;
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--task" || a === "-t") {
      task = argv[++i] ?? "all";
    } else if (a === "--file" || a === "-f") {
      file = argv[++i] ?? file;
    }
  }
  return { task: String(task).toLowerCase(), file: resolve(file) };
}

async function main() {
  const { task, file } = parseArgs(process.argv);
  const orders = await loadOrdersFromFile(file);

  const run = {
    "1": () => console.log(`read: ${orders.length} orders from ${file}`),
    "2": () => console.log(`parsed: ${orders.length} orders`),
    "3": () => console.log(formatSellerReport(orders)),
    "4": () => console.log(formatDailyReport(orders)),
    "5": () => console.log(formatOrdersList(orders)),
    "6": () =>
      console.log(averageAmountPerCustomer(orders).toFixed(2)),
    all: () => {
      run["1"]();
      run["2"]();
      console.log("");
      console.log("3) sellers (id, total desc)");
      run["3"]();
      console.log("");
      console.log("4) daily totals UTC");
      run["4"]();
      console.log("");
      console.log("5) orders oldest first");
      run["5"]();
      console.log("");
      console.log("6) average per customer");
      run["6"]();
    },
  };

  const fn = run[task];
  if (!fn) {
    console.error(`Unknown task: ${task}`);
    process.exitCode = 1;
    return;
  }
  fn();
}

main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
