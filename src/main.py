# main.py
import argparse
import json
from datetime import date
from collections import defaultdict

import file_io as io_mod
import gpt


def normalize_amount(data):
    """Normalize the 'amount' field: strip '$' and convert to float when possible.

    Args:
        data: Dict containing receipt fields, including "amount".

    Returns:
        The same dict with "amount" converted to float when possible.
    """
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
    """Parse a YYYY-MM-DD date string into a datetime.date.

    Args:
        s: Date string in YYYY-MM-DD format.

    Returns:
        datetime.date if valid, else None.
    """
    if not isinstance(s, str):
        return None
    s = s.strip()
    try:
        y, m, d = s.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        return None


def process_directory(dirpath):
    """Process all receipt images in a directory and extract structured info.

    Args:
        dirpath: Path to a directory containing receipt image files.

    Returns:
        A dict mapping each filename to the extracted receipt information.
    """
    results = {}
    for name, path in io_mod.list_files(dirpath):
        image_b64 = io_mod.encode_file(path)
        data = gpt.extract_receipt_info(image_b64)
        data = normalize_amount(data)
        results[name] = data
    return results


def filter_expenses(data_by_file, start_s, end_s):
    """Filter receipts by inclusive date range, keeping only valid date+amount rows.

    Args:
        data_by_file: Dict mapping filename -> receipt dict.
        start_s: Start date string YYYY-MM-DD (inclusive).
        end_s: End date string YYYY-MM-DD (inclusive).

    Returns:
        List of tuples: (filename, receipt_date, amount, vendor, category)
    """
    start_d = parse_date_yyyy_mm_dd(start_s)
    end_d = parse_date_yyyy_mm_dd(end_s)
    if start_d is None or end_d is None:
        raise ValueError("Dates must be in YYYY-MM-DD format (e.g., 2026-01-19).")

    rows = []
    for fname, rec in data_by_file.items():
        d = parse_date_yyyy_mm_dd(rec.get("date"))
        amt = rec.get("amount")

        if d is None:
            continue
        if not isinstance(amt, (int, float)):
            continue

        if start_d <= d <= end_d:
            rows.append(
                (
                    fname,
                    d.isoformat(),
                    float(amt),
                    rec.get("vendor"),
                    rec.get("category"),
                )
            )

    # Sort by date then filename for stable output
    rows.sort(key=lambda r: (r[1], r[0]))
    return rows


def print_expenses_report(rows, start_s, end_s):
    """Print an expenses report and total for the filtered receipts."""
    total = sum(r[2] for r in rows)

    print(f"Expenses from {start_s} to {end_s}")
    print("-" * 60)
    for fname, d, amt, vendor, category in rows:
        v = vendor if vendor is not None else ""
        c = category if category is not None else ""
        print(f"{d}  ${amt:.2f}  {c:16}  {v}  ({fname})")
    print("-" * 60)
    print(f"TOTAL: ${total:.2f}")


def plot_by_category(data_by_file, out_path):
    """Generate a pie chart of spending by category and save it to a PNG.

    Only includes receipts with a valid numeric amount and a non-empty category.

    Args:
        data_by_file: Dict mapping filename -> receipt dict.
        out_path: Output filename for the PNG (e.g., spending.png).
    """
    import matplotlib.pyplot as plt

    sums = defaultdict(float)
    for rec in data_by_file.values():
        cat = rec.get("category")
        amt = rec.get("amount")
        if not isinstance(amt, (int, float)):
            continue
        if not isinstance(cat, str) or not cat.strip():
            continue
        sums[cat.strip()] += float(amt)

    if not sums:
        raise ValueError("No valid (category, amount) data available to plot.")

    labels = list(sums.keys())
    values = [sums[k] for k in labels]

    plt.figure()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.title("Spending by Category")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def main():
    """Parse CLI arguments, process a receipts directory, and run requested outputs."""
    parser = argparse.ArgumentParser()
    parser.add_argument("dirpath")
    parser.add_argument("--print", action="store_true")
    parser.add_argument(
        "--expenses",
        nargs=2,
        metavar=("START", "END"),
        help="Print total expenses within an inclusive date range (YYYY-MM-DD YYYY-MM-DD).",
    )
    parser.add_argument(
        "--plot",
        metavar="OUT_PNG",
        help="Save a pie chart PNG of spending by category (e.g., spending.png).",
    )
    args = parser.parse_args()

    data = process_directory(args.dirpath)

    if args.print:
        print(json.dumps(data, indent=2))

    if args.expenses:
        start_s, end_s = args.expenses
        rows = filter_expenses(data, start_s, end_s)
        print_expenses_report(rows, start_s, end_s)

    if args.plot:
        plot_by_category(data, args.plot)
        print(f"Saved plot to: {args.plot}")


if __name__ == "__main__":
    main()

