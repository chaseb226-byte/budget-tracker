# Budget Tracker (Python)

A basic, no-dependencies Python budget tool built by Dakota Beerbower.
My third GitHub project — the code version of my Google Sheets budget tracker.

It reads a CSV of transactions and totals a month against:

- **$1,600 monthly spending limit**
- **$600 rent set-aside, covered first**

## Live web version

**https://chaseb226-byte.github.io/budget-tracker/**

The same rules in the browser (`index.html` / `styles.css` / `script.js`):
add transactions, import/export CSV, and watch the totals, rent coverage,
and biggest category update live. Rows are saved only in your own browser
on your own device — nothing is uploaded anywhere.

## Rules

| Type in the CSV | How it counts |
| --- | --- |
| `Income` | Income — Grease Monkey payroll + cash tip deposits |
| `Spending` | Counts against the $1,600 limit |
| `Transfer` | Ignored — moves of your own money, like transfers to/from your own Cash App. Not income, not spending. |

## Files

- `budget_tracker.py` — the Python tool
- `index.html`, `styles.css`, `script.js` — the live web version (GitHub Pages)
- `transactions.csv` — my real November 2026 starter rows (matches the Sheets tracker)
- `sample_transactions.csv` — made-up example data to try it with
- `test_budget_tracker.py` — tests, run with `python3 -m unittest -v`

## Run it

```bash
python3 budget_tracker.py transactions.csv --month 2026-11
python3 budget_tracker.py sample_transactions.csv --month 2026-11
python3 budget_tracker.py transactions.csv --limit 1600 --rent 600
```

## Example output

Running it on the real starter rows (`transactions.csv`):

```
Budget summary — 2026-11
  Income (payroll + tips): $77.00
  Spending:                $1.00 of $1,600.00 limit
  Remaining allowance:     $1,599.00 (0.1% used)

  Rent set-aside:          $600.00
  Rent covered?            Not yet — $523.00 still needed

  Biggest category:        Software / AI tools ($1.00)
  Spending by category:
    - Software / AI tools: $1.00

  Ignored 1 transfer row(s) — moves of your own money, not income or spending.
```

## CSV format

```csv
date,description,type,category,amount
2026-11-01,Cash tip deposit,Income,Tips,77
2026-11-01,Groceries,Spending,Food and drink,54.20
2026-11-02,Move to own Cash App,Transfer,Own transfer,50
```

## Author

Dakota Beerbower · https://github.com/chaseb226-byte
Other projects: [portfolio site](https://chaseb226-byte.github.io/portfolio-site/) ·
[trading checklist](https://chaseb226-byte.github.io/trading-checklist/)
