from app.main import WorkflowAgent

def test_workflow_selection_for_all_assessment_questions():
    agent=WorkflowAgent()
    requests=[
        ("Which products need restocking?","WF001"),
        ("Find products where vendor price differs by more than 10%.","WF002"),
        ("Process this vendor spreadsheet and show invalid rows.","WF003"),
        ("Generate SEO content for this product.","WF004"),
        ("Where is order ORD-1001?","WF005"),
        ("Find likely duplicate products in the catalog.","WF006"),
        ("Create a campaign brief for the new collection.","WF007"),
        ("Classify these keywords and map them to pages.","WF008"),
        ("Assign this urgent task to the best available developer.","WF009"),
        ("Which workflows are failing most often?","WF010"),
    ]
    for request, expected in requests:
        assert agent.router.select(request)["workflow"]["Workflow_ID"] == expected

def test_inventory_contains_low_stock_products():
    agent=WorkflowAgent()
    result=agent.run("Which products need restocking?")
    assert result["workflow_id"]=="WF001"
    assert result["result"]["count"] >= 1
    assert all(x["current_stock"] < x["minimum_stock"] for x in result["result"]["restock_list"])

def test_price_validation_flags_over_ten_percent():
    result=WorkflowAgent().run("Find products where vendor price differs by more than 10%.")
    assert result["workflow_id"]=="WF002"
    assert all(x["difference_percent"] > 10 for x in result["result"]["exceptions"])

def test_vendor_processing_reports_invalid_rows():
    result=WorkflowAgent().run("Process this vendor spreadsheet and show invalid rows.")
    assert result["workflow_id"]=="WF003"
    assert result["result"]["summary"]["invalid_rows"] == 2

def test_order_missing_prompts_for_another_identifier():
    result=WorkflowAgent().run("Where is order ORD-9999?")
    assert result["workflow_id"]=="WF005"
    assert result["status"]=="needs_input"

def test_campaign_missing_fields_requests_clarification():
    result=WorkflowAgent().run("Create a campaign brief for the new collection.")
    assert result["workflow_id"]=="WF007"
    assert result["status"]=="needs_input"


def test_all_ten_workflows_execute_and_return_a_trace():
    agent=WorkflowAgent()
    cases=[
        ("Which products need restocking?", {}),
        ("Find products where vendor price differs by more than 10%.", {}),
        ("Process this vendor spreadsheet and show invalid rows.", {}),
        ("Generate SEO content for this product.", {"product_name":"Bottle"}),
        ("Where is order ORD-1001?", {}),
        ("Find likely duplicate products in the catalog.", {}),
        ("Create a campaign brief for the new collection.", {"campaign_goal":"Launch","dates":"Nov 1-7"}),
        ("Classify these keywords and map them to pages.", {}),
        ("Assign this urgent task to the best available developer.", {}),
        ("Which workflows are failing most often?", {}),
    ]
    for request, inputs in cases:
        result=agent.run(request, inputs)
        assert result["workflow_id"].startswith("WF")
        assert result["steps"]
        assert "result" in result
        assert result["selection"]["workflow_name"]

def test_product_description_marks_missing_attributes():
    result=WorkflowAgent().run("Generate SEO content for this product.", {"product_name":"Travel Mug"})
    assert result["status"]=="success"
    assert "category" in result["result"]["missing_fields"]
    assert "[not provided]" in result["result"]["product_description"]
