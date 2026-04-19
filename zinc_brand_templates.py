"""Zinc brand template renderer — generates Google Slides batchUpdate request lists."""

from typing import Any

# ── Brand ──────────────────────────────────────────────────────────────────
COLOURS = {
    "cream":   "#FAF0EA",
    "blush":   "#F9E4D8",
    "hotpink": "#F0196A",
    "lime":    "#2ECC40",
    "coral":   "#E8B0A0",
    "charcoal":"#404040",
    "text":    "#1A1A1A",
    "white":   "#FFFFFF",
}
FONT_HEADING = "Playfair Display"
FONT_BODY    = "Inter"

# Slide canvas in EMU
W = 9_144_000
H = 5_143_500
INCH = 914_400


def hex_to_rgb(hex_str: str) -> dict:
    h = hex_str.lstrip("#")
    return {
        "red":   int(h[0:2], 16) / 255,
        "green": int(h[2:4], 16) / 255,
        "blue":  int(h[4:6], 16) / 255,
    }


def _colour(name: str) -> dict:
    return {"rgbColor": hex_to_rgb(COLOURS[name])}


# ── Shape helpers ──────────────────────────────────────────────────────────

def _rect(obj_id: str, x: int, y: int, w: int, h: int,
          shape: str = "RECTANGLE") -> dict:  # noqa: use ROUND_RECTANGLE not ROUND_RECT
    return {"createShape": {
        "objectId": obj_id,
        "shapeType": shape,
        "elementProperties": {
            "pageObjectId": "{{SLIDE_ID}}",
            "size": {"width": {"magnitude": w, "unit": "EMU"},
                     "height": {"magnitude": h, "unit": "EMU"}},
            "transform": {"scaleX": 1, "scaleY": 1,
                          "translateX": x, "translateY": y, "unit": "EMU"},
        },
    }}


def _fill(obj_id: str, colour_name: str) -> dict:
    return {"updateShapeProperties": {
        "objectId": obj_id,
        "shapeProperties": {"shapeBackgroundFill": {
            "solidFill": {"color": _colour(colour_name)}
        }},
        "fields": "shapeBackgroundFill",
    }}


def _fill_hex(obj_id: str, hex_colour: str) -> dict:
    return {"updateShapeProperties": {
        "objectId": obj_id,
        "shapeProperties": {"shapeBackgroundFill": {
            "solidFill": {"color": {"rgbColor": hex_to_rgb(hex_colour)}}
        }},
        "fields": "shapeBackgroundFill",
    }}


def _no_border(obj_id: str) -> dict:
    return {"updateShapeProperties": {
        "objectId": obj_id,
        "shapeProperties": {"outline": {"propertyState": "NOT_RENDERED"}},
        "fields": "outline",
    }}


def _text(obj_id: str, text: str, insert_index: int = 0) -> dict:
    return {"insertText": {"objectId": obj_id, "text": text,
                           "insertionIndex": insert_index}}


def _text_style(obj_id: str, font: str, size_pt: int, colour_name: str,
                bold: bool = False, italic: bool = False,
                start: int = 0, end: int | None = None) -> dict:
    style: dict[str, Any] = {
        "fontFamily": font,
        "fontSize": {"magnitude": size_pt, "unit": "PT"},
        "foregroundColor": {"opaqueColor": _colour(colour_name)},
        "bold": bold,
        "italic": italic,
    }
    tr: dict[str, Any] = {"type": "ALL"} if end is None else \
        {"type": "FIXED_RANGE", "startIndex": start, "endIndex": end}
    return {"updateTextStyle": {
        "objectId": obj_id,
        "textRange": tr,
        "style": style,
        "fields": "fontFamily,fontSize,foregroundColor,bold,italic",
    }}


def _card(obj_id: str, x: int, y: int, w: int, h: int) -> list[dict]:
    """White rounded-rect card with no border."""
    reqs = [
        _rect(obj_id, x, y, w, h, "ROUND_RECTANGLE"),
        _fill(obj_id, "white"),
        _no_border(obj_id),
        {"updateShapeProperties": {
            "objectId": obj_id,
            "shapeProperties": {"contentAlignment": "MIDDLE",
                                "autofit": {"autofitType": "NONE"}},
            "fields": "contentAlignment",
        }},
    ]
    return reqs


