# BRIEF: Zinc Slides MCP Server

## Objective
A hosted MCP server that lets anyone at Zinc create, read, and edit on-brand Google Slides presentations directly from claude.ai chat — zero manual steps for the end user. Output always lands in Zinc's shared Google Drive.

## Background
- Zinc uses Figma Slides for "Tech Fry Up" and similar customer/internal decks
- The deck has a well-defined 8-template system with consistent brand colours and typography
- We're on Claude Enterprise — remote MCP servers are supported org-wide
- Claude Design (Anthropic) ruled out: burns weekly quota in 30 mins, no native Google Slides output
- No existing tool combines: MCP + Google Slides output + custom brand templates + Claude

## What It Does
- Claude interviews user about content → structures it as slide JSON
- Claude calls `create_presentation` / `update_slide` / `add_slide` tools on this MCP server
- Server applies Zinc brand templates, creates/edits the Google Slides file, outputs to Zinc Drive
- Claude returns the presentation URL — user never leaves the chat

## Slide Templates (8 total)
1. **Title** — cream bg, coral triangle, hero image, date, title
2. **Agenda** — white bg, serif italic heading + hot pink underline, agenda items
3. **Section divider** — blush bg + diagonal texture, large centered serif, small caps subtitle
4. **Metrics/stats** — cream bg + texture, grid of white stat cards with trend indicators
5. **Feature update** — white/cream, "NEW!" badge, numbered items with "LIVE" pills, optional screenshot
6. **Demo/presenter** — cream bg, presenter name, chart card
7. **Team roadmap** — blush bg + texture, 2×2 team cards with coloured pills
8. **Release list** — cream bg, large muted numbers, white feature cards with timeline pills

## Brand Colours
```
#FAF0EA  — warm cream (main bg)
#F9E4D8  — blush (section dividers, roadmap)
#F0196A  — hot pink (underline accents)
#2ECC40  — lime green (LIVE / NEW! badges)
#E8B0A0  — muted coral (decorative numbers, triangle)
#404040  — dark charcoal
#1A1A1A  — near-black text
#FFFFFF  — white cards
```

## Fonts
- Heading: Playfair Display (Google Font — editorial serif matching the deck)
- Body: Inter

## MCP Tools
| Tool | Description |
|------|-------------|
| `create_presentation` | Full deck from slide JSON array |
| `get_presentation` | Read current slides (Claude reads before editing) |
| `add_slide` | Insert slide at position with template + content |
| `update_slide` | Edit specific slide by index |
| `delete_slide` | Remove slide by index |
| `reorder_slides` | Change slide order |
| `list_presentations` | List Zinc's decks from Drive folder |

## Tech Stack
- Runtime: Node.js / TypeScript
- MCP SDK: `@modelcontextprotocol/sdk`
- Google APIs: `googleapis` npm package
- Auth: Google service account (no per-user OAuth)
- Hosting: Railway
- Transport: HTTP + SSE (remote MCP)
- Base: Fork of `taylorwilsdon/google_workspace_mcp`

## Constraints
- Service account must have Editor access to Zinc shared Drive folder
- All output goes to: `1WKRlte3nCKMgoiOct5zM70Ylon_ol_Af` (Zinc Build folder)
- Must be internet-reachable (Railway ✅)
- No per-user OAuth — one service account for all Zinc users

## Security & GDPR
- **PII:** Slide content may contain names, business data — stored transiently, never logged
- **Data flows:** User content → Claude → MCP server → Google Slides API → Zinc Drive. Nothing stored server-side beyond the Railway process lifetime
- **Credentials:** Google service account key → `CoreOps/GSD-Danger` vault (write access to Drive/Slides)
- **Blast radius:** Can create/modify files in Zinc Drive — scoped to the output folder only
- **Reversibility:** Google Slides supports version history; deletions recoverable from Drive trash
- **GDPR:** No retention. Slides content goes to Drive (covered by Zinc's Google Workspace DPA)
- **External exposure:** Railway endpoint must be authenticated (MCP auth token) — not public

## Success Criteria
- Claude in claude.ai chat can create a full branded deck end-to-end with no user intervention
- Claude can read an existing deck and make surgical edits
- All 8 templates render correctly in Google Slides
- Presentation lands in Zinc shared Drive folder and link is returned
- Deployable as org connector in Claude Enterprise
