from __future__ import annotations

import pandas as pd

from parsers.bank_csv import parse_bank_csv
from parsers.bank_pdf import parse_bank_pdf
from parsers.bank_png import parse_bank_png
from classify.rules import build_classifier
from export.writers import write_xlsx_bytes

def _normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    if "vendor" not in df.columns or "amount" not in df.columns:
        raise ValueError("Parser must return columns: vendor, amount")

    df = df.copy()
    df["vendor"] = df["vendor"].astype(str).str.strip()
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    return df

def run_pipeline(
    bank_file,
    coa_file=None,
    include_uncategorized: bool = True,
    debug: bool = False,
) -> bytes:
    filename = (getattr(bank_file, "name", "") or "").lower()

    if filename.endswith(".pdf"):
        df = parse_bank_pdf(bank_file)
    elif filename.endswith(".png"):
        df = parse_bank_png(bank_file)
    elif filename.endswith(".csv"):
        df = parse_bank_csv(bank_file)
    else:
        raise ValueError("Unsupported file type. Use PDF, CSV, or PNG.")

    df = _normalize_df(df)

    classifier = build_classifier(coa_file)
    df["account_classification"] = df["vendor"].apply(classifier)

    if not include_uncategorized:
        df = df[df["account_classification"] != "Uncategorized"].copy()

    debits = df[df["amount"] < 0].copy()
    credits = df[df["amount"] > 0].copy()

    # Output positive values on both sheets
    debits["amount"] = debits["amount"].abs()
    credits["amount"] = credits["amount"].abs()

    debits_out = debits[["amount", "vendor", "account_classification"]].sort_values(
        "amount", ascending=False
    )
    credits_out = credits[["amount", "vendor", "account_classification"]].sort_values(
        "amount", ascending=False
    )

    return write_xlsx_bytes(debits_out, credits_out)


