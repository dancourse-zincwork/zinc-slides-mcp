"""Zinc Slides MCP tools."""

import os
import json
import uuid
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP

from zinc_auth import refresh_access_token, build_slides_service, build_drive_service
from zinc_brand_templates import build_slide_requests

load_dotenv()

mcp = FastMCP("zinc-slides")

_CLIENT_ID     = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
_REFRESH_TOKEN = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN", "")
_FOLDER_ID     = os.getenv("ZINC_DRIVE_FOLDER_ID", "")

_access_token: str = ""


def _get_token() -> str:
    global _access_token
    _access_token = refresh_access_token(_CLIENT_ID, _CLIENT_SECRET, _REFRESH_TOKEN)
    return _access_token


def _url(pres_id: str) -> str:
    return f"https://docs.google.com/presentation/d/{pres_id}/edit"


def _move_to_folder(drive, file_id: str) -> None:
    if not _FOLDER_ID:
        return
    f = drive.files().get(fileId=file_id, fields="parents").execute()
    old_parents = ",".join(f.get("parents", []))
    drive.files().update(
        fileId=file_id,
        addParents=_FOLDER_ID,
        removeParents=old_parents,
        fields="id,parents",
    ).execute()


@mcp.tool()
def create_zinc_presentation(title: str, slides: list) -> str:
    """Create a new on-brand Zinc Google Slides presentation.

    Args:
        title: Presentation title.
        slides: List of slide dicts, each with 'template' and 'content' keys.
                Templates: title, agenda, section_divider, metrics_stats,
                feature_update, demo_presenter, team_roadmap, release_list.

    Returns:
        Google Slides URL.
    """
    token = _get_token()
    slides_svc = build_slides_service(token)
    drive_svc  = build_drive_service(token)

    pres = slides_svc.presentations().create(body={"title": title}).execute()
    pres_id = pres["presentationId"]
    _move_to_folder(drive_svc, pres_id)

    # Remove the default blank slide
    default_slides = pres.get("slides", [])
    delete_reqs = [{"deleteObject": {"objectId": s["objectId"]}}
                   for s in default_slides]
    if delete_reqs:
        slides_svc.presentations().batchUpdate(
            presentationId=pres_id, body={"requests": delete_reqs}
        ).execute()

    # Add branded slides
    for i, slide_def in enumerate(slides):
        template = slide_def.get("template", "section_divider")
        content  = slide_def.get("content", slide_def)
        slide_id = f"slide_{uuid.uuid4().hex[:8]}"

        create_req = [{"createSlide": {
            "objectId": slide_id,
            "insertionIndex": i,
        }}]
        slides_svc.presentations().batchUpdate(
            presentationId=pres_id, body={"requests": create_req}
        ).execute()

        brand_reqs = build_slide_requests(slide_id, template, content)
        if brand_reqs:
            slides_svc.presentations().batchUpdate(
                presentationId=pres_id, body={"requests": brand_reqs}
            ).execute()

    return f"Presentation created: {_url(pres_id)}"


@mcp.tool()
def get_zinc_presentation(presentation_id: str) -> str:
    """Read a presentation's structure so Claude can make targeted edits.

    Returns JSON summary with slide index, template hint (from title text), and content.
    """
    token = _get_token()
    svc   = build_slides_service(token)
    pres  = svc.presentations().get(presentationId=presentation_id).execute()

    summary = {"title": pres.get("title"), "slides": []}
    for i, slide in enumerate(pres.get("slides", [])):
        texts = []
        for el in slide.get("pageElements", []):
            shape = el.get("shape", {})
            for te in shape.get("text", {}).get("textElements", []):
                c = te.get("textRun", {}).get("content", "").strip()
                if c:
                    texts.append(c)
        summary["slides"].append({
            "index": i,
            "slide_id": slide["objectId"],
            "text_content": texts[:6],
        })

    return json.dumps(summary, indent=2)


