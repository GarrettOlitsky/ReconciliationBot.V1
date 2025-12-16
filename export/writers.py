import io
import pandas as pd

def write_xlsx_bytes(debits_df, credits_df):
    out = io.BytesIO()
    with pd.ExcelWriter(out, engine="openpyxl") as writer:
        debits_df.to_excel(writer, sheet_name="Debits", index=False)
        credits_df.to_excel(writer, sheet_name="Credits", index=False)
    return out.getvalue()
