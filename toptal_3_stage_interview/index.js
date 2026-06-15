const JSON_URL = "https://topt.a1/r6cvQM";

async function loadDietRecords() {
  const response = await fetch(JSON_URL);
  return await response.json();
}

function getDate(record) {
  return record.date_consumed ?? record["date consumed"];
}

function getTime(record) {
  return record.time_consumed ?? record["time consumed"];
}

function getRecordsInDateRange(records, startDate, endDate) {
  return records.filter((record) => {
    const date = getDate(record);
    return date >= startDate && date <= endDate;
  });
}

function calculateTotalExpenditure(records, startDate, endDate) {
  const total = getRecordsInDateRange(records, startDate, endDate).reduce(
    (sum, record) => sum + Number(record.price),
    0
  );
  return total.toFixed(2);
}

function calculateAverageExpenditure(records, startDate, endDate) {
  const recordsInRange = getRecordsInDateRange(records, startDate, endDate);
  if (recordsInRange.length === 0) return "0.00";
  const total = recordsInRange.reduce(
    (sum, record) => sum + Number(record.price),
    0
  );
  return (total / recordsInRange.length).toFixed(2);
}

function findTopDishesByNutrients(records) {
  const totalsByDish = {};
  for (const record of records) {
    const name = record.name;
    if (!totalsByDish[name]) {
      totalsByDish[name] = { carbs: 0, fats: 0, proteins: 0 };
    }
    totalsByDish[name].carbs += Number(record.carbs);
    totalsByDish[name].fats += Number(record.fat);
    totalsByDish[name].proteins += Number(record.protein);
  }

  const findMaxDish = (nutrientKey) => {
    let topName = null;
    let topAmount = -Infinity;
    for (const [name, totals] of Object.entries(totalsByDish)) {
      if (totals[nutrientKey] > topAmount) {
        topAmount = totals[nutrientKey];
        topName = name;
      }
    }
    return `${topName} - total ${nutrientKey}: ${topAmount.toFixed(2)}g`;
  };

  return [findMaxDish("carbs"), findMaxDish("fats"), findMaxDish("proteins")];
}

function findMostCommonDishesInTimeRange(records, startTime, endTime) {
  const countByDish = {};
  for (const record of records) {
    const time = getTime(record);
    if (time >= startTime && time <= endTime) {
      countByDish[record.name] = (countByDish[record.name] ?? 0) + 1;
    }
  }
  return Object.entries(countByDish)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([name, count]) => `${name} - ${count}`);
}

async function runAll() {
  const records = await loadDietRecords();

  console.log("Requirement 2:");
  console.log(
    "Total:",
    calculateTotalExpenditure(records, "2022-12-01", "2022-12-04")
  );
  console.log(
    "Average:",
    calculateAverageExpenditure(records, "2022-12-01", "2022-12-04")
  );

  console.log("\nRequirement 3:");
  findTopDishesByNutrients(records).forEach((line) => console.log(line));

  console.log("\nRequirement 4:");
  findMostCommonDishesInTimeRange(records, "09:00", "14:00").forEach((line) =>
    console.log(line)
  );
}

runAll();

export {
  loadDietRecords,
  calculateTotalExpenditure,
  calculateAverageExpenditure,
  findTopDishesByNutrients,
  findMostCommonDishesInTimeRange,
};
