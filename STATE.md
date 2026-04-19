---
project: 85-zinc-slides-mcp
project_path: gsd-coreops-projects/PROJ299-zinc-slides-mcp
project_id: PROJ299
phase: plan
current_wave: 1
last_updated: 2026-04-19T20:30:00Z
notion_page_id: 347b5fdb-c0bc-81a5-965a-ffff3980bec4
ops_board_page_id: 347b5fdb-c0bc-81a5-965a-ffff3980bec4
due: 2026-04-25
central_task_list: true
task_page_ids:
  T1: 347b5fdb-c0bc-8153-8cb5-cdc383a69a18
  T2: 347b5fdb-c0bc-8178-9d22-f4a63a8bf56f
  T3: 347b5fdb-c0bc-818a-b4b1-df14c288952b
  T4: 347b5fdb-c0bc-819d-8e27-db23bd8ed829
  T5: 347b5fdb-c0bc-81b0-8ba3-ea8b0f2d5347
  T6: 347b5fdb-c0bc-817d-bb94-c6becf4f959a
  T7: 347b5fdb-c0bc-81ba-9ad5-c0e81481c164
  T8: 347b5fdb-c0bc-81cd-bb60-f992f5678ec7
goals:
  - "Create on-brand Google Slides from Claude chat with zero user manual steps"
  - "Edit/update existing Zinc slides via Claude"
  - "All 8 Zinc brand templates working end-to-end"
  - "Deployed to Railway, registered as Claude Enterprise org connector"
stakeholders:
  - "Dan Course — owner"
  - "Zinc team — end users (claude.ai Enterprise)"
blockers: []
decisions:
  - "Node.js/TypeScript over Python — better MCP SDK support"
  - "Service account auth — no per-user OAuth, simpler for org-wide use"
  - "Fork taylorwilsdon/google_workspace_mcp as base"
  - "Playfair Display + Inter as Google Font equivalents"
  - "Claude Design ruled out — too expensive, no native Slides output"
  - "HTTP + SSE transport (remote MCP, not stdio)"
---

## Completed
- [x] Brief written, templates catalogued from Figma .deck file
- [x] Architecture designed (MCP + Railway + Google Slides API)
- [x] 8 brand templates documented with colours, layouts, elements

## In Progress
- [ ] T1: Fork + clone base repo
- [ ] T2: Get Google service account credential

## Next
1. Wave 1: T1 + T2 (parallel)
2. Wave 2: MCP scaffold + Slides API connection
3. Wave 3: Template renderer
4. Wave 4: Edit tools + E2E test

## Blockers
(none)

## Notes for Next Session
- Build folder ID: 1WKRlte3nCKMgoiOct5zM70Ylon_ol_Af
- Brand colours + templates fully documented in BRIEF.md
- taylorwilsdon/google_workspace_mcp is the fork base
