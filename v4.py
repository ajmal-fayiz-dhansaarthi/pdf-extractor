import camelot
import PyPDF2
import re
import json
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv() 

PDF_PATH = os.getenv('PDF_PATH')
PDF_PASSWORD = os.getenv('PDF_PASSWORD')

print(f"PDF Path: {PDF_PATH}")
print(f"PDF Password: {PDF_PASSWORD}")
def extract_key_value_data(pdf_path, password=None):
    """Extract key-value pairs from PDF text"""
    
    # Open and read PDF text
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        
        # Decrypt if password protected
        if pdf_reader.is_encrypted and password:
            pdf_reader.decrypt(password)
        
        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
    
    # Initialize extracted data dictionary
    extracted_data = {
        "document_info": {},
        "portfolio_summary": {},
        "fund_details": [],
        "transactions": []
    }
    
    # Extract document information
    patterns = {
        "statement_period": r"(\d{2}-\w{3}-\d{4})\s+To\s+(\d{2}-\w{3}-\d{4})",
        "pan": r"PAN:\s*([A-Z]{5}\d{4}[A-Z])",
        "folio_no": r"Folio\s*No[:\s]*(\d+\s*/\s*\d+)",
        "kyc_status": r"KYC:\s*([A-Z]+)",
        "nominee_1": r"Nominee\s*1:\s*([A-Z\s]+?)(?=\s+Nominee\s*2:|\s+PAN:|\n)",
        "nominee_2": r"Nominee\s*2:\s*([A-Z\s]+?)(?=\s+Nominee\s*3:|\s+PAN:|\n|$)",
        "nominee_3": r"Nominee\s*3:\s*([A-Z\s]+?)(?=\s+Opening|\n|$)",
        "registrar": r"Registrar\s*[:\s]*([A-Z\s]+?)(?=\n|$)"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE | re.MULTILINE)
        if match:
            if key == "statement_period":
                extracted_data["document_info"]["period_start"] = match.group(1)
                extracted_data["document_info"]["period_end"] = match.group(2)
            else:
                extracted_data["document_info"][key] = match.group(1).strip()
    
    return extracted_data, full_text

def extract_portfolio_summary(tables):
    """Extract portfolio summary from tables"""
    portfolio_data = []
    
    for i, table in enumerate(tables):
        df = table.df
        print(f"Table {i} shape: {df.shape}")
        print(f"Table {i} content:\n{df}\n")
        
        # Look for portfolio summary table - more flexible approach
        found_portfolio = False
        for row_idx, row in df.iterrows():
            row_text = ' '.join([str(cell) for cell in row])
            if 'PORTFOLIO SUMMARY' in row_text.upper():
                found_portfolio = True
                print(f"Found portfolio summary in table {i}")
                break
        
        if found_portfolio or any('Cost Value' in str(cell) or 'Market Value' in str(cell) for row in df.values for cell in row):
            # Find the header row
            header_row_idx = None
            for row_idx, row in df.iterrows():
                if 'Mutual Fund' in str(row.iloc[0]) and len(df.columns) >= 3:
                    header_row_idx = row_idx
                    break
            
            if header_row_idx is not None:
                # Get headers
                headers = df.iloc[header_row_idx].tolist()
                print(f"Headers found: {headers}")
                
                # Process data rows
                for row_idx in range(header_row_idx + 1, len(df)):
                    row = df.iloc[row_idx]
                    fund_name = str(row.iloc[0]).strip()
                    
                    # Skip empty rows and totals
                    if fund_name and fund_name.lower() not in ['total', '', 'nan']:
                        fund_data = {
                            'mutual_fund': fund_name,
                            'cost_value': str(row.iloc[1]).strip() if len(row) > 1 else '',
                            'market_value': str(row.iloc[2]).strip() if len(row) > 2 else ''
                        }
                        portfolio_data.append(fund_data)
                        print(f"Added fund: {fund_data}")
    
    return portfolio_data

