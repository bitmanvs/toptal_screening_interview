/**
 * @param {import('./types.js').Order} order
 */
export function orderTotal(order) {
  return order.order_items.reduce(
    (sum, item) => sum + item.quantity * item.unit_price,
    0
  );
}

/**
 * @param {number} n
 */
export function money2(n) {
  return Math.round(n * 100) / 100;
}

/**
 * @param {import('./types.js').Order[]} orders
 * @returns {{ seller_id: number; total: number }[]}
 */
export function sellerTotalsDescending(orders) {
  const bySeller = new Map();
  for (const o of orders) {
    const id = o.seller_id;
    bySeller.set(id, (bySeller.get(id) ?? 0) + orderTotal(o));
  }
  return [...bySeller.entries()]
    .map(([seller_id, total]) => ({ seller_id, total: money2(total) }))
    .sort((a, b) => b.total - a.total);
}

/**
 * @param {import('./types.js').Order[]} orders
 * @returns {{ date: string; amount: number }[]}
 */
export function dailyTotalsChronological(orders) {
  const byDay = new Map();
  for (const o of orders) {
    const date = utcDateKey(o.created_at);
    byDay.set(date, (byDay.get(date) ?? 0) + orderTotal(o));
  }
  return [...byDay.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([date, amount]) => ({ date, amount: money2(amount) }));
}

/**
 * @param {string} isoUtc
 */
export function utcDateKey(isoUtc) {
  return isoUtc.slice(0, 10);
}

/**
 * @param {import('./types.js').Order[]} orders
 */
export function ordersOldestFirst(orders) {
  return [...orders].sort(
    (a, b) => Date.parse(a.created_at) - Date.parse(b.created_at)
  );
}

/**
 * Average total spend per distinct customer_id (sum of order totals / unique customers).
 * @param {import('./types.js').Order[]} orders
 */
export function averageAmountPerCustomer(orders) {
  const spend = new Map();
  for (const o of orders) {
    const id = o.customer_id;
    spend.set(id, (spend.get(id) ?? 0) + orderTotal(o));
  }
  const sum = [...spend.values()].reduce((a, b) => a + b, 0);
  return money2(sum / spend.size);
}

/**
 * @param {import('./types.js').Order[]} orders
 */
export function formatSellerReport(orders) {
  return sellerTotalsDescending(orders)
    .map((r) => `${r.seller_id}\t${r.total.toFixed(2)}`)
    .join("\n");
}

/**
 * @param {import('./types.js').Order[]} orders
 */
export function formatDailyReport(orders) {
  return dailyTotalsChronological(orders)
    .map((r) => `${r.date}, ${r.amount.toFixed(2)}`)
    .join("\n");
}

/**
 * @param {import('./types.js').Order[]} orders
 */
export function formatOrdersList(orders) {
  const sorted = ordersOldestFirst(orders);
  return sorted
    .map(
      (o) =>
        `${o.order_number}\t${o.created_at}\t${o.customer_name}\t${o.seller_name}`
    )
    .join("\n");
}
