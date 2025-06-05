import camelot
import PyPDF2
import re
import json
from datetime import datetime

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
    
    for table in tables:
        df = table.df
        
        # Check if this looks like a portfolio summary table
        if any('Cost Value' in str(cell) or 'Market Value' in str(cell) for row in df.values for cell in row):
            # Process portfolio summary
            headers = None
            for i, row in df.iterrows():
                if 'Mutual Fund' in str(row.iloc[0]) and 'Cost Value' in str(df.iloc[i+1] if i+1 < len(df) else ''):
                    headers = df.iloc[i+1].tolist()  # Next row contains headers
                    continue
                
                if headers and i > 1:  # Skip header rows
                    fund_data = {}
                    for j, value in enumerate(row):
                        if j < len(headers) and headers[j]:
                            fund_data[headers[j].strip()] = str(value).strip()
                    
                    if fund_data.get('Mutual Fund', '').strip() and fund_data['Mutual Fund'] != 'Total':
                        portfolio_data.append(fund_data)
    
    return portfolio_data

def extract_transactions(tables):
    """Extract transaction data from tables"""
    transactions = []
    
    for table in tables:
        df = table.df
        
        # Look for transaction tables (contain Date, Transaction columns)
        if any('Date' in str(cell) and 'Transaction' in str(cell) for row in df.values for cell in row):
            # Find header row
            header_row_idx = None
            for i, row in df.iterrows():
                if 'Date' in str(row.iloc[0]) and 'Transaction' in str(row.iloc[1]):
                    header_row_idx = i
                    break
            
            if header_row_idx is not None:
                headers = df.iloc[header_row_idx].tolist()
                headers = [str(h).strip() for h in headers if str(h).strip()]
                
                # Process transaction rows
                for i in range(header_row_idx + 1, len(df)):
                    row = df.iloc[i]
                    if str(row.iloc[0]).strip() and str(row.iloc[0]).strip() != '':
                        transaction = {}
                        for j, value in enumerate(row):
                            if j < len(headers) and headers[j]:
                                transaction[headers[j]] = str(value).strip()
                        
                        if transaction:
                            transactions.append(transaction)
    
    return transactions

def main():
    # Configuration
    pdf_path = './AQXXXXXX4Q_01042023-31032024_CP169296113_17072024112509423.pdf'
    password = "qwqw1212"
    output_json_path = 'extracted_statement_data_cl_test.json'
    
    try:
        # Extract key-value data from PDF text
        print("Extracting document information...")
        extracted_data, full_text = extract_key_value_data(pdf_path, password)
        
        # Extract tables using camelot
        print("Extracting tables...")
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream', password=password)
        
        # Extract portfolio summary
        print("Processing portfolio summary...")
        portfolio_summary = extract_portfolio_summary(tables)
        extracted_data["portfolio_summary"] = portfolio_summary
        
        # Extract transactions
        print("Processing transactions...")
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