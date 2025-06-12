import casparser
import os
from dotenv import load_dotenv
import json

load_dotenv()


output_json_path = 'extracted_statement_data_casparser_test.json'
PDF_PATH = os.getenv('PDF_PATH')
PDF_PASSWORD = os.getenv('PDF_PASSWORD')


data = casparser.read_cas_pdf(PDF_PATH, PDF_PASSWORD)
with open('transactions.txt', 'w', encoding='utf-8') as txt_file:
    txt_file.write(json.dumps(data, indent=4, ensure_ascii=False))
print(data)

# Get data in json format
json_str = casparser.read_cas_pdf(
    PDF_PATH, PDF_PASSWORD, output="json")
with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_str, json_file, indent=4, ensure_ascii=False)

# Get transactions data in csv string format
csv_str = casparser.read_cas_pdf(
    PDF_PATH, PDF_PASSWORD, output="csv")
with open('transactions.csv', 'w', encoding='utf-8') as csv_file:
    csv_file.write(csv_str)
