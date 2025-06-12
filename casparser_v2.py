
import os
import json
import requests
from dotenv import load_dotenv
import requests
import casparser

# Load environment variables from .env file
load_dotenv()

# PDF_URL = os.getenv('PDF_PATH_1')
PDF_URL = "https://izkualqyrhgozeydabjj.........04-4d56-8e2d-663598c70506.pdf" #supabase link
PDF_PASSWORD = os.getenv('PDF_PASSWORD_1')
LOCAL_PDF_PATH = 'downloaded_statement.pdf'

OUTPUT_JSON_PATH = 'extracted_statement_data_casparser_test.json'
OUTPUT_TXT_PATH = 'transactions.txt'
OUTPUT_CSV_PATH = 'transactions.csv'

def download_pdf(url, local_path):
    response = requests.get(url)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        f.write(response.content)

def main():
    if not PDF_URL or not PDF_PASSWORD:
        print("Error: PDF_URL or PDF_PASSWORD not set in .env file.")
        return

    # Download the PDF from the URL
    print("Downloading PDF...")
    download_pdf(PDF_URL, LOCAL_PDF_PATH)
    print("PDF downloaded to", LOCAL_PDF_PATH)

    # Get data in JSON-serializable format
    json_data = casparser.read_cas_pdf(LOCAL_PDF_PATH, PDF_PASSWORD, output="json")

    # Write JSON data to TXT and JSON files
    with open(OUTPUT_TXT_PATH, 'w', encoding='utf-8') as txt_file:
        txt_file.write(json.dumps(json_data, indent=4, ensure_ascii=False))
    print("Data written to", OUTPUT_TXT_PATH)

    parsed_json_data = json.loads(json_data)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(parsed_json_data, json_file, indent=4, ensure_ascii=False)
    print("JSON data written to", OUTPUT_JSON_PATH)

    # Get transactions data in CSV string format
    csv_str = casparser.read_cas_pdf(LOCAL_PDF_PATH, PDF_PASSWORD, output="csv")
    with open(OUTPUT_CSV_PATH, 'w', encoding='utf-8') as csv_file:
        csv_file.write(csv_str)
    print("CSV data written to", OUTPUT_CSV_PATH)

if __name__ == "__main__":
    main()