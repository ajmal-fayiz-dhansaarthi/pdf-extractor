# PDF Extracter

This project extracts key information, portfolio summaries, and transaction details from mutual fund statement PDFs.

## Features

- Extracts document info 
- Parses portfolio summary and transactions using Camelot and PyPDF2
- Outputs structured data as JSON

## Setup

1. **Clone the repository**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Add a `.env` file** with:
   ```
   PDF_PATH="your_statement.pdf"
   PDF_PASSWORD="your_password"
   ```
4. **Place your PDF in the project directory**

## Usage

```bash
python v4.py
# or
python v5.py
```

## Notes

- All PDF files are ignored by git via `.gitignore`.
- Output JSON will be saved as `extracted_statement_data_**.json`.

## Requirements

- Python 3.7+
- [Camelot](https://camelot-py.readthedocs.io/)
- PyPDF2
- python-dotenv