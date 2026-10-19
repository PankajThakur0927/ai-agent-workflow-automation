
import json
from openai import OpenAI

from .config import (
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)


class WorkflowRouter:
    def __init__(self, workflows: list[dict]):
        self.workflows = workflows
        self.client = None
        self.model = None
        self.provider = LLM_PROVIDER

        try:
            if self.provider == "ollama":
                self.client = OpenAI(
                    base_url=OLLAMA_BASE_URL,
                    api_key="ollama",
                )
                self.model = OLLAMA_MODEL
            elif self.provider == "openai" and OPENAI_API_KEY:
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                self.model = OPENAI_MODEL
        except Exception as exc:
            print(f"LLM initialization failed: {exc}")
            self.client = None

    def select(self, request: str, inputs: dict | None = None) -> dict:
        inputs = inputs or {}

        if self.client:
            try:
                workflow_options = [
                    {
                        "id": w.get("Workflow_ID"),
                        "name": w.get("Workflow_Name"),
                        "description": w.get("Trigger", ""),
                    }
                    for w in self.workflows
                ]

                response = self.client.chat.completions.create(
                    model=self.model,
                    response_format={"type": "json_object"},
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Choose the best workflow for the user's request. "
                                "Return a JSON object with keys workflow_id and "
                                "rationale. workflow_id must exactly match an ID "
                                "from the supplied workflow list."
                            ),
                        },
                        {
                            "role": "user",
                            "content": json.dumps({
                                "request": request,
                                "inputs": inputs,
                                "workflows": workflow_options,
                            }),
                        },
                    ],
                    temperature=0,
                )

                content = response.choices[0].message.content
                if not content:
                    raise ValueError("The model returned an empty response.")

                parsed = json.loads(content)
                selected_id = str(parsed.get("workflow_id", ""))

                workflow = next(
                    (
                        w for w in self.workflows
                        if str(w.get("Workflow_ID", "")) == selected_id
                    ),
                    None,
                )

                if workflow:
                    return {
                        "workflow": workflow,
                        "confidence": 0.9,
                        "rationale": parsed.get(
                            "rationale", "Selected by the language model."
                        ),
                        "router": self.provider.title(),
                    }

                raise ValueError(
                    f"Unknown workflow ID returned by model: {selected_id}"
                )

            except Exception as exc:
                print(f"LLM routing failed; using keyword fallback: {exc}")

        request_lower = request.lower()
        keyword_groups = [
            (["restock", "inventory", "stock"], "WF001"),
            (["price", "pricing", "cost validation"], "WF002"),
            (["vendor", "supplier file", "vendor file"], "WF003"),
            (["description", "product copy"], "WF004"),
            (["order status", "track order", "delivery"], "WF005"),
            (["duplicate", "duplicates"], "WF006"),
            (["campaign", "marketing brief"], "WF007"),
            (["seo", "keyword classification", "keywords"], "WF008"),
            (["assign task", "employee task", "task assignment"], "WF009"),
            (["performance report", "workflow report"], "WF010"),
        ]

        selected_id = None
        for keywords, workflow_id in keyword_groups:
            if any(keyword in request_lower for keyword in keywords):
                selected_id = workflow_id
                break

        workflow = next(
            (
                w for w in self.workflows
                if str(w.get("Workflow_ID", "")) == selected_id
            ),
            None,
        )

        if workflow is None:
            raise ValueError(
                "Could not identify a workflow. Try describing inventory, "
                "price validation, vendor files, product descriptions, "
                "order status, duplicates, marketing campaigns, SEO, "
                "task assignment, or workflow performance."
            )

        return {
            "workflow": workflow,
            "confidence": 0.6,
            "rationale": "Selected using workflow-related keywords.",
            "router": "Keyword fallback",
        }
