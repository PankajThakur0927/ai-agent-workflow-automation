import json
import pandas as pd
import streamlit as st
from app.main import WorkflowAgent
from app.workflow_source import load_test_questions

st.set_page_config(page_title="AI Workflow Agent", page_icon="🤖", layout="wide")
st.title("AI Agent Workflow Automation")
st.caption("One reusable agent routes requests to workflow definitions loaded from Excel.")
@st.cache_resource
def get_agent():
    return WorkflowAgent()
agent=get_agent()
with st.sidebar:
    st.header("Available workflows")
    st.dataframe(pd.DataFrame([{"ID":w["Workflow_ID"],"Workflow":w["Workflow_Name"]} for w in agent.workflows]),
                 hide_index=True, width=True)
    st.caption("Workflow definitions are read from data/AI_Agent_Workflow_Assessment.xlsx")
    provider = getattr(agent.router, "provider", "unknown")
client = getattr(agent.router, "client", None)

st.markdown(
    f"**LLM routing:** {provider.title() if client else 'Keyword fallback'}"
)
with st.form("request_form"):
    request=st.text_area("What would you like the agent to do?",
                         value="Which products need restocking?", height=100)
    st.caption("Optional JSON inputs for workflows needing structured fields. Example: {\"product_name\":\"Travel Mug\", \"category\":\"Drinkware\"}")
    raw_inputs=st.text_area("Optional inputs (JSON)", value="{}", height=90)
    submitted=st.form_submit_button("Run agent", type="primary")
if submitted:
    try:
        inputs=json.loads(raw_inputs or "{}")
        if not isinstance(inputs,dict): raise ValueError("Inputs must be a JSON object.")
        result=agent.run(request,inputs)
        st.subheader("Workflow selected")
        c1,c2,c3=st.columns(3)
        c1.metric("Workflow",result["selection"]["workflow_id"])
        c2.metric("Router",result["selection"]["router"])
        c3.metric("Status",result["status"].replace("_"," ").title())
        st.write(result["selection"]["workflow_name"])
        st.caption(f'Confidence: {result["selection"]["confidence"]:.0%} · {result["selection"]["rationale"]}')
        st.subheader("Steps executed")
        st.dataframe(pd.DataFrame(result["steps"]),hide_index=True,use_container_width=True)
        st.subheader("Final result")
        st.json(result["result"])
        with st.expander("Workflow definition loaded from Excel"):
            st.json(result["workflow_definition"])
        with st.expander("Full execution trace (JSON)"):
            st.code(json.dumps(result,indent=2,default=str),language="json")
    except Exception as exc:
        st.error(f"Could not run request: {exc}")
st.divider()
with st.expander("Try the 10 assessment test requests"):
    questions=load_test_questions()
    for q in questions:
        if st.button(f'{q["Workflow_ID"]}: {q["Test_Request"]}',key=q["Workflow_ID"]):
            st.session_state["preset_request"]=q["Test_Request"]
            st.info("Copy this request into the request box above and click Run agent.")