@mcp.tool()
def add_zinc_slide(presentation_id: str, position: int,
                   template: str, content: dict) -> str:
    """Insert a new branded slide at the given position (0-based).

    Args:
        presentation_id: The Google Slides presentation ID.
        position: Where to insert (0 = before first slide).
        template: One of the 8 Zinc templates.
        content: Template content dict (see create_zinc_presentation docs).

    Returns:
        Updated presentation URL.
    """
    token    = _get_token()
    svc      = build_slides_service(token)
    slide_id = f"slide_{uuid.uuid4().hex[:8]}"

    svc.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [{"createSlide": {
            "objectId": slide_id, "insertionIndex": position,
        }}]},
    ).execute()

    brand_reqs = build_slide_requests(slide_id, template, content)
    if brand_reqs:
        svc.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": brand_reqs}
        ).execute()

    return f"Slide added: {_url(presentation_id)}"


@mcp.tool()
def update_zinc_slide(presentation_id: str, slide_index: int,
                      template: str, content: dict) -> str:
    """Replace a slide's content with a fresh branded template.

    Deletes all existing elements on the slide and re-applies the template.

    Args:
        presentation_id: The Google Slides presentation ID.
        slide_index: 0-based index of the slide to update.
        template: Zinc template name.
        content: New content dict.

    Returns:
        Updated presentation URL.
    """
    token = _get_token()
    svc   = build_slides_service(token)
    pres  = svc.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])

    if slide_index >= len(slides):
        return f"Error: slide index {slide_index} out of range (deck has {len(slides)} slides)"

    slide    = slides[slide_index]
    slide_id = slide["objectId"]

    # Delete all existing page elements
    delete_reqs = [{"deleteObject": {"objectId": el["objectId"]}}
                   for el in slide.get("pageElements", [])]
    if delete_reqs:
        svc.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": delete_reqs}
        ).execute()

    brand_reqs = build_slide_requests(slide_id, template, content)
    if brand_reqs:
        svc.presentations().batchUpdate(
            presentationId=presentation_id, body={"requests": brand_reqs}
        ).execute()

    return f"Slide {slide_index} updated: {_url(presentation_id)}"


@mcp.tool()
def delete_zinc_slide(presentation_id: str, slide_index: int) -> str:
    """Delete a slide by index (0-based).

    Returns:
        Updated presentation URL.
    """
    token = _get_token()
    svc   = build_slides_service(token)
    pres  = svc.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])

    if slide_index >= len(slides):
        return f"Error: slide index {slide_index} out of range"

    slide_id = slides[slide_index]["objectId"]
    svc.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [{"deleteObject": {"objectId": slide_id}}]},
    ).execute()
    return f"Slide {slide_index} deleted: {_url(presentation_id)}"


@mcp.tool()
def reorder_zinc_slides(presentation_id: str, new_order: list) -> str:
    """Reorder slides. new_order is a list of current 0-based indices in desired order.

    Example: [2, 0, 1] moves current slide 2 to position 0.

    Returns:
        Updated presentation URL.
    """
    token = _get_token()
    svc   = build_slides_service(token)
    pres  = svc.presentations().get(presentationId=presentation_id).execute()
    slides = pres.get("slides", [])

    slide_ids = [slides[i]["objectId"] for i in new_order if i < len(slides)]
    svc.presentations().batchUpdate(
        presentationId=presentation_id,
        body={"requests": [{"updateSlidesPosition": {
            "slideObjectIds": slide_ids,
            "insertionIndex": 0,
        }}]},
    ).execute()
    return f"Slides reordered: {_url(presentation_id)}"


@mcp.tool()
def list_zinc_presentations(search: Optional[str] = "") -> str:
    """List recent Zinc presentations from the shared Drive folder.

    Args:
        search: Optional title filter string.

    Returns:
        Formatted list of presentation titles and URLs.
    """
    token = _get_token()
    svc   = build_drive_service(token)

    q = f"mimeType='application/vnd.google-apps.presentation' and trashed=false"
    if _FOLDER_ID:
        q += f" and '{_FOLDER_ID}' in parents"
    if search:
        q += f" and name contains '{search}'"

    result = svc.files().list(
        q=q,
        fields="files(id,name,modifiedTime)",
        orderBy="modifiedTime desc",
        pageSize=20,
    ).execute()

    files = result.get("files", [])
    if not files:
        return "No presentations found."

    lines = [f"- {f['name']} | {_url(f['id'])} (modified {f['modifiedTime'][:10]})"
             for f in files]
    return "\n".join(lines)
