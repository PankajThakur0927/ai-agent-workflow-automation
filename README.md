# AI Agent Workflow Automation

A reusable Python agent that reads 10 business workflow definitions from an Excel workbook, routes natural-language requests to the appropriate workflow, executes reusable tools, applies decision logic, and returns an auditable execution trace.

## Architecture

```text
User request + optional structured inputs
                 |
                 v
        WorkflowRouter (LLM)
      OpenAI JSON routing when configured
       keyword fallback when offline
                 |
                 v
      Excel Workflow Source (pandas)
                 |
                 v
          Shared Agent / Engine
                 |
       +---------+----------+
       |                    |
       v                    v
  Registered workflow   Shared tools / mock
  handlers              business data & APIs
       |                    |
       +---------+----------+
                 |
                 v
   Status + selected workflow + step trace
            + final structured result
```

## Why this design?

- **No separate chatbots:** one router, one execution engine, a shared tool layer, and workflow-specific handlers.
- **Excel is the source of truth for definitions:** `app/workflow_source.py` reads `Workflows` and `Test_Questions` from the supplied workbook at runtime. Trigger, inputs, steps, decisions, required tools, and expected output are returned with every run.
- **LLM-assisted selection:** if `OPENAI_API_KEY` is configured, the router asks the LLM to choose a workflow ID using the definitions from Excel and requests structured JSON. Without a key or if the API call fails, a deterministic keyword fallback keeps the app runnable.
- **Controlled execution:** the LLM selects a workflow; Python executes validated registered handlers. The LLM cannot run arbitrary code or invent tool names.
- **Auditable results:** every run returns the selected workflow, routing rationale, execution steps, status, result, and timestamp.
- **Mock data/APIs:** sample inventory, vendor pricing, order service, employee directory, catalog, and execution logs make the assessment demonstrable without company credentials.
- **Extension point:** new workflows can be added by adding a row to the Excel `Workflows` sheet and registering a Python handler in `WorkflowEngine.handlers`. Shared tools can be reused. The current assessment's 10 workflows are implemented.

> Production note: WF003 currently uses the included sample vendor dataset; WF001/WF002/WF005/WF006/WF009/WF010 use in-memory demo data. Replace these data adapters with real database/API integrations when credentials and schemas are available. WF004 uses a transparent template so missing attributes are never invented. LLM-based routing is active with an API key; workflow-specific generation can be upgraded to model calls in a production deployment.

## Implemented workflows

| ID | Workflow | Conditions covered |
|---|---|---|
| WF001 | Inventory Restock Check | `current_stock < minimum_stock`; calculate target-stock reorder quantity |
| WF002 | Product Price Validation | Match by SKU; flag absolute price differences greater than 10% |
| WF003 | Vendor File Processing | Normalize column names; missing SKU/product name creates invalid row |
| WF004 | Product Description Generator | Explicitly mark missing product attributes; request product name if missing |
| WF005 | Customer Order Status | Look up order ID; ask for another identifier if not found |
| WF006 | Duplicate Product Detection | Exact SKU = definite duplicate; attribute/name similarity = possible duplicate |
| WF007 | Marketing Campaign Brief | Ask for campaign goal and dates if missing |
| WF008 | SEO Keyword Classification | Informational, commercial, transactional, navigational intent; priority and target page |
| WF009 | Employee Task Assignment | Score skill match and capacity; escalate if no suitable employee has capacity |
| WF010 | Workflow Performance Report | Success/failure, average time, errors, workflow-level failure rates, recommendations |

## Quick start

### 1. Requirements

- Python 3.10 or newer
- An OpenAI API key is optional for fallback mode and recommended for LLM routing.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the LLM (optional)

Copy `.env.example` to `.env` and add your key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Never commit `.env` or expose your API key in a demo video. The app still runs without a key using the fallback router.

### 4. Run the command-line agent

Run from the repository root:

```bash
python -m app.main
```

Example request:

```text
Request> Which products need restocking?
```

### 5. Run the web interface

```bash
streamlit run streamlit_app.py
```

The interface displays the selected workflow, routing method and rationale, steps executed, final result, and the Excel definition used. Use the optional JSON input box for structured inputs, for example:

```json
{
  "product_name": "Travel Mug",
  "category": "Drinkware",
  "attributes": "double-wall insulation",
  "material": "stainless steel",
  "color": "silver",
  "target_audience": "commuters"
}
```

For a campaign brief:

```json
{
  "campaign_goal": "Launch the autumn collection",
  "products": ["Travel Mug", "Desk Lamp"],
  "target_audience": "young professionals",
  "promotion": "10% launch discount",
  "dates": "2026-11-01 to 2026-11-14"
}
```

For keyword classification:

```json
{
  "keywords": [
    "how to choose a laptop stand",
    "buy wireless mouse",
    "wireless mouse price",
    "Acme store"
  ]
}
```

For employee assignment:

```json
{
  "task_description": "Build a FastAPI integration",
  "required_skills": ["python", "api", "fastapi"],
  "priority": "urgent",
  "deadline": "2026-10-22"
}
```

## Test the implementation

```bash
pytest -q
```

The tests cover all 10 assessment request examples and selected decision rules: low stock, >10% price differences, invalid vendor rows, missing order handling, and missing campaign inputs.

## Example requests from the assessment

1. `Which products need restocking?`
2. `Find products where vendor price differs by more than 10%.`
3. `Process this vendor spreadsheet and show invalid rows.`
4. `Generate SEO content for this product.`
5. `Where is order ORD-1001?`
6. `Find likely duplicate products in the catalog.`
7. `Create a campaign brief for the new collection.`
8. `Classify these keywords and map them to pages.`
9. `Assign this urgent task to the best available developer.`
10. `Which workflows are failing most often?`

## Adding workflow 11

1. Add a new row to the `Workflows` sheet with a unique `Workflow_ID`, name, trigger, inputs, steps, decision logic, tools, and expected output.
2. Implement a Python handler in `WorkflowEngine` that accepts `(request, inputs, trace)` and returns a dictionary.
3. Register the handler in `WorkflowEngine.handlers`.
4. Add a routing keyword to `WorkflowRouter._keyword_fallback` if the LLM is not configured.
5. Add a test for the new request and important decision conditions.

The Excel loader and UI do not need to be rewritten. For a fully data-driven future version, represent steps as typed operations and have the engine interpret a small, validated step DSL instead of adding a handler; this assessment version deliberately keeps business logic explicit and testable.

## Project structure

```text
.
├── app/
│   ├── config.py
│   ├── engine.py
│   ├── main.py
│   ├── router.py
│   ├── sample_data.py
│   ├── tools.py
│   └── workflow_source.py
├── data/
│   └── AI_Agent_Workflow_Assessment.xlsx
├── examples/
├── tests/
│   └── test_workflows.py
├── .env.example
├── .gitignore
├── requirements.txt
├── streamlit_app.py
└── README.md
```

## Important limitations

This is an assessment-ready local demo, not a production-connected system. Mock records are clearly labeled. It does not change real inventory, assign real employees, send campaigns, or access real order systems. Before production, add authentication, authorization, input/file-size limits, structured logging, retry/timeouts, data privacy controls, real API adapters, and human approval for consequential actions.