def _pill(obj_id: str, x: int, y: int, label: str,
          colour_name: str = "lime", text_colour: str = "text") -> list[dict]:
    pw, ph = int(INCH * 1.2), int(INCH * 0.28)
    reqs = _card(obj_id, x, y, pw, ph)
    reqs[1] = _fill(obj_id, colour_name)
    reqs.append(_text(obj_id, label))
    reqs.append(_text_style(obj_id, FONT_BODY, 9, text_colour, bold=True))
    return reqs


def _slide_bg(slide_obj_id: str, colour_name: str) -> dict:
    return {"updatePageProperties": {
        "objectId": slide_obj_id,
        "pageProperties": {
            "pageBackgroundFill": {"solidFill": {"color": _colour(colour_name)}}
        },
        "fields": "pageBackgroundFill",
    }}


def _inject_slide_id(reqs: list[dict], slide_id: str) -> list[dict]:
    import json
    raw = json.dumps(reqs).replace("{{SLIDE_ID}}", slide_id)
    import json as _j
    return _j.loads(raw)


# ── Templates ──────────────────────────────────────────────────────────────

def build_title_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    # Triangle decoration bottom-right
    tri_id = f"{slide_id}_tri"
    reqs.append(_rect(tri_id, int(W * 0.55), int(H * 0.35), int(W * 0.45), int(H * 0.65), "TRIANGLE"))
    reqs.append(_fill(tri_id, "coral"))
    reqs.append(_no_border(tri_id))
    # Date label
    date_id = f"{slide_id}_date"
    reqs.append(_rect(date_id, int(INCH * 0.6), int(INCH * 0.7), int(INCH * 3), int(INCH * 0.35)))
    reqs.append(_fill(date_id, "cream"))
    reqs.append(_no_border(date_id))
    date_text = content.get("date", "")
    if date_text:
        reqs.append(_text(date_id, date_text.upper()))
        reqs.append(_text_style(date_id, FONT_BODY, 10, "lime", bold=True))
    # Title
    title_id = f"{slide_id}_title"
    reqs.append(_rect(title_id, int(INCH * 0.6), int(INCH * 1.2), int(INCH * 5), int(INCH * 2.5)))
    reqs.append(_fill(title_id, "cream"))
    reqs.append(_no_border(title_id))
    title_text = content.get("title", "")
    reqs.append(_text(title_id, title_text))
    reqs.append(_text_style(title_id, FONT_HEADING, 60, "text", bold=True))
    return _inject_slide_id(reqs, slide_id)


def build_agenda_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "white")]
    # "Agenda" heading
    head_id = f"{slide_id}_head"
    reqs.append(_rect(head_id, int(INCH * 1.5), int(INCH * 0.5), int(INCH * 6), int(INCH * 1.2)))
    reqs.append(_fill(head_id, "white"))
    reqs.append(_no_border(head_id))
    reqs.append(_text(head_id, content.get("heading", "Agenda")))
    reqs.append(_text_style(head_id, FONT_HEADING, 72, "text", italic=True))
    # Hotpink underline
    ul_id = f"{slide_id}_ul"
    reqs.append(_rect(ul_id, int(INCH * 1.5), int(INCH * 1.75), int(INCH * 2.5), 228_600))
    reqs.append(_fill(ul_id, "hotpink"))
    reqs.append(_no_border(ul_id))
    # Agenda items
    for i, item in enumerate(content.get("agenda_items", [])[:6]):
        item_id = f"{slide_id}_item{i}"
        y = int(INCH * 2.1) + i * int(INCH * 0.55)
        reqs.append(_rect(item_id, int(INCH * 1.5), y, int(INCH * 6), int(INCH * 0.5)))
        reqs.append(_fill(item_id, "white"))
        reqs.append(_no_border(item_id))
        label = item.get("title", "")
        desc  = item.get("description", "")
        full  = label + ("\n" + desc if desc else "")
        reqs.append(_text(item_id, full))
        reqs.append(_text_style(item_id, FONT_BODY, 14, "text", bold=True, start=0, end=len(label)))
        if desc:
            reqs.append(_text_style(item_id, FONT_BODY, 12, "charcoal",
                                     start=len(label) + 1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


def build_section_divider_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "blush")]
    head_id = f"{slide_id}_head"
    reqs.append(_rect(head_id, int(INCH * 1), int(INCH * 1.5), int(INCH * 7.5), int(INCH * 1.8)))
    reqs.append(_fill(head_id, "blush"))
    reqs.append(_no_border(head_id))
    reqs.append(_text(head_id, content.get("heading", "")))
    reqs.append(_text_style(head_id, FONT_HEADING, 80, "text"))
    sub_id = f"{slide_id}_sub"
    reqs.append(_rect(sub_id, int(INCH * 1), int(INCH * 3.5), int(INCH * 7.5), int(INCH * 0.5)))
    reqs.append(_fill(sub_id, "blush"))
    reqs.append(_no_border(sub_id))
    sub = content.get("subheading", "")
    if sub:
        reqs.append(_text(sub_id, sub.upper()))
        reqs.append(_text_style(sub_id, FONT_BODY, 12, "charcoal"))
    return _inject_slide_id(reqs, slide_id)


