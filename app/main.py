import json
from .workflow_source import load_workflows
from .router import WorkflowRouter
from .engine import WorkflowEngine

class WorkflowAgent:
    def __init__(self, workbook_path=None):
        self.workflows=load_workflows(workbook_path) if workbook_path else load_workflows()
        self.router=WorkflowRouter(self.workflows)
        self.engine=WorkflowEngine()

    def run(self, request: str, inputs: dict | None = None) -> dict:
        selection=self.router.select(request)
        execution=self.engine.execute(selection["workflow"], request, inputs)
        execution["selection"]={
            "workflow_id":selection["workflow"]["Workflow_ID"],
            "workflow_name":selection["workflow"]["Workflow_Name"],
            "confidence":selection["confidence"],
            "rationale":selection["rationale"],
            "router":selection["router"]
        }
        execution["workflow_definition"]={
            "trigger":selection["workflow"]["Trigger"],
            "inputs":selection["workflow"]["Inputs"],
            "steps":selection["workflow"]["Steps"],
            "decision_logic":selection["workflow"]["Decision_Logic"],
            "tools_required":selection["workflow"]["Tools_Required"],
            "expected_output":selection["workflow"]["Expected_Output"]
        }
        return execution

def main():
    agent=WorkflowAgent()
    print("AI Agent Workflow Automation (type 'exit' to quit)")
    while True:
        request=input("\nRequest> ").strip()
        if request.lower() in {"exit","quit"}: break
        try:
            print(json.dumps(agent.run(request),indent=2,default=str))
        except Exception as exc:
            print(f"Error: {exc}")

if __name__=="__main__":
    main()
