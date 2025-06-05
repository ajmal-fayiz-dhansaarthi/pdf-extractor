
# import pypdf

# def extract_text_from_protected_pdf(pdf_path, password):
#     reader = pypdf.PdfReader(pdf_path)

#     if reader.is_encrypted:
#         reader.decrypt(password)

#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() or ""

#     with open(output_text_path, 'w', encoding='utf-8') as text_file:
#             text_file.write(text)

# # Example usage
# pdf_path = './NSDLe-CAS_115105632_APR_2025.PDF'
# password = 'AQMPB2554Q'
# output_text_path = 'extracted_text.txt'

# extracted_text = extract_text_from_protected_pdf(pdf_path, password)


# import pypdf
# import re
# import json

# def extract_text_from_protected_pdf(pdf_path, password):
#     reader = pypdf.PdfReader(pdf_path)

#     if reader.is_encrypted:
#         reader.decrypt(password)

#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() or ""

#     return text

# def parse_transactions(text):
#     # Assuming your table headers are known
#     headers = ["Date", "Transaction Details", "Stamp Duty", "NAV"]

#     # Find transaction lines using regex (example pattern)
#     transaction_lines = re.findall(r'(\d{2}/\d{2}/\d{4}).+?(?=\n)', text)

#     # Split text into lines
#     lines = text.split('\n')

#     transactions = []
#     for line in lines:
#         # Basic cleanup and split
#         columns = re.split(r'\s{2,}', line.strip())

#         if len(columns) >= len(headers):
#             transaction = {headers[i]: columns[i] for i in range(len(headers))}
#             transactions.append(transaction)

#     return transactions

# # Example usage
# pdf_path = './NSDLe-CAS_115105632_APR_2025.PDF'
# password = 'AQMPB2554Q'
# output_json_path = 'extracted_transactions.json'

# text = extract_text_from_protected_pdf(pdf_path, password)
# transactions = parse_transactions(text)

# with open(output_json_path, 'w', encoding='utf-8') as json_file:
#     json.dump(transactions, json_file, indent=4)

# print(f"Transactions extracted and saved to {output_json_path}")

# ================================
# import pdfplumber
# import json

# def extract_tables_from_protected_pdf(pdf_path, password):
#     extracted_tables = []

#     with pdfplumber.open(pdf_path, password=password) as pdf:
#         for page in pdf.pages:
#             tables = page.extract_tables()
#             for table in tables:
#                 # Each table is a list of rows; each row is a list of cells
#                 for row in table:
#                     extracted_tables.append(row)

#     return extracted_tables

# def parse_transactions_from_tables(tables):
#     # Assuming the first row is headers
#     headers = None
#     transactions = []
#     for row in tables:
#         # Skip empty rows
#         if not any(row):
#             continue
#         if headers is None:
#             headers = row  # First non-empty row as headers
#         else:
#             transaction = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
#             transactions.append(transaction)
#     return transactions

# import camelot

# # Read tables
# a = camelot.read_pdf("test.pdf")

# # Print first table
# print(a[0].df)

# # Example usage
# pdf_path = './AQXXXXXX4Q_01042023-31032024_CP169296113_17072024112509423.pdf'
# output_json_path = 'extracted_transactions.json'
# password = 'qwqw1212'


# tables = extract_tables_from_protected_pdf(pdf_path, password)
# transactions = parse_transactions_from_tables(tables)

# with open(output_json_path, 'w', encoding='utf-8') as json_file:
#     json.dump(transactions, json_file, indent=4)

# print(f"Transactions extracted and saved to {output_json_path}")
# ======================================
# using camelot
import camelot
import json
output_json_path = 'extracted_transactions.json'
# Extract tables from PDF
tables = camelot.read_pdf('./AQXXXXXX4Q_01042023-31032024_CP169296113_17072024112509423.pdf', pages='all', flavor='stream', password="qwqw1212")

# Export to JSON
transactions = []
for table in tables:
    df = table.df
    print("tables",df)
    headers = df.iloc[0]  # First row as headers
    for index, row in df.iloc[1:].iterrows():
        transaction = {headers[i]: row[i] for i in range(len(headers))}
        transactions.append(transaction)

with open(output_json_path, 'w', encoding='utf-8') as json_file:
    json.dump(transactions, json_file, indent=4)

print(f"Transactions extracted and saved to {output_json_path}")
# ===================
# using tabula
# import tabula
# import pandas as pd
# import json

# def extract_tables_from_pdf(pdf_path):
#     tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True)
#     return tables

# def parse_transactions_from_tables(tables):
#     transactions = []
#     for df in tables:
#         if df.empty:
#             continue  # Skip empty tables

#         df.columns = df.iloc[0]  # First row as headers
#         df = df.drop(0).reset_index(drop=True)  # Remove the header row

#         for index, row in df.iterrows():
#             transaction = row.to_dict()
#             transactions.append(transaction)
#     return transactions

# # Example usage
# pdf_path = './NSDLe-CAS_115105632_APR_2025.PDF'
# output_json_path = 'extracted_transactions.json'

# tables = extract_tables_from_pdf(pdf_path)
# transactions = parse_transactions_from_tables(tables)

# with open(output_json_path, 'w', encoding='utf-8') as json_file:
#     json.dump(transactions, json_file, indent=4)

# print(f"Transactions extracted and saved to {output_json_path}")
