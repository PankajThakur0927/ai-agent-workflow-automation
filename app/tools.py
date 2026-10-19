from difflib import SequenceMatcher
import re
import pandas as pd

def read_csv_or_excel(path: str) -> pd.DataFrame:
    if not path:
        raise ValueError("A CSV/XLSX file path is required.")
    lower = path.lower()
    if lower.endswith(".csv"):
        return pd.read_csv(path)
    if lower.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    raise ValueError("Unsupported file type. Please use CSV or XLSX.")

def normalize_column(name: str) -> str:
    name = re.sub(r"([a-z])([A-Z])", r"\1_\2", str(name))
    name = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return re.sub(r"_+", "_", name).strip("_")

def similarity(a, b) -> float:
    return SequenceMatcher(None, str(a).strip().lower(), str(b).strip().lower()).ratio()

def safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def money(value) -> str:
    return f"${value:,.2f}"
