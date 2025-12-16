# ReconciliationBot (V1)

ReconciliationBot is a **proof-of-concept reconciliation tool** that parses bank statements and generates a categorized reconciliation Excel file.

⚠️ **Version 1 Limitation**
- **V1 is tested and supported only for Bank of America PDF statements**
- Other banks (USAA, SoFi, etc.) are **best-effort only** and may require parser tuning
- PNG / OCR support is experimental

---

## What it does

Upload:
- A bank statement (**PDF / CSV / PNG**)
- Optional Chart of Accounts (**CSV**)

Output:
- `reconciliation.xlsx` with two sheets:
  - **Debits**: Amount, Vendor, Account Classification
  - **Credits**: Amount, Vendor, Account Classification

---

## Supported Inputs (V1)

### ✅ Bank of America
- **PDF (text-based)** — fully supported

### ⚠️ Experimental / Best-effort
- CSV bank exports
- PNG screenshots (OCR via Tesseract)
- PDFs from other banks (USAA, SoFi, etc.)

---

## Chart of Accounts (Optional)

Upload a CSV with columns:

```csv
keyword,account
amazon,Office Supplies
starbucks,Meals
uber,Travel
```
### 1. Clone the Repository
```
git clone https://github.com/GarrettOlitsky/ReconciliationBot.V1.git
cd ReconciliationBot.V1
```
### 2. Create and activate a virtual environment
```
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```
### 3. Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Run the Streamlit app
```
python -m streamlit run app/main.py
```
### Notes
Bank statements are layouts, not structured data
Each bank requires tailored parsing logic
This project intentionally prioritizes clarity over over-engineering
### Disclaimer
This project is for demonstration and workflow automation purposes only.
It is not financial, accounting, or tax advice, and is not production-ready.
