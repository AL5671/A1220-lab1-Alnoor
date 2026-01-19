# main.py
import json
import argparse
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


def main():
    """Parse CLI arguments, process a receipts directory, and optionally print JSON output."""
    parser = argparse.ArgumentParser()
    parser.add_argument("dirpath")
    parser.add_argument("--print", action="store_true")
    args = parser.parse_args()

    data = process_directory(args.dirpath)
    if args.print:
        print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()

