from __future__ import annotations

import re
import pandas as pd
from PIL import Image
import pytesseract

# OCR line parser (bank-dependent; starter)
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

def parse_bank_png(file_obj) -> pd.DataFrame:
    img = Image.open(file_obj).convert("RGB")
    text = pytesseract.image_to_string(img)

    rows = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = LINE_RX.match(line)
        if not m:
            continue

        amt = _clean_amount(m.group("amount"))
        if amt is None:
            continue

        vendor = m.group("vendor").strip()
        rows.append({"vendor": vendor, "amount": amt})

    df = pd.DataFrame(rows)
    if df.empty:
        raise ValueError(
            "PNG: OCR ran but no transactions matched the parser. "
            "This usually means the statement layout needs tuning."
        )

    return df[["vendor", "amount"]]


