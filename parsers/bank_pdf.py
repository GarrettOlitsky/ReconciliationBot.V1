from __future__ import annotations

import re
import pandas as pd
import pdfplumber

# Fallback regex for text extraction (bank-dependent; meant as a safety net)
# Tries to catch lines like:
# 12/01 Starbucks 5.67
# 12/01 Payroll Deposit 1,200.00
LINE_RX = re.compile(
    r"(?P<date>\d{1,2}/\d{1,2}(?:/\d{2,4})?)\s+(?P<vendor>.+?)\s+(?P<amount>[-(]?\$?\d[\d,]*\.\d{2}\)?)\s*$"
)

def _clean_amount(s: str) -> float | None:
    s = s.strip()
    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1]
    s = s.replace("$", "").replace(",", "").strip()
    try:
        val = float(s)
        return -val if neg else val
    except ValueError:
        return None

def _try_extract_tables(pdf: pdfplumber.PDF) -> pd.DataFrame:
    rows = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables or []:
            for row in table:
                if row and any(cell is not None and str(cell).strip() for cell in row):
                    rows.append([str(c).strip() if c is not None else "" for c in row])

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Heuristic: find columns that look like debit/credit/amount
    # This is intentionally generic; you’ll tune per bank if needed.
    return df

def _try_parse_from_text(pdf: pdfplumber.PDF) -> pd.DataFrame:
    rows = []
    for page in pdf.pages:
        text = page.extract_text() or ""
        for raw_line in text.splitlines():
            line = raw_line.strip()
            m = LINE_RX.match(line)
            if not m:
                continue
            amt = _clean_amount(m.group("amount"))
            if amt is None:
                continue
            rows.append({"vendor": m.group("vendor").strip(), "amount": amt})

    return pd.DataFrame(rows)

def parse_bank_pdf(file_obj) -> pd.DataFrame:
    with pdfplumber.open(file_obj) as pdf:
        # 1) Try table extraction first (best)
        table_df = _try_extract_tables(pdf)

        # If we got a real table, try to interpret it
        if not table_df.empty:
            # Heuristic interpretation:
            # Look for rows that have a money-looking value in the last 1-3 columns
            money_rx = re.compile(r"^\(?-?\$?\d[\d,]*\.\d{2}\)?$")

            extracted = []
            for _, row in table_df.iterrows():
                cells = [str(x).strip() for x in row.tolist()]
                # find last money-ish cell
                money_idx = None
                money_val = None
                for i in range(len(cells) - 1, -1, -1):
                    c = cells[i].replace(" ", "")
                    if money_rx.match(c):
                        money_idx = i
                        money_val = cells[i]
                        break
                if money_idx is None:
                    continue

                # vendor usually somewhere before money column; take the longest non-empty text cell before it
                vendor_candidates = [c for c in cells[:money_idx] if c and not money_rx.match(c.replace(" ", ""))]
                if not vendor_candidates:
                    continue
                vendor = max(vendor_candidates, key=len).strip()

                amt = _clean_amount(money_val)
                if amt is None:
                    continue

                extracted.append({"vendor": vendor, "amount": amt})

            df = pd.DataFrame(extracted)
            if not df.empty:
                return df[["vendor", "amount"]]

        # 2) Fallback: parse page text lines (works on some statements)
        text_df = _try_parse_from_text(pdf)
        if not text_df.empty:
            return text_df[["vendor", "amount"]]

    raise ValueError(
        "PDF: could not extract transactions. "
        "If this is a scanned PDF, convert to CSV or use PNG/OCR. "
        "If it's a text PDF, your bank layout may need a tuned parser."
    )


