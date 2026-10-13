#!/usr/bin/env python3
"""Audit an order CSV without changing the source or guessing conflicted values."""
import argparse
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import sys

REQUIRED = ("order_id", "date", "channel", "amount", "currency", "status")


def read_orders(source):
    rows = []
    with source.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not set(REQUIRED).issubset(fields):
            raise ValueError("CSV must have unique headers including " + ", ".join(REQUIRED))
        for raw in reader:
            if None in raw or any(value is None for value in raw.values()):
                raise ValueError(f"Malformed CSV row ending at line {reader.line_num}")
            rows.append({"raw": raw, "row_number": reader.line_num,
                         "source_id": f"{raw['order_id']}@{source.name}:{reader.line_num}"})
    return fields, rows


def audit(source):
    fields, rows = read_orders(source)
    unique, seen, duplicates, issues = [], {}, [], []
    for row in rows:
        signature = tuple(row["raw"][field] for field in fields)
        if signature in seen:
            duplicates.append({"order_id": row["raw"]["order_id"],
                               "kept_source_id": seen[signature]["source_id"],
                               "duplicate_source_id": row["source_id"]})
        else:
            seen[signature] = row
            unique.append(row)
    groups = {}
    for row in unique:
        groups.setdefault(row["raw"]["order_id"], []).append(row)
    conflicts, conflict_ids = [], set()
    for order_id, group in groups.items():
        if len(group) > 1:
            differing = [field for field in fields if len({r["raw"][field] for r in group}) > 1]
            conflicts.append({"order_id": order_id, "source_ids": [r["source_id"] for r in group],
                              "differing_fields": differing,
                              "rows": [{"source_id": r["source_id"], "values": r["raw"]} for r in group]})
            conflict_ids.add(order_id)
    cleaned, totals = [], {}
    for row in unique:
        raw, row_number, source_id = row["raw"], row["row_number"], row["source_id"]
        valid = True

        def issue(code, field, value, blocks=True):
            nonlocal valid
            issues.append({"source_id": source_id, "order_id": raw["order_id"],
                           "row_number": row_number, "code": code, "field": field, "value": value})
            if blocks:
                valid = False

        if not raw["order_id"].strip():
            issue("missing_order_id", "order_id", raw["order_id"])
        if raw["order_id"] in conflict_ids:
            issue("order_conflict", "order_id", raw["order_id"])
        normalized_date = None
        try:
            text = raw["date"].strip()
            if not re.fullmatch(r"\d{4}[-/]\d{2}[-/]\d{2}", text):
                raise ValueError("unsupported date format")
            normalized_date = date.fromisoformat(text.replace("/", "-")).isoformat()
            if normalized_date != raw["date"]:
                issue("normalized_date", "date", raw["date"], blocks=False)
        except ValueError:
            issue("invalid_date", "date", raw["date"])
        amount = None
        if not raw["amount"].strip():
            issue("missing_amount", "amount", raw["amount"])
        else:
            try:
                amount = Decimal(raw["amount"].strip())
                if not amount.is_finite():
                    raise InvalidOperation
            except InvalidOperation:
                issue("invalid_amount", "amount", raw["amount"])
        currency = raw["currency"].strip().upper()
        if not re.fullmatch(r"[A-Z]{3}", currency):
            issue("invalid_currency", "currency", raw["currency"])
        if raw["status"].strip().lower() != "paid":
            issue("not_paid", "status", raw["status"])
        if not valid:
            continue
        cleaned_row = dict(raw)
        cleaned_row.update(date=normalized_date, amount=format(amount, "f"), currency=currency,
                           source_id=source_id, row_number=row_number)
        cleaned.append(cleaned_row)
        aggregate = totals.setdefault(currency, {"currency": currency, "amount": Decimal(0),
                                                "order_count": 0, "source_ids": []})
        aggregate["amount"] += amount
        aggregate["order_count"] += 1
        aggregate["source_ids"].append(source_id)
    aggregates = []
    for currency in sorted(totals):
        aggregate = totals[currency]
        aggregate["amount"] = float(aggregate["amount"])
        aggregates.append(aggregate)
    result = {"skill": "ecommerce-order-audit", "source_ids": [r["source_id"] for r in rows],
              "input_rows": len(rows), "exact_duplicates": duplicates, "conflicts": conflicts,
              "issues": issues, "aggregates": aggregates}
    return result, cleaned, fields


def write_outputs(source, out, result, cleaned, fields):
    targets = [out / name for name in ("result.json", "cleaned.csv", "issues.csv")]
    for target in targets:
        if target.resolve() == source.resolve() or target.exists() or target.is_symlink():
            raise ValueError(f"Refusing to overwrite source or existing output: {target}")
    out.mkdir(parents=True, exist_ok=True)
    with targets[1].open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=[*fields, "source_id", "row_number"])
        writer.writeheader()
        writer.writerows(cleaned)
    with targets[2].open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["source_id", "order_id", "row_number", "code", "field", "value"])
        writer.writeheader()
        writer.writerows(result["issues"])
    with targets[0].open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        result, cleaned, fields = audit(args.input)
        write_outputs(args.input, args.out, result, cleaned, fields)
    except (OSError, ValueError, UnicodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(args.out.resolve() / "result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