def build_metrics_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    label_id = f"{slide_id}_lbl"
    reqs.append(_rect(label_id, int(INCH * 0.6), int(INCH * 0.4), int(INCH * 4), int(INCH * 0.35)))
    reqs.append(_fill(label_id, "cream"))
    reqs.append(_no_border(label_id))
    lbl = content.get("label", "")
    if lbl:
        reqs.append(_text(label_id, lbl.upper()))
        reqs.append(_text_style(label_id, FONT_BODY, 10, "charcoal"))
    metrics = content.get("metrics", [])[:6]
    cols, card_w, card_h = 3, int(INCH * 2.6), int(INCH * 1.6)
    margin_x, margin_y = int(INCH * 0.5), int(INCH * 0.9)
    gap = int(INCH * 0.15)
    for i, m in enumerate(metrics):
        row, col = divmod(i, cols)
        x = margin_x + col * (card_w + gap)
        y = margin_y + row * (card_h + gap)
        cid = f"{slide_id}_card{i}"
        reqs.extend(_card(cid, x, y, card_w, card_h))
        name_id = f"{slide_id}_mname{i}"
        reqs.append(_rect(name_id, x + int(INCH*0.15), y + int(INCH*0.1), card_w - int(INCH*0.3), int(INCH*0.3)))
        reqs.append(_fill(name_id, "white"))
        reqs.append(_no_border(name_id))
        reqs.append(_text(name_id, m.get("name", "")))
        reqs.append(_text_style(name_id, FONT_BODY, 10, "charcoal"))
        val_id = f"{slide_id}_mval{i}"
        reqs.append(_rect(val_id, x + int(INCH*0.15), y + int(INCH*0.45), card_w - int(INCH*0.3), int(INCH*0.6)))
        reqs.append(_fill(val_id, "white"))
        reqs.append(_no_border(val_id))
        reqs.append(_text(val_id, m.get("value", "")))
        reqs.append(_text_style(val_id, FONT_HEADING, 32, "text", bold=True))
        trend = m.get("trend", "")
        if trend:
            tr_id = f"{slide_id}_mtrend{i}"
            reqs.extend(_pill(tr_id, x + int(INCH*0.15), y + int(INCH*1.15), trend,
                               "lime" if m.get("trend_up", True) else "coral"))
    return _inject_slide_id(reqs, slide_id)


