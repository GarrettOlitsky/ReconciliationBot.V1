import pandas as pd

DEFAULT_RULES = {
    "amazon": "Office Supplies",
    "starbucks": "Meals",
    "uber": "Travel",
    "lyft": "Travel",
    "doordash": "Meals",
    "stripe": "Sales Income",
    "paypal": "Sales Income",
    "interest": "Interest Income",
}

def _load_coa_rules(coa_file):
    if coa_file is None:
        return None

    coa = pd.read_csv(coa_file)
    coa.columns = [c.lower().strip() for c in coa.columns]

    if not {"keyword", "account"}.issubset(set(coa.columns)):
        raise ValueError("COA CSV must have columns: keyword, account")

    rules = [
        (str(k).lower().strip(), str(a).strip())
        for k, a in zip(coa["keyword"], coa["account"])
        if str(k).strip()
    ]
    return rules

def build_classifier(coa_file=None):
    coa_rules = _load_coa_rules(coa_file)
    default_rules = list(DEFAULT_RULES.items())

    def classify(vendor: str) -> str:
        v = (vendor or "").lower()

        if coa_rules:
            for kw, acct in coa_rules:
                if kw and kw in v:
                    return acct

        for kw, acct in default_rules:
            if kw in v:
                return acct

        return "Uncategorized"

    return classify
