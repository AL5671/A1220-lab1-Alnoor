# A1220 Lab 1 – Receipt Parser

## Overview
This project processes images of receipts and uses the OpenAI API to extract
structured information including vendor, date, total amount, and category.

The program outputs the extracted information as JSON, mapping each receipt
image filename to its parsed fields.

## Project Structure
.
├── Makefile
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── gpt.py
│   └── file_io.py

## Setup

1. Create and activate a virtual environment
   python -m venv .venv
   source .venv/bin/activate

2. Install dependencies
   pip install openai pdoc

3. Set the OpenAI API key
   export OPENAI_API_KEY="YOUR_API_KEY_HERE"

## Running the Program
From the project root, run:
make run

This runs the program with the --print option enabled and prints the extracted
receipt data as JSON to the terminal.

## Documentation
To generate documentation using pdoc:
pdoc src -o docs

The generated documentation will appear in the docs/ directory.

## Notes
- Receipt images are not committed to the repository.
- The OpenAI API key must be set as an environment variable before running.
- Output is printed to standard output when --print is enabled.

## License
This project is licensed under the MIT License.