def build_feature_update_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "white")]
    # NEW! badge
    if content.get("badge"):
        reqs.extend(_pill(f"{slide_id}_badge", int(INCH*0.6), int(INCH*0.5),
                           content["badge"], "lime"))
    # Title
    title_id = f"{slide_id}_title"
    reqs.append(_rect(title_id, int(INCH*0.6), int(INCH*1.0), int(INCH*4), int(INCH*1.2)))
    reqs.append(_fill(title_id, "white"))
    reqs.append(_no_border(title_id))
    reqs.append(_text(title_id, content.get("title", "")))
    reqs.append(_text_style(title_id, FONT_HEADING, 40, "text", bold=True))
    # Subtitle
    sub = content.get("subtitle", "")
    if sub:
        sub_id = f"{slide_id}_sub"
        reqs.append(_rect(sub_id, int(INCH*0.6), int(INCH*2.3), int(INCH*4), int(INCH*0.6)))
        reqs.append(_fill(sub_id, "white"))
        reqs.append(_no_border(sub_id))
        reqs.append(_text(sub_id, sub))
        reqs.append(_text_style(sub_id, FONT_BODY, 13, "charcoal"))
    # Numbered items (right column)
    for i, item in enumerate(content.get("items", [])[:3]):
        y = int(INCH * 0.5) + i * int(INCH * 1.5)
        num_id = f"{slide_id}_num{i}"
        reqs.append(_rect(num_id, int(INCH*4.9), y, int(INCH*0.7), int(INCH*1.2)))
        reqs.append(_fill(num_id, "white"))
        reqs.append(_no_border(num_id))
        reqs.append(_text(num_id, str(i + 1)))
        reqs.append(_text_style(num_id, FONT_HEADING, 80, "coral"))
        card_id = f"{slide_id}_card{i}"
        reqs.extend(_card(card_id, int(INCH*5.6), y, int(INCH*3.1), int(INCH*1.3)))
        status = item.get("status", "")
        if status:
            reqs.extend(_pill(f"{slide_id}_live{i}", int(INCH*5.7), y + int(INCH*0.1),
                               status, "lime"))
        text_id = f"{slide_id}_ctitle{i}"
        reqs.append(_rect(text_id, int(INCH*5.7), y + int(INCH*0.45), int(INCH*2.9), int(INCH*0.85)))
        reqs.append(_fill(text_id, "white"))
        reqs.append(_no_border(text_id))
        item_title = item.get("title", "")
        item_desc  = item.get("description", "")
        full = item_title + ("\n" + item_desc if item_desc else "")
        reqs.append(_text(text_id, full))
        reqs.append(_text_style(text_id, FONT_BODY, 13, "text", bold=True,
                                 start=0, end=len(item_title)))
        if item_desc:
            reqs.append(_text_style(text_id, FONT_BODY, 11, "charcoal",
                                     start=len(item_title)+1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


def build_demo_presenter_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    lbl_id = f"{slide_id}_lbl"
    reqs.append(_rect(lbl_id, int(INCH*0.6), int(INCH*0.5), int(INCH*2), int(INCH*0.3)))
    reqs.append(_fill(lbl_id, "cream"))
    reqs.append(_no_border(lbl_id))
    reqs.append(_text(lbl_id, content.get("label", "DEMO TIME")))
    reqs.append(_text_style(lbl_id, FONT_BODY, 10, "charcoal"))
    title_id = f"{slide_id}_title"
    reqs.append(_rect(title_id, int(INCH*0.6), int(INCH*1.0), int(INCH*4.5), int(INCH*1.5)))
    reqs.append(_fill(title_id, "cream"))
    reqs.append(_no_border(title_id))
    reqs.append(_text(title_id, content.get("title", "")))
    reqs.append(_text_style(title_id, FONT_HEADING, 48, "text", bold=True))
    if content.get("presenter"):
        pres_id = f"{slide_id}_pres"
        reqs.append(_rect(pres_id, int(INCH*0.6), int(INCH*2.7), int(INCH*3), int(INCH*0.4)))
        reqs.append(_fill(pres_id, "cream"))
        reqs.append(_no_border(pres_id))
        reqs.append(_text(pres_id, content["presenter"]))
        reqs.append(_text_style(pres_id, FONT_BODY, 16, "charcoal"))
    chart_id = f"{slide_id}_chart"
    reqs.extend(_card(chart_id, int(INCH*5), int(INCH*0.5), int(INCH*3.7), int(INCH*4.2)))
    return _inject_slide_id(reqs, slide_id)


def build_team_roadmap_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "blush")]
    sec_id = f"{slide_id}_sec"
    reqs.append(_rect(sec_id, int(INCH*0.6), int(INCH*0.4), int(INCH*3), int(INCH*0.3)))
    reqs.append(_fill(sec_id, "blush"))
    reqs.append(_no_border(sec_id))
    reqs.append(_text(sec_id, content.get("section_label", "Q2 FOR TECH")))
    reqs.append(_text_style(sec_id, FONT_BODY, 10, "charcoal"))
    cards = content.get("cards", [])[:4]
    positions = [
        (int(INCH*0.5), int(INCH*0.9)),
        (int(INCH*5.1), int(INCH*0.9)),
        (int(INCH*0.5), int(INCH*3.0)),
        (int(INCH*5.1), int(INCH*3.0)),
    ]
    team_colours = ["lime", "hotpink", "coral", "charcoal"]
    cw, ch = int(INCH*4.3), int(INCH*1.9)
    for i, (card_data, pos) in enumerate(zip(cards, positions)):
        cid = f"{slide_id}_rcard{i}"
        reqs.extend(_card(cid, pos[0], pos[1], cw, ch))
        tc = team_colours[i % len(team_colours)]
        if card_data.get("team"):
            reqs.extend(_pill(f"{slide_id}_rpill{i}",
                               pos[0] + int(INCH*0.15), pos[1] + int(INCH*0.1),
                               card_data["team"], tc,
                               "white" if tc in ("hotpink","charcoal") else "text"))
        tid = f"{slide_id}_rtitle{i}"
        reqs.append(_rect(tid, pos[0]+int(INCH*0.15), pos[1]+int(INCH*0.55), cw-int(INCH*0.3), int(INCH*0.6)))
        reqs.append(_fill(tid, "white"))
        reqs.append(_no_border(tid))
        ct = card_data.get("title","")
        cd = card_data.get("description","")
        full = ct + ("\n"+cd if cd else "")
        reqs.append(_text(tid, full))
        reqs.append(_text_style(tid, FONT_BODY, 14, "text", bold=True, start=0, end=len(ct)))
        if cd:
            reqs.append(_text_style(tid, FONT_BODY, 11, "charcoal",
                                     start=len(ct)+1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


def build_release_list_slide(slide_id: str, content: dict) -> list[dict]:
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    lbl_id = f"{slide_id}_lbl"
    reqs.append(_rect(lbl_id, int(INCH*0.6), int(INCH*0.4), int(INCH*2.5), int(INCH*0.3)))
    reqs.append(_fill(lbl_id, "cream"))
    reqs.append(_no_border(lbl_id))
    reqs.append(_text(lbl_id, content.get("label", "UPCOMING")))
    reqs.append(_text_style(lbl_id, FONT_BODY, 10, "charcoal"))
    if content.get("title"):
        ht_id = f"{slide_id}_htitle"
        reqs.append(_rect(ht_id, int(INCH*0.6), int(INCH*0.8), int(INCH*4), int(INCH*1.0)))
        reqs.append(_fill(ht_id, "cream"))
        reqs.append(_no_border(ht_id))
        reqs.append(_text(ht_id, content["title"]))
        reqs.append(_text_style(ht_id, FONT_HEADING, 40, "text", bold=True))
    for i, item in enumerate(content.get("items", [])[:3]):
        y = int(INCH*0.7) + i * int(INCH*1.45)
        num_id = f"{slide_id}_rnum{i}"
        reqs.append(_rect(num_id, int(INCH*4.8), y, int(INCH*0.8), int(INCH*1.3)))
        reqs.append(_fill(num_id, "cream"))
        reqs.append(_no_border(num_id))
        reqs.append(_text(num_id, str(i+1)))
        reqs.append(_text_style(num_id, FONT_HEADING, 120, "coral"))
        cid = f"{slide_id}_rcard{i}"
        reqs.extend(_card(cid, int(INCH*5.7), y, int(INCH*3.0), int(INCH*1.3)))
        if item.get("timeline"):
            reqs.extend(_pill(f"{slide_id}_rpill{i}",
                               int(INCH*5.85), y+int(INCH*0.08),
                               item["timeline"], "blush"))
        tid = f"{slide_id}_rtitle{i}"
        reqs.append(_rect(tid, int(INCH*5.85), y+int(INCH*0.42), int(INCH*2.8), int(INCH*0.85)))
        reqs.append(_fill(tid, "white"))
        reqs.append(_no_border(tid))
        it = item.get("title","")
        id_ = item.get("description","")
        full = it + ("\n"+id_ if id_ else "")
        reqs.append(_text(tid, full))
        reqs.append(_text_style(tid, FONT_BODY, 13, "text", bold=True, start=0, end=len(it)))
        if id_:
            reqs.append(_text_style(tid, FONT_BODY, 11, "charcoal",
                                     start=len(it)+1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


# ── Master dispatcher ──────────────────────────────────────────────────────

_TEMPLATES = {
    "title":           build_title_slide,
    "agenda":          build_agenda_slide,
    "section_divider": build_section_divider_slide,
    "metrics_stats":   build_metrics_slide,
    "feature_update":  build_feature_update_slide,
    "demo_presenter":  build_demo_presenter_slide,
    "team_roadmap":    build_team_roadmap_slide,
    "release_list":    build_release_list_slide,
}


def build_slide_requests(slide_id: str, template_name: str,
                         content: dict) -> list[dict]:
    fn = _TEMPLATES.get(template_name)
    if fn is None:
        raise ValueError(f"Unknown template '{template_name}'. "
                         f"Choose from: {list(_TEMPLATES)}")
    return fn(slide_id, content)
