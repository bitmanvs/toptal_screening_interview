import { readFileSync } from "fs";

const orders = JSON.parse(readFileSync("data/orders.json", "utf8"));

const total = (o) => o.order_items.reduce((s, i) => s + i.quantity * i.unit_price, 0);

// 3
const sellers = {};
orders.forEach((o) => (sellers[o.seller_id] = (sellers[o.seller_id] || 0) + total(o)));
Object.entries(sellers)
  .sort((a, b) => b[1] - a[1])
  .forEach(([id, t]) => console.log(id, t.toFixed(2)));

console.log();

// 4
const days = {};
orders.forEach((o) => {
  const d = o.created_at.slice(0, 10);
  days[d] = (days[d] || 0) + total(o);
});
Object.entries(days)
  .sort((a, b) => a[0].localeCompare(b[0]))
  .forEach(([d, t]) => console.log(`${d}, ${t.toFixed(2)}`));

console.log();

// 5
[...orders]
  .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  .forEach((o) => console.log(o.order_number, o.created_at, o.customer_name, o.seller_name));

console.log();

// 6
const spend = {};
orders.forEach((o) => (spend[o.customer_id] = (spend[o.customer_id] || 0) + total(o)));
const vals = Object.values(spend);
console.log((vals.reduce((a, b) => a + b, 0) / vals.length).toFixed(2));
