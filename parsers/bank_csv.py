from __future__ import annotations

import pandas as pd

COMMON_VENDOR_COLS = [
    "description", "merchant", "name", "details", "transaction description", "memo"
]
COMMON_AMOUNT_COLS = ["amount", "amt"]
COMMON_DEBIT_COLS = ["debit", "withdrawal", "withdrawals"]
COMMON_CREDIT_COLS = ["credit", "deposit", "deposits"]

def _find_col(cols, candidates):
    lower = {c.lower().strip(): c for c in cols}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    return None

def parse_bank_csv(file_obj) -> pd.DataFrame:
    df = pd.read_csv(file_obj)

    vendor_col = _find_col(df.columns, COMMON_VENDOR_COLS)
    amt_col = _find_col(df.columns, COMMON_AMOUNT_COLS)
    debit_col = _find_col(df.columns, COMMON_DEBIT_COLS)
    credit_col = _find_col(df.columns, COMMON_CREDIT_COLS)

    if vendor_col is None:
        raise ValueError("CSV: could not find a vendor/description column.")

    if amt_col:
        df["amount"] = pd.to_numeric(df[amt_col], errors="coerce")
    elif debit_col or credit_col:
        debit = pd.to_numeric(df[debit_col], errors="coerce").fillna(0) if debit_col else 0
        credit = pd.to_numeric(df[credit_col], errors="coerce").fillna(0) if credit_col else 0
        df["amount"] = credit - debit
    else:
        raise ValueError("CSV: could not find amount column(s). Need Amount or (Debit/Credit).")

    df["vendor"] = df[vendor_col].astype(str).str.strip()
    df = df.dropna(subset=["amount"])
    return df[["vendor", "amount"]]


