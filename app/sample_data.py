import pandas as pd

INVENTORY = pd.DataFrame([
    {"sku":"A100","product_name":"Wireless Mouse","current_stock":4,"minimum_stock":10,"target_stock":25},
    {"sku":"A101","product_name":"USB-C Hub","current_stock":18,"minimum_stock":8,"target_stock":20},
    {"sku":"A102","product_name":"Laptop Stand","current_stock":2,"minimum_stock":6,"target_stock":15},
])
PRODUCT_PRICES = pd.DataFrame([
    {"sku":"A100","product_name":"Wireless Mouse","internal_price":20.0},
    {"sku":"A101","product_name":"USB-C Hub","internal_price":35.0},
    {"sku":"A102","product_name":"Laptop Stand","internal_price":40.0},
])
VENDOR_PRICES = pd.DataFrame([
    {"sku":"A100","vendor_price":23.5},
    {"sku":"A101","vendor_price":36.0},
    {"sku":"A102","vendor_price":32.0},
])
VENDOR_FILE = pd.DataFrame([
    {"SKU":"V001","Product Name":"Travel Mug","Unit Price":12.5,"Category":"Drinkware"},
    {"SKU":"","Product Name":"Desk Lamp","Unit Price":21.0,"Category":"Lighting"},
    {"SKU":"V003","Product Name":"","Unit Price":8.0,"Category":"Stationery"},
])
ORDERS = {
    "ORD-1001": {"order_id":"ORD-1001","customer_email":"alex@example.com","status":"Shipped",
                 "items":["Wireless Mouse","USB-C Hub"],"shipment_status":"In transit",
                 "tracking_number":"TRK-784512","estimated_delivery":"2026-10-21"},
    "ORD-1002": {"order_id":"ORD-1002","customer_email":"sam@example.com","status":"Processing",
                 "items":["Laptop Stand"],"shipment_status":"Not shipped yet",
                 "tracking_number":None,"estimated_delivery":None},
}
PRODUCT_CATALOG = pd.DataFrame([
    {"sku":"P100","product_name":"Wireless Mouse","category":"Accessories","color":"Black","material":"Plastic"},
    {"sku":"P100","product_name":"Wireless Mouse","category":"Accessories","color":"Black","material":"Plastic"},
    {"sku":"P101","product_name":"Wireless Mouse Pro","category":"Accessories","color":"Black","material":"Plastic"},
    {"sku":"P102","product_name":"Steel Water Bottle","category":"Drinkware","color":"Silver","material":"Steel"},
])
EMPLOYEES = [
    {"name":"Asha","skills":["python","api","fastapi","automation"],"active_tasks":2,"capacity":5},
    {"name":"Ravi","skills":["python","machine learning","llm"],"active_tasks":5,"capacity":5},
    {"name":"Meera","skills":["javascript","react","api"],"active_tasks":1,"capacity":4},
]
EXECUTION_LOGS = pd.DataFrame([
    {"workflow_id":"WF001","status":"success","duration_seconds":1.2,"error":""},
    {"workflow_id":"WF002","status":"failure","duration_seconds":4.5,"error":"Vendor file missing"},
    {"workflow_id":"WF002","status":"failure","duration_seconds":5.1,"error":"Timeout"},
    {"workflow_id":"WF003","status":"success","duration_seconds":2.0,"error":""},
    {"workflow_id":"WF004","status":"success","duration_seconds":8.0,"error":""},
    {"workflow_id":"WF005","status":"success","duration_seconds":1.5,"error":""},
    {"workflow_id":"WF006","status":"failure","duration_seconds":7.5,"error":"Similarity threshold exceeded"},
])
