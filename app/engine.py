from datetime import datetime
from .sample_data import INVENTORY, PRODUCT_PRICES, VENDOR_PRICES, VENDOR_FILE, ORDERS, PRODUCT_CATALOG, EMPLOYEES, EXECUTION_LOGS
from .tools import normalize_column, similarity, safe_float

class WorkflowEngine:
    """Shared execution shell; workflow definitions come from Excel, handlers are reusable tools."""
    def __init__(self):
        self.handlers = {
            "WF001": self.inventory_restock, "WF002": self.price_validation,
            "WF003": self.vendor_processing, "WF004": self.product_description,
            "WF005": self.order_status, "WF006": self.duplicate_detection,
            "WF007": self.campaign_brief, "WF008": self.keyword_classification,
            "WF009": self.employee_assignment, "WF010": self.performance_report,
        }

    def execute(self, workflow: dict, request: str, inputs: dict | None = None) -> dict:
        inputs = inputs or {}
        wid = workflow["Workflow_ID"]
        if wid not in self.handlers:
            raise ValueError(f"No registered executor for {wid}. Add a handler to extend the system.")
        trace = []
        trace.append({"step":"Workflow loaded from Excel", "status":"success",
                      "detail":f'{wid}: {workflow["Workflow_Name"]}'})
        try:
            result = self.handlers[wid](request, inputs, trace)
            return {"workflow_id":wid, "workflow_name":workflow["Workflow_Name"],
                    "status":result.pop("status", "success"), "steps":trace,
                    "result":result, "executed_at":datetime.now().isoformat(timespec="seconds")}
        except Exception as exc:
            trace.append({"step":"Error handler", "status":"error", "detail":str(exc)})
            return {"workflow_id":wid, "workflow_name":workflow["Workflow_Name"],
                    "status":"error", "steps":trace,
                    "result":{"message":str(exc),"recovery":"Check the input and retry."},
                    "executed_at":datetime.now().isoformat(timespec="seconds")}

    def inventory_restock(self, request, inputs, trace):
        trace.append({"step":"Fetch inventory", "status":"success","detail":f"{len(INVENTORY)} products loaded"})
        df=INVENTORY.copy()
        df["needs_restock"]=df.current_stock < df.minimum_stock
        df["suggested_reorder_quantity"]=(df.target_stock-df.current_stock).clip(lower=0)
        rows=df[df.needs_restock][["sku","product_name","current_stock","minimum_stock","suggested_reorder_quantity"]].to_dict("records")
        trace.append({"step":"Check threshold and calculate reorder quantity","status":"success","detail":f"{len(rows)} products below minimum"})
        return {"restock_list":rows,"count":len(rows),"note":"Demo inventory data."}

    def price_validation(self, request, inputs, trace):
        df=PRODUCT_PRICES.merge(VENDOR_PRICES,on="sku",how="inner")
        df["difference_percent"]=((df.vendor_price-df.internal_price).abs()/df.internal_price*100).round(2)
        df["exception"]=df.difference_percent>10
        rows=df.to_dict("records")
        trace.extend([{"step":"Match by SKU and compare prices","status":"success","detail":f"{len(rows)} products matched"},
                      {"step":"Flag differences above 10%","status":"success","detail":f'{int(df.exception.sum())} exceptions found'}])
        return {"validation_report":rows,"exceptions":[r for r in rows if r["exception"]],"threshold_percent":10}

    def vendor_processing(self, request, inputs, trace):
        df=VENDOR_FILE.copy()
        df.columns=[normalize_column(c) for c in df.columns]
        required=["sku","product_name"]
        invalid=df[df[required].isna().any(axis=1) | (df[required].astype(str).apply(lambda col: col.str.strip().eq("")).any(axis=1))]
        cleaned=df.drop(index=invalid.index).copy()
        trace.extend([{"step":"Read and normalize columns","status":"success","detail":f"{len(df.columns)} columns normalized"},
                      {"step":"Validate required fields","status":"success","detail":f"{len(invalid)} invalid rows"}])
        return {"cleaned_rows":cleaned.to_dict("records"),"invalid_rows":invalid.to_dict("records"),
                "summary":{"input_rows":len(df),"clean_rows":len(cleaned),"invalid_rows":len(invalid)},
                "note":"Demo vendor file; replace with a user-uploaded CSV/XLSX path in production."}

    def product_description(self, request, inputs, trace):
        product=inputs.get("product_name")
        if not product:
            import re
            m=re.search(r"(?:for|about)\s+(.+?)(?:\.|$)",request,re.I)
            product=m.group(1).strip() if m else None
        missing=[x for x in ["category","attributes","material","color","target_audience"] if not inputs.get(x)]
        if not product:
            trace.append({"step":"Validate product inputs","status":"needs_input","detail":"Product name is required"})
            return {"status":"needs_input","message":"Please provide the product name, category, attributes, material, color, and target audience.",
                    "missing_fields":["product_name","category","attributes","material","color","target_audience"]}
        trace.append({"step":"Validate product inputs","status":"success","detail":"Product name received"})
        # Do not invent attributes. A transparent template is used when no LLM key is configured.
        category=inputs.get("category","[not provided]")
        attributes=inputs.get("attributes","[not provided]")
        material=inputs.get("material","[not provided]")
        color=inputs.get("color","[not provided]")
        audience=inputs.get("target_audience","[not provided]")
        desc=f"{product} is a {category} product. Key attributes: {attributes}. Material: {material}. Color: {color}. Designed for: {audience}."
        trace.append({"step":"Generate description and SEO fields","status":"success","detail":"Generated from supplied attributes; missing values explicitly marked"})
        return {"product_description":desc,"short_description":f"{product} — {attributes}.",
                "seo_title":f"{product} | {category}","meta_description":f"Discover {product}. Attributes: {attributes}. Material: {material}.",
                "missing_fields":missing,"note":"Template generation; connect an LLM for richer copy."}

    def order_status(self, request, inputs, trace):
        import re
        order_id=inputs.get("order_id")
        if not order_id:
            m=re.search(r"ORD-\d+",request,re.I)
            order_id=m.group(0).upper() if m else None
        if not order_id:
            return {"status":"needs_input","message":"Please provide an order ID (e.g., ORD-1001) or customer email."}
        order=ORDERS.get(order_id)
        if not order:
            trace.append({"step":"Search order database","status":"not_found","detail":f"No order found for {order_id}"})
            return {"status":"needs_input","message":f"No order found for {order_id}. Please provide another order ID or customer email."}
        trace.extend([{"step":"Search order data","status":"success","detail":f"Found {order_id}"},
                      {"step":"Retrieve shipment information","status":"success","detail":order["shipment_status"]}])
        return {"order":order}

    def duplicate_detection(self, request, inputs, trace):
        df=PRODUCT_CATALOG.copy()
        groups=[]; used=set()
        for i,row in df.iterrows():
            if i in used: continue
            matches=[]
            for j,other in df.iterrows():
                if j<=i or j in used: continue
                if str(row.sku)==str(other.sku):
                    confidence=1.0; kind="definite duplicate (exact SKU match)"
                else:
                    score=similarity(row.product_name,other.product_name)
                    same_attrs=sum(str(row[k]).lower()==str(other[k]).lower() for k in ["category","color","material"])/3
                    confidence=round(0.7*score+0.3*same_attrs,2)
                    kind="possible duplicate" if confidence>=0.78 else None
                if kind:
                    matches.append({"sku":other.sku,"product_name":other.product_name,"confidence":confidence,"classification":kind})
                    used.add(j)
            if matches:
                groups.append({"product":{"sku":row.sku,"product_name":row.product_name},"matches":matches})
        trace.append({"step":"Normalize identifiers and compare attributes","status":"success","detail":f"{len(groups)} duplicate groups identified"})
        return {"duplicate_groups":groups,"method":"Exact SKU is definite; name/attribute similarity >= 0.78 is possible."}

    def campaign_brief(self, request, inputs, trace):
        goal=inputs.get("campaign_goal")
        dates=inputs.get("dates")
        if not goal or not dates:
            missing=[field for field,val in [("campaign_goal",goal),("dates",dates)] if not val]
            trace.append({"step":"Validate campaign inputs","status":"needs_input","detail":f"Missing {', '.join(missing)}"})
            return {"status":"needs_input","message":"Please provide the campaign goal and campaign dates before I generate the brief.",
                    "missing_fields":missing}
        audience=inputs.get("target_audience","Not specified")
        products=inputs.get("products",["Products not specified"])
        promotion=inputs.get("promotion","No promotion specified")
        trace.extend([{"step":"Identify objective and summarize products","status":"success","detail":str(goal)},
                      {"step":"Generate messaging, channels, timeline and checklist","status":"success","detail":"Draft brief created"}])
        return {"objective":goal,"target_audience":audience,"products":products,"promotion":promotion,
                "dates":dates,"messaging":f"Introduce the collection with a clear benefit-led message for {audience}.",
                "recommended_channels":["Email","Website landing page","Organic social media"],
                "timeline":[{"period":"Pre-launch","action":"Prepare assets and teaser content"},{"period":"Launch","action":"Publish campaign and send email"},{"period":"Post-launch","action":"Review engagement and conversions"}],
                "checklist":["Approve copy and creative","Verify landing page","Schedule campaign","Track results"]}

    def keyword_classification(self, request, inputs, trace):
        keywords=inputs.get("keywords",["how to choose a laptop stand","buy wireless mouse","wireless mouse price","Acme store"])
        categories=[]
        for kw in dict.fromkeys(str(k).strip() for k in keywords if str(k).strip()):
            t=kw.lower()
            if any(x in t for x in ["buy","order","purchase","coupon","price"]): intent="transactional"
            elif any(x in t for x in ["best","review","compare","vs","top"]): intent="commercial"
            elif any(x in t for x in ["how","what","why","guide","learn"]): intent="informational"
            elif any(x in t for x in ["brand","store","login","website"]): intent="navigational"
            else: intent="informational"
            category="Accessories" if any(x in t for x in ["mouse","laptop","keyboard","hub"]) else "General"
            priority="high" if intent=="transactional" else ("medium" if intent=="commercial" else "low")
            page="Product page" if intent=="transactional" else ("Category/comparison page" if intent=="commercial" else ("Guide/blog" if intent=="informational" else "Brand page"))
            categories.append({"keyword":kw,"intent":intent,"category":category,"priority":priority,"recommended_target_page":page})
        trace.append({"step":"Deduplicate and classify keyword intent","status":"success","detail":f"{len(categories)} unique keywords classified"})
        return {"keyword_report":categories}

    def employee_assignment(self, request, inputs, trace):
        task=inputs.get("task_description") or request
        required=[s.lower() for s in inputs.get("required_skills",["python","api"])]
        priority=inputs.get("priority","urgent")
        deadline=inputs.get("deadline","Not specified")
        ranked=[]
        for emp in EMPLOYEES:
            skillset={s.lower() for s in emp["skills"]}
            skill_score=sum(1 for skill in required if any(skill in s or s in skill for s in skillset))/max(1,len(required))
            capacity=max(0,emp["capacity"]-emp["active_tasks"])
            availability=capacity/max(1,emp["capacity"])
            score=round(0.75*skill_score+0.25*availability,3)
            ranked.append({"name":emp["name"],"skills":emp["skills"],"active_tasks":emp["active_tasks"],
                           "capacity":emp["capacity"],"available_slots":capacity,"score":score})
        ranked.sort(key=lambda x:(x["score"],x["available_slots"]),reverse=True)
        suitable=[x for x in ranked if x["score"]>0 and x["available_slots"]>0]
        trace.append({"step":"Match skills and evaluate workload","status":"success","detail":f"{len(suitable)} suitable candidates"})
        if not suitable:
            return {"status":"needs_escalation","message":"No suitable employee with available capacity. Escalate to a manager.","ranked_candidates":ranked}
        best=suitable[0]
        return {"recommended_employee":best["name"],"reasoning":f"Highest combined skill-match and capacity score ({best['score']}).",
                "priority":priority,"deadline":deadline,"task_summary":task,"ranked_candidates":ranked}

    def performance_report(self, request, inputs, trace):
        df=EXECUTION_LOGS.copy()
        total=len(df); successes=int((df.status=="success").sum()); failures=total-successes
        failure_rate=round(failures/total*100,2) if total else 0
        avg=round(float(df.duration_seconds.mean()),2) if total else 0
        by=df.groupby("workflow_id").agg(total=("status","count"),failures=("status",lambda s:(s=="failure").sum()),
                                         avg_seconds=("duration_seconds","mean")).reset_index()
        by["failure_rate_percent"]=(by.failures/by.total*100).round(2)
        errors=df[df.error.astype(str).str.strip()!=""].error.value_counts().to_dict()
        trace.extend([{"step":"Aggregate execution logs","status":"success","detail":f"{total} executions analyzed"},
                      {"step":"Calculate metrics and identify issues","status":"success","detail":f"{failure_rate}% overall failure rate"}])
        return {"total_executions":total,"successes":successes,"failures":failures,"failure_rate_percent":failure_rate,
                "average_execution_seconds":avg,"workflows":by.to_dict("records"),"frequent_errors":errors,
                "recommendations":["Investigate workflows with failure rates above 10%.","Add timeouts and retries for transient API failures.","Instrument slow steps with duration metrics."]}
