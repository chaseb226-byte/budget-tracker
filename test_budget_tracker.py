#!/usr/bin/env python3
"""Tests for budget_tracker.py — run with: python3 -m unittest -v"""

import os
import tempfile
import unittest

from budget_tracker import load_transactions, summarize

HEADER = "date,description,type,category,amount\n"


def write_csv(text):
    f = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, encoding="utf-8"
    )
    f.write(text)
    f.close()
    return f.name


class BudgetTrackerTests(unittest.TestCase):
    def load(self, body):
        path = write_csv(HEADER + body)
        self.addCleanup(os.unlink, path)
        return load_transactions(path)

    def test_november_starter_matches_sheet_tracker(self):
        rows = self.load(
            "2026-11-01,Cash tip deposit,Income,Tips,77\n"
            "2026-11-01,Emergent,Spending,Software / AI tools,1\n"
            "2026-11-01,Move to own Cash App,Transfer,Own transfer,27.87\n"
        )
        s = summarize(rows, month="2026-11")
        self.assertEqual(s["income"], 77)
        self.assertEqual(s["spending"], 1)
        self.assertEqual(s["remaining"], 1599)
        self.assertEqual(s["rent_still_needed"], 523)
        self.assertFalse(s["rent_covered"])
        self.assertEqual(s["ignored_transfers"], 1)

    def test_transfers_are_not_income_or_spending(self):
        rows = self.load(
            "2026-11-01,Paycheck,Income,Payroll,800\n"
            "2026-11-02,To Cash App,Transfer,Own transfer,200\n"
            "2026-11-03,From Cash App,Transfer,Own transfer,50\n"
        )
        s = summarize(rows, month="2026-11")
        self.assertEqual(s["income"], 800)
        self.assertEqual(s["spending"], 0)
        self.assertTrue(s["rent_covered"])

    def test_month_filter_and_biggest_category(self):
        rows = self.load(
            "2026-10-31,Old paycheck,Income,Payroll,900\n"
            "2026-11-03,Groceries,Spending,Food and drink,120.50\n"
            "2026-11-04,Gas,Spending,Transport,45\n"
        )
        s = summarize(rows, month="2026-11")
        self.assertEqual(s["income"], 0)
        self.assertEqual(s["spending"], 165.50)
        self.assertEqual(s["biggest_category"][0], "Food and drink")

    def test_unknown_type_is_an_error(self):
        rows = self.load("2026-11-01,Mystery,Other,Misc,10\n")
        with self.assertRaises(ValueError):
            summarize(rows, month="2026-11")


if __name__ == "__main__":
    unittest.main()
