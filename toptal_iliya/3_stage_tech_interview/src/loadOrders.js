import fs from "fs/promises";

/**
 * @param {string} filePath
 */
export async function loadOrdersFromFile(filePath) {
  const text = await fs.readFile(filePath, "utf8");
  return parseOrdersJson(text);
}

/**
 * @param {string} jsonText
 */
export function parseOrdersJson(jsonText) {
  const data = JSON.parse(jsonText);
  if (!Array.isArray(data)) {
    throw new Error("Expected a JSON array of orders");
  }
  return data;
}
