# main.py
import argparse
import json
from datetime import date
from collections import defaultdict

import file_io as io_mod
import gpt


def normalize_amount(data):
    """Normalize the 'amount' field: strip '$' and convert to float when possible."""
    amount = data.get("amount")

    if amount is None:
        return data

    if isinstance(amount, str):
        cleaned = amount.strip()
        if cleaned.startswith("$"):
            cleaned = cleaned[1:].strip()
        try:
            data["amount"] = float(cleaned)
        except ValueError:
            pass

    return data


def parse_date_yyyy_mm_dd(s):
    """Parse YYYY-MM-DD into datetime.date, else return None."""
    if not isinstance(s, str):
        return None
    try:
        y, m, d = s.strip().split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def process_directory(dirpath):
    """Process all receipt images in a directory and extract structured info."""
    results = {}
    for name, path in io_mod.list_files(dirpath):
        image_b64 = io_mod.encode_file(path)
        data = gpt.extract_receipt_info(image_b64)
        data = normalize_amount(data)
        results[name] = data
    return results


def filter_expenses(data_by_file, start_s, end_s):
    """Filter receipts by inclusive date range."""
    start_d = parse_date_yyyy_mm_dd(start_s)
    end_d = parse_date_yyyy_mm_dd(end_s)

    if start_d is None or end_d is None:
        raise ValueError("Dates must be YYYY-MM-DD")

    rows = []
    for fname, rec in data_by_file.items():
        d = parse_date_yyyy_mm_dd(rec.get("date"))
        amt = rec.get("amount")

        if d is None or not isinstance(amt, (int, float)):
            continue

        if start_d <= d <= end_d:
            rows.append(
                (fname, d.isoformat(), float(amt),
                 rec.get("vendor"), rec.get("category"))
            )

    rows.sort(key=lambda r: (r[1], r[0]))
    return rows


def print_expenses_report(rows, start_s, end_s):
    """Print expenses table and total."""
    total = sum(r[2] for r in rows)

    print(f"Expenses from {start_s} to {end_s}")
    print("-" * 60)
    for fname, d, amt, vendor, category in rows:
        print(f"{d}  ${amt:.2f}  {category or ''}  {vendor or ''}  ({fname})")
    print("-" * 60)
    print(f"TOTAL: ${total:.2f}")


def plot_by_category(data_by_file, out_path):
    """Save a pie chart of spending by category."""
    import matplotlib.pyplot as plt

    sums = defaultdict(float)
    for rec in data_by_file.values():
        amt = rec.get("amount")
        cat = rec.get("category")
        if isinstance(amt, (int, float)) and isinstance(cat, str):
            sums[cat] += amt

    if not sums:
        raise ValueError("No valid data to plot")

    plt.figure()
    plt.pie(sums.values(), labels=sums.keys(), autopct="%1.1f%%")
    plt.title("Spending by Category")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dirpath")
    parser.add_argument("--print", action="store_true")
    parser.add_argument("--expenses", nargs=2, metavar=("START", "END"))
    parser.add_argument("--plot", metavar="OUT_PNG")
    args = parser.parse_args()

    data = process_directory(args.dirpath)

    if args.print:
        print(json.dumps(data, indent=2))

    if args.expenses:
        rows = filter_expenses(data, args.expenses[0], args.expenses[1])
        print_expenses_report(rows, args.expenses[0], args.expenses[1])

    if args.plot:
        plot_by_category(data, args.plot)
        print(f"Saved plot to: {args.plot}")


if __name__ == "__main__":
    main()

