# Sample requests and expected behavior

Run these in the Streamlit UI or CLI:

- WF001: `Which products need restocking?` — returns low-stock products and suggested reorder quantities.
- WF002: `Find products where vendor price differs by more than 10%.` — returns SKU-matched price report and exceptions.
- WF003: `Process this vendor spreadsheet and show invalid rows.` — returns normalized clean rows and invalid rows.
- WF004: `Generate SEO content for this product.` with JSON fields — returns long/short description and SEO metadata; absent attributes are marked.
- WF005: `Where is order ORD-1001?` — returns status and tracking details. `ORD-9999` prompts for another identifier.
- WF006: `Find likely duplicate products in the catalog.` — returns duplicate groups and confidence.
- WF007: `Create a campaign brief for the new collection.` — asks for goal and dates. Supply those fields to get a brief.
- WF008: `Classify these keywords and map them to pages.` with a `keywords` list — returns intent, category, priority, and page.
- WF009: `Assign this urgent task to the best available developer.` with task and skills — returns ranked recommendation or escalation.
- WF010: `Which workflows are failing most often?` — returns success/failure metrics, error counts, and recommendations.

All outputs use illustrative sample data; replace adapters before using real business systems.
