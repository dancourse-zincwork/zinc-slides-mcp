# Plan: Zinc Slides MCP Server

## Wave 1 — Foundation (parallel)
- [ ] **T1: Fork + clone base repo** | Agent: self | Est: quick
  - Fork taylorwilsdon/google_workspace_mcp
  - Clone to gsd-coreops-projects/PROJ{ID}-zinc-slides-mcp
  - Strip to Slides-relevant code only
- [ ] **T2: Get Google service account credential** | Agent: self | Est: quick
  - Fetch via /creds or check if existing Drive credential works
  - Confirm Editor access to Zinc Build Drive folder

## Wave 2 — Core MCP server (depends on Wave 1)
- [ ] **T3: Set up MCP server scaffold** | Agent: self | Depends: T1
  - HTTP + SSE transport
  - Register all 7 tools (create, get, add, update, delete, reorder, list)
  - Auth middleware (bearer token)
  - Deploy stub to Railway (returns dummy data)
- [ ] **T4: Google Slides API connection** | Agent: self | Depends: T1, T2
  - Service account auth working
  - Can create empty presentation in Zinc Drive folder
  - Can read presentation structure back

## Wave 3 — Brand template renderer (depends on Wave 2)
- [ ] **T5: Template renderer — cream/white slides** | Agent: codex | Depends: T3, T4
  - title, agenda, feature_update, demo_presenter, release_list templates
  - Brand colours, Playfair Display heading, Inter body
  - Decorative elements: triangle, pink underline, large numbers, pill badges
- [ ] **T6: Template renderer — blush/textured slides** | Agent: codex | Depends: T3, T4
  - section_divider, metrics_stats, team_roadmap templates
  - Diagonal texture background (pre-rendered SVG → Drive → insert)
  - White rounded cards

## Wave 4 — Edit tools + end-to-end test (depends on Wave 3)
- [ ] **T7: Edit tools** | Agent: self | Depends: T5, T6
  - get_presentation returns structured JSON Claude can reason over
  - update_slide patches specific slide
  - add_slide inserts at position
  - delete_slide, reorder_slides
- [ ] **T8: End-to-end test** | Agent: self | Depends: T7
  - Create a full Tech Fry Up style deck from Claude chat
  - Edit an existing slide via Claude
  - Verify output in Zinc Drive with correct branding
  - Register as connector in Claude Enterprise (or test via desktop MCP config)
