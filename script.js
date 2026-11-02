// Budget Tracker (web version) — same rules as budget_tracker.py.
// Income = payroll + cash tips. Spending counts against the limit.
// Transfer = moves of your own money (e.g. your own Cash App) — ignored.

const STARTER = [
  { date: "2026-11-01", description: "Cash tip deposit", type: "Income", category: "Tips", amount: 77 },
  { date: "2026-11-01", description: "Emergent", type: "Spending", category: "Software / AI tools", amount: 1 },
  { date: "2026-11-01", description: "Move to own Cash App", type: "Transfer", category: "Own transfer", amount: 27.87 },
];

const STORAGE_KEY = "budget-tracker-rows-v1";
const SETTINGS_KEY = "budget-tracker-settings-v1";

function loadRows() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch (e) { /* fall through to starter */ }
  return [...STARTER];
}

function saveRows() {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(rows)); } catch (e) {}
}

let rows = loadRows();

const els = {
  limit: document.getElementById("limit"),
  rent: document.getElementById("rent"),
  income: document.getElementById("statIncome"),
  spending: document.getElementById("statSpending"),
  remaining: document.getElementById("statRemaining"),
  rentStat: document.getElementById("statRent"),
  summaryLine: document.getElementById("summaryLine"),
  biggestLine: document.getElementById("biggestLine"),
  categoryList: document.getElementById("categoryList"),
  txBody: document.getElementById("txBody"),
};

function money(v) {
  return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function summarize() {
  const limit = parseFloat(els.limit.value) || 0;
  const rent = parseFloat(els.rent.value) || 0;
  let income = 0, spending = 0, ignored = 0;
  const byCategory = {};
  for (const r of rows) {
    if (r.type === "Income") income += r.amount;
    else if (r.type === "Spending") {
      spending += r.amount;
      byCategory[r.category || "Uncategorized"] = (byCategory[r.category || "Uncategorized"] || 0) + r.amount;
    } else if (r.type === "Transfer") ignored += 1;
  }
  const categories = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);
  return {
    limit, rent, income, spending, ignored, categories,
    remaining: limit - spending,
    pct: limit ? (spending / limit) * 100 : 0,
    rentNeeded: Math.max(0, rent - income),
    rentCovered: income >= rent,
  };
}

function render() {
  const s = summarize();
  els.income.textContent = money(s.income);
  els.spending.textContent = money(s.spending);
  els.remaining.textContent = money(s.remaining);
  els.remaining.className = s.remaining >= 0 ? "good" : "bad";
  els.rentStat.textContent = money(s.rentNeeded);
  els.summaryLine.textContent =
    `${money(s.spending)} of ${money(s.limit)} spent (${s.pct.toFixed(1)}% used) · ` +
    (s.rentCovered ? "Rent set-aside is covered." : `Rent not covered yet — ${money(s.rentNeeded)} to go.`) +
    (s.ignored ? ` · ${s.ignored} transfer row(s) ignored (your own money moving).` : "");
  els.biggestLine.textContent = s.categories.length
    ? `Biggest category: ${s.categories[0][0]} (${money(s.categories[0][1])})`
    : "No spending recorded yet.";
  els.categoryList.innerHTML = s.categories
    .map(([name, total]) => `<span class="chip">${name}: ${money(total)}</span>`)
    .join("");

  els.txBody.innerHTML = "";
  rows.forEach((r, i) => {
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td>${r.date}</td><td></td><td>${r.type}</td><td></td><td class="amount">${money(r.amount)}</td>`;
    tr.children[1].textContent = r.description;
    tr.children[3].textContent = r.category;
    const td = document.createElement("td");
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "delete-btn";
    btn.textContent = "Delete";
    btn.addEventListener("click", () => { rows.splice(i, 1); saveRows(); render(); });
    td.appendChild(btn);
    tr.appendChild(td);
    els.txBody.appendChild(tr);
  });
}

document.getElementById("addBtn").addEventListener("click", () => {
  const amount = parseFloat(document.getElementById("fAmount").value);
  const description = document.getElementById("fDesc").value.trim();
  if (!description || !Number.isFinite(amount)) {
    alert("Enter a description and an amount.");
    return;
  }
  rows.push({
    date: document.getElementById("fDate").value || "2026-11-01",
    description,
    type: document.getElementById("fType").value,
    category: document.getElementById("fCategory").value.trim() || "Uncategorized",
    amount,
  });
  saveRows();
  render();
});

document.getElementById("resetBtn").addEventListener("click", () => {
  rows = [...STARTER];
  saveRows();
  render();
});

document.getElementById("exportBtn").addEventListener("click", () => {
  const lines = ["date,description,type,category,amount"];
  for (const r of rows) {
    const esc = (v) => `"${String(v).replaceAll('"', '""')}"`;
    lines.push([r.date, esc(r.description), r.type, esc(r.category), r.amount.toFixed(2)].join(","));
  }
  const blob = new Blob([lines.join("\n")], { type: "text/csv" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "transactions.csv";
  a.click();
  URL.revokeObjectURL(a.href);
});

document.getElementById("csvFile").addEventListener("change", (event) => {
  const file = event.target.files[0];
  if (!file) return;
  file.text().then((text) => {
    const lines = text.trim().split(/\r?\n/);
    const parsed = [];
    for (const line of lines.slice(1)) {
      if (!line.trim()) continue;
      const parts = line.split(",");
      if (parts.length < 5) continue;
      const amount = parseFloat(parts[parts.length - 1]);
      if (!Number.isFinite(amount)) continue;
      parsed.push({
        date: parts[0].trim(),
        description: parts[1].trim(),
        type: parts[2].trim(),
        category: parts[3].trim(),
        amount,
      });
    }
    if (parsed.length) { rows = parsed; saveRows(); render(); }
    else alert("No valid rows found in that CSV.");
  });
});

[els.limit, els.rent].forEach((el) => {
  try {
    const saved = JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}");
    if (saved.limit) els.limit.value = saved.limit;
    if (saved.rent) els.rent.value = saved.rent;
  } catch (e) {}
  el.addEventListener("input", () => {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify({ limit: els.limit.value, rent: els.rent.value }));
    } catch (e) {}
    render();
  });
});

render();
