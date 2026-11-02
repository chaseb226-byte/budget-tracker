#!/usr/bin/env python3
"""Budget Tracker — a basic Python budget summary tool.

Reads a CSV of transactions and totals one month against:
  - a monthly spending limit (default $1,600)
  - a rent set-aside that must be covered first (default $600)

Rules (the same ones Dakota uses in the Google Sheets tracker):
  - Type "Income" counts as income. That is Grease Monkey payroll plus
    cash tip deposits.
  - Type "Spending" counts against the spending limit.
  - Type "Transfer" is ignored — those are moves of your own money,
    like transfers to/from your own Cash App account. They are not
    income and not spending.

CSV format (with header):
  date,description,type,category,amount
  2026-11-01,Cash tip deposit,Income,Tips,77

Usage:
  python3 budget_tracker.py transactions.csv
  python3 budget_tracker.py transactions.csv --month 2026-11
  python3 budget_tracker.py transactions.csv --limit 1600 --rent 600
"""

import argparse
import csv
import sys
from collections import defaultdict
from datetime import date


def load_transactions(path):
    """Read the CSV and return a list of transaction dicts."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"date", "description", "type", "category", "amount"}
        if reader.fieldnames is None or not required.issubset(
            {h.strip().lower() for h in reader.fieldnames}
        ):
            raise ValueError(
                "CSV must have a header with: date, description, type, category, amount"
            )
        for line_no, raw in enumerate(reader, start=2):
            # Normalize keys to lowercase so "Date" and "date" both work.
            row = {k.strip().lower(): (v or "").strip() for k, v in raw.items()}
            try:
                row["amount"] = float(row["amount"])
                row["date"] = date.fromisoformat(row["date"])
            except ValueError:
                raise ValueError(f"Bad date or amount on line {line_no}: {raw}")
            row["type"] = row["type"].capitalize()
            rows.append(row)
    return rows


def summarize(rows, month=None, limit=1600.0, rent=600.0):
    """Total one month (YYYY-MM, or all rows if month is None)."""
    income = 0.0
    spending = 0.0
    ignored_transfers = 0
    by_category = defaultdict(float)

    for row in rows:
        if month and row["date"].strftime("%Y-%m") != month:
            continue
        if row["type"] == "Income":
            income += row["amount"]
        elif row["type"] == "Spending":
            spending += row["amount"]
            by_category[row["category"] or "Uncategorized"] += row["amount"]
        elif row["type"] == "Transfer":
            ignored_transfers += 1
        else:
            raise ValueError(f"Unknown type {row['type']!r} — use Income, Spending, or Transfer")

    biggest = None
    if by_category:
        biggest = max(by_category.items(), key=lambda kv: kv[1])

    return {
        "month": month or "all dates",
        "income": income,
        "spending": spending,
        "limit": limit,
        "remaining": limit - spending,
        "pct_used": (spending / limit * 100) if limit else 0.0,
        "rent": rent,
        "rent_covered": income >= rent,
        "rent_still_needed": max(0.0, rent - income),
        "biggest_category": biggest,
        "by_category": dict(sorted(by_category.items(), key=lambda kv: -kv[1])),
        "ignored_transfers": ignored_transfers,
    }


def format_summary(s):
    lines = [
        f"Budget summary — {s['month']}",
        f"  Income (payroll + tips): ${s['income']:,.2f}",
        f"  Spending:                ${s['spending']:,.2f} of ${s['limit']:,.2f} limit",
        f"  Remaining allowance:     ${s['remaining']:,.2f} ({s['pct_used']:.1f}% used)",
        "",
        f"  Rent set-aside:          ${s['rent']:,.2f}",
    ]
    if s["rent_covered"]:
        lines.append("  Rent covered?            Yes")
    else:
        lines.append(f"  Rent covered?            Not yet — ${s['rent_still_needed']:,.2f} still needed")
    lines.append("")
    if s["biggest_category"]:
        name, total = s["biggest_category"]
        lines.append(f"  Biggest category:        {name} (${total:,.2f})")
        lines.append("  Spending by category:")
        for name, total in s["by_category"].items():
            lines.append(f"    - {name}: ${total:,.2f}")
    else:
        lines.append("  No spending recorded for this period.")
    if s["ignored_transfers"]:
        lines.append("")
        lines.append(
            f"  Ignored {s['ignored_transfers']} transfer row(s) — moves of your own money, not income or spending."
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Summarize a month of spending against a limit.")
    parser.add_argument("csv_file", help="Path to the transactions CSV")
    parser.add_argument("--month", help="Month to summarize, YYYY-MM (default: all rows)")
    parser.add_argument("--limit", type=float, default=1600.0, help="Monthly spending limit (default 1600)")
    parser.add_argument("--rent", type=float, default=600.0, help="Rent set-aside (default 600)")
    args = parser.parse_args(argv)

    try:
        rows = load_transactions(args.csv_file)
        summary = summarize(rows, month=args.month, limit=args.limit, rent=args.rent)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
