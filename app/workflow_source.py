from pathlib import Path
import pandas as pd
from .config import WORKBOOK_PATH

REQUIRED_COLUMNS = [
    "Workflow_ID", "Workflow_Name", "Trigger", "Inputs", "Steps",
    "Decision_Logic", "Tools_Required", "Expected_Output"
]

def load_workflows(path: str | Path = WORKBOOK_PATH) -> list[dict]:
    """Load workflow definitions from the supplied Excel workbook at runtime."""
    df = pd.read_excel(path, sheet_name="Workflows")
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Workflow sheet is missing columns: {sorted(missing)}")
    df = df[REQUIRED_COLUMNS].fillna("")
    workflows = df.to_dict(orient="records")
    for workflow in workflows:
        workflow["Workflow_ID"] = str(workflow["Workflow_ID"]).strip()
        workflow["Workflow_Name"] = str(workflow["Workflow_Name"]).strip()
    return workflows

def load_test_questions(path: str | Path = WORKBOOK_PATH) -> list[dict]:
    df = pd.read_excel(path, sheet_name="Test_Questions").fillna("")
    return df.to_dict(orient="records")
