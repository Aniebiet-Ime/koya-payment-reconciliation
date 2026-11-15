#!/usr/bin/env python3
"""Reconcile payment events using the latest attempt for each transaction.

Run from the directory containing payments.jsonl and expected.txt:
    python3 reconcile.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP

latest_by_txn = {}

with open("payments.jsonl", "r", encoding="utf-8") as payments_file:
    for line in payments_file:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, TypeError):
            # The export may contain unreadable lines.
            continue

        if not isinstance(event, dict):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            # Events without a transaction ID cannot be reconciled.
            continue

        existing = latest_by_txn.get(txn_id)

        # Timestamps in this export are consistently formatted UTC ISO-8601
        # strings, so lexical comparison preserves chronological order.
        if existing is None or event["ts"] > existing["ts"]:
            latest_by_txn[txn_id] = event

total = Decimal("0")
count = 0

for event in latest_by_txn.values():
    if event.get("status") == "success":
        count += 1
        raw_amount = event["amount"]
        amount = Decimal(str(raw_amount).replace(",", "").strip())
        total += amount

with open("expected.txt", "r", encoding="utf-8") as expected_file:
    expected = int(expected_file.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    rounded_total = total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{rounded_total}")
