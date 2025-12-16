import streamlit as st
from pipeline import run_pipeline

st.set_page_config(page_title="ReconciliationBot", layout="centered")
st.title("ReconciliationBot")

st.write(
    "Upload a bank statement (PDF / CSV / PNG). "
    "Optionally upload a Chart of Accounts CSV (keyword, account)."
)

bank_file = st.file_uploader("Bank statement", type=["pdf", "csv", "png"])
coa_file = st.file_uploader("Optional: Chart of Accounts (CSV)", type=["csv"])

st.divider()

include_uncategorized = st.checkbox("Include Uncategorized rows", value=True)
debug = st.checkbox("Debug mode", value=False)

if st.button("Generate reconciliation.xlsx", type="primary", disabled=(bank_file is None)):
    try:
        xlsx_bytes = run_pipeline(
            bank_file=bank_file,
            coa_file=coa_file,
            include_uncategorized=include_uncategorized,
            debug=debug,
        )

        st.success("Done.")
        st.download_button(
            label="Download reconciliation.xlsx",
            data=xlsx_bytes,
            file_name="reconciliation.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    except Exception as e:
        st.error(f"Error: {e}")
        if debug:
            raise