def extract_transactions(tables):
    """Extract transaction data from tables"""
    transactions = []
    
    for i, table in enumerate(tables):
        df = table.df
        print(f"Checking table {i} for transactions:")
        print(f"Table shape: {df.shape}")
        
        # Look for transaction patterns - more flexible approach
        found_transactions = False
        
        # Check if table contains transaction-like data
        for row_idx, row in df.iterrows():
            row_text = ' '.join([str(cell) for cell in row])
            # Look for date patterns or transaction keywords
            if (re.search(r'\d{2}-\w{3}-\d{4}', row_text) or 
                'Systematic Investment' in row_text or
                'Dividend' in row_text or
                'Redemption' in row_text):
                found_transactions = True
                print(f"Found transaction indicators in table {i}")
                break
        
        if found_transactions:
            # Process each row looking for transaction data
            for row_idx, row in df.iterrows():
                row_data = [str(cell).strip() for cell in row]
                
                # Look for rows with date pattern
                if len(row_data) >= 3 and re.search(r'\d{2}-\w{3}-\d{4}', row_data[0]):
                    transaction = {
                        'date': row_data[0],
                        'transaction_type': row_data[1] if len(row_data) > 1 else '',
                        'amount': '',
                        'units': '',
                        'nav': '',
                        'unit_balance': ''
                    }
                    
                    # Try to extract numeric values from remaining columns
                    numeric_cols = []
                    for col in row_data[2:]:
                        if col and col != 'nan' and col != '':
                            numeric_cols.append(col)
                    
                    # Map numeric columns to transaction fields
                    if len(numeric_cols) >= 1:
                        transaction['amount'] = numeric_cols[0]
                    if len(numeric_cols) >= 2:
                        transaction['units'] = numeric_cols[1]
                    if len(numeric_cols) >= 3:
                        transaction['nav'] = numeric_cols[2]
                    if len(numeric_cols) >= 4:
                        transaction['unit_balance'] = numeric_cols[3]
                    
                    transactions.append(transaction)
                    print(f"Added transaction: {transaction}")
    
    return transactions

def main():
    # Configuration
    pdf_path = PDF_PATH
    password = PDF_PASSWORD
    output_json_path = 'extracted_statement_data_v4.json'
    
    try:
        # Extract key-value data from PDF text
        print("Extracting document information...")
        extracted_data, full_text = extract_key_value_data(pdf_path, password)
        
        # Extract tables using camelot
        print("Extracting tables...")
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream', password=password)
        print(f"Found {len(tables)} tables")
        
        # Debug: Print basic info about each table
        for i, table in enumerate(tables):
            print(f"\nTable {i}: {table.df.shape} - Accuracy: {table.accuracy}")
            print("First few rows:")
            print(table.df.head())
        
        # Extract portfolio summary
        print("\nProcessing portfolio summary...")
        portfolio_summary = extract_portfolio_summary(tables)
        extracted_data["portfolio_summary"] = portfolio_summary
        
        # Extract transactions
        print("\nProcessing transactions...")
        transactions = extract_transactions(tables)
        extracted_data["transactions"] = transactions
        
        # Add extraction metadata
        extracted_data["extraction_info"] = {
            "extraction_date": datetime.now().isoformat(),
            "total_tables_found": len(tables),
            "total_transactions": len(transactions),
            "total_funds": len(portfolio_summary)
        }
        
        # Save to JSON
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(extracted_data, json_file, indent=4, ensure_ascii=False)
        
        print(f"\nExtraction complete!")
        print(f"Data saved to: {output_json_path}")
        print(f"Found {len(portfolio_summary)} funds in portfolio")
        print(f"Found {len(transactions)} transactions")
        
        # Print sample of extracted key information
        print("\nSample extracted information:")
        for key, value in extracted_data["document_info"].items():
            print(f"{key}: {value}")
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        print("Make sure you have the required libraries installed:")
        print("pip install camelot-py[cv] PyPDF2")

if __name__ == "__main__":
    main()