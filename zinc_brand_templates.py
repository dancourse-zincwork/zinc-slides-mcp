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
          shape: str = "RECTANGLE") -> dict:
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


def _para_align(obj_id: str, alignment: str = "START") -> dict:
    return {"updateParagraphStyle": {
        "objectId": obj_id,
        "textRange": {"type": "ALL"},
        "style": {"alignment": alignment},
        "fields": "alignment",
    }}


def _card(obj_id: str, x: int, y: int, w: int, h: int) -> list[dict]:
    return [
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


def _heading_with_underline(slide_id: str, heading: str, y_inch: float,
                             font_size: int = 40) -> list[dict]:
    """Left-aligned heading + hotpink underline bar."""
    reqs = []
    hid = f"{slide_id}_h"
    reqs.append(_rect(hid, int(INCH * 0.6), int(INCH * y_inch),
                      int(INCH * 8.4), int(INCH * 0.9)))
    reqs.append(_fill(hid, "cream"))
    reqs.append(_no_border(hid))
    reqs.append(_text(hid, heading))
    reqs.append(_text_style(hid, FONT_HEADING, font_size, "text", bold=True))
    reqs.append(_para_align(hid, "START"))
    ul_id = f"{slide_id}_ul"
    reqs.append(_rect(ul_id, int(INCH * 0.6), int(INCH * (y_inch + 0.85)),
                      int(INCH * 2.5), 228_600))
    reqs.append(_fill(ul_id, "hotpink"))
    reqs.append(_no_border(ul_id))
    return reqs


def _inject_slide_id(reqs: list[dict], slide_id: str) -> list[dict]:
    import json
    return json.loads(json.dumps(reqs).replace("{{SLIDE_ID}}", slide_id))


# ── Templates ──────────────────────────────────────────────────────────────

def build_title_slide(slide_id: str, content: dict) -> list[dict]:
    """Opening / title slide. content: {title, subtitle?, date?}"""
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    tri_id = f"{slide_id}_tri"
    reqs.append(_rect(tri_id, int(W * 0.55), int(H * 0.35),
                      int(W * 0.45), int(H * 0.65), "TRIANGLE"))
    reqs.append(_fill(tri_id, "coral"))
    reqs.append(_no_border(tri_id))
    if content.get("date"):
        date_id = f"{slide_id}_date"
        reqs.append(_rect(date_id, int(INCH * 0.6), int(INCH * 0.7),
                          int(INCH * 3.5), int(INCH * 0.35)))
        reqs.append(_fill(date_id, "cream"))
        reqs.append(_no_border(date_id))
        reqs.append(_text(date_id, content["date"].upper()))
        reqs.append(_text_style(date_id, FONT_BODY, 10, "lime", bold=True))
    title_id = f"{slide_id}_title"
    reqs.append(_rect(title_id, int(INCH * 0.6), int(INCH * 1.2),
                      int(INCH * 5.5), int(INCH * 2.5)))
    reqs.append(_fill(title_id, "cream"))
    reqs.append(_no_border(title_id))
    reqs.append(_text(title_id, content.get("title", "")))
    reqs.append(_text_style(title_id, FONT_HEADING, 60, "text", bold=True))
    if content.get("subtitle"):
        sub_id = f"{slide_id}_sub"
        reqs.append(_rect(sub_id, int(INCH * 0.6), int(INCH * 3.6),
                          int(INCH * 5), int(INCH * 0.5)))
        reqs.append(_fill(sub_id, "cream"))
        reqs.append(_no_border(sub_id))
        reqs.append(_text(sub_id, content["subtitle"]))
        reqs.append(_text_style(sub_id, FONT_BODY, 16, "charcoal"))
    return _inject_slide_id(reqs, slide_id)


def build_content_slide(slide_id: str, content: dict) -> list[dict]:
    """General content slide (title + body). content: {heading, body}"""
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    reqs.extend(_heading_with_underline(slide_id, content.get("heading", ""), 0.4))
    body_id = f"{slide_id}_body"
    reqs.append(_rect(body_id, int(INCH * 0.6), int(INCH * 1.5),
                      int(INCH * 8.4), int(INCH * 3.2)))
    reqs.append(_fill(body_id, "cream"))
    reqs.append(_no_border(body_id))
    body_text = content.get("body", "")
    reqs.append(_text(body_id, body_text))
    reqs.append(_text_style(body_id, FONT_BODY, 16, "text"))
    reqs.append(_para_align(body_id, "START"))
    return _inject_slide_id(reqs, slide_id)


def build_two_column_slide(slide_id: str, content: dict) -> list[dict]:
    """Two-column layout. content: {heading, left_heading?, left_body, right_heading?, right_body}"""
    reqs: list[dict] = [_slide_bg(slide_id, "white")]
    head_id = f"{slide_id}_h"
    reqs.append(_rect(head_id, int(INCH * 0.6), int(INCH * 0.4),
                      int(INCH * 8.4), int(INCH * 0.8)))
    reqs.append(_fill(head_id, "white"))
    reqs.append(_no_border(head_id))
    reqs.append(_text(head_id, content.get("heading", "")))
    reqs.append(_text_style(head_id, FONT_HEADING, 36, "text", bold=True))
    reqs.append(_para_align(head_id, "START"))
    ul_id = f"{slide_id}_ul"
    reqs.append(_rect(ul_id, int(INCH * 0.6), int(INCH * 1.2),
                      int(INCH * 2.5), 228_600))
    reqs.append(_fill(ul_id, "hotpink"))
    reqs.append(_no_border(ul_id))
    col_y = int(INCH * 1.4)
    col_h = int(INCH * 3.3)
    for side, x_inch, key_h, key_b in [
        ("l", 0.6, "left_heading",  "left_body"),
        ("r", 5.0, "right_heading", "right_body"),
    ]:
        if content.get(key_h):
            ch_id = f"{slide_id}_{side}h"
            reqs.append(_rect(ch_id, int(INCH * x_inch), col_y,
                              int(INCH * 3.8), int(INCH * 0.45)))
            reqs.append(_fill(ch_id, "white"))
            reqs.append(_no_border(ch_id))
            reqs.append(_text(ch_id, content[key_h]))
            reqs.append(_text_style(ch_id, FONT_BODY, 14, "text", bold=True))
        cb_id = f"{slide_id}_{side}b"
        body_y = col_y + (int(INCH * 0.5) if content.get(key_h) else 0)
        reqs.append(_rect(cb_id, int(INCH * x_inch), body_y,
                          int(INCH * 3.8), col_h))
        reqs.append(_fill(cb_id, "white"))
        reqs.append(_no_border(cb_id))
        reqs.append(_text(cb_id, content.get(key_b, "")))
        reqs.append(_text_style(cb_id, FONT_BODY, 13, "charcoal"))
        reqs.append(_para_align(cb_id, "START"))
    return _inject_slide_id(reqs, slide_id)


def build_section_slide(slide_id: str, content: dict) -> list[dict]:
    """Section break / chapter divider. content: {heading, subheading?}"""
    reqs: list[dict] = [_slide_bg(slide_id, "blush")]
    head_id = f"{slide_id}_head"
    reqs.append(_rect(head_id, int(INCH * 1), int(INCH * 0.8),
                      int(INCH * 7.5), int(INCH * 3.0)))
    reqs.append(_fill(head_id, "blush"))
    reqs.append(_no_border(head_id))
    reqs.append(_text(head_id, content.get("heading", "")))
    reqs.append(_text_style(head_id, FONT_HEADING, 80, "text"))
    reqs.append(_para_align(head_id, "CENTER"))
    if content.get("subheading"):
        sub_id = f"{slide_id}_sub"
        reqs.append(_rect(sub_id, int(INCH * 1), int(INCH * 4.1),
                          int(INCH * 7.5), int(INCH * 0.5)))
        reqs.append(_fill(sub_id, "blush"))
        reqs.append(_no_border(sub_id))
        reqs.append(_text(sub_id, content["subheading"].upper()))
        reqs.append(_text_style(sub_id, FONT_BODY, 12, "charcoal"))
        reqs.append(_para_align(sub_id, "CENTER"))
    return _inject_slide_id(reqs, slide_id)


def build_big_number_slide(slide_id: str, content: dict) -> list[dict]:
    """Single large stat callout. content: {number, label, context?}"""
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    num_id = f"{slide_id}_num"
    reqs.append(_rect(num_id, int(INCH * 1), int(INCH * 0.6),
                      int(INCH * 7.5), int(INCH * 2.8)))
    reqs.append(_fill(num_id, "cream"))
    reqs.append(_no_border(num_id))
    reqs.append(_text(num_id, content.get("number", "")))
    reqs.append(_text_style(num_id, FONT_HEADING, 120, "coral", bold=True))
    reqs.append(_para_align(num_id, "CENTER"))
    lbl_id = f"{slide_id}_lbl"
    reqs.append(_rect(lbl_id, int(INCH * 1), int(INCH * 3.3),
                      int(INCH * 7.5), int(INCH * 0.65)))
    reqs.append(_fill(lbl_id, "cream"))
    reqs.append(_no_border(lbl_id))
    reqs.append(_text(lbl_id, content.get("label", "")))
    reqs.append(_text_style(lbl_id, FONT_HEADING, 28, "text"))
    reqs.append(_para_align(lbl_id, "CENTER"))
    if content.get("context"):
        ctx_id = f"{slide_id}_ctx"
        reqs.append(_rect(ctx_id, int(INCH * 1), int(INCH * 4.0),
                          int(INCH * 7.5), int(INCH * 0.5)))
        reqs.append(_fill(ctx_id, "cream"))
        reqs.append(_no_border(ctx_id))
        reqs.append(_text(ctx_id, content["context"]))
        reqs.append(_text_style(ctx_id, FONT_BODY, 12, "charcoal"))
        reqs.append(_para_align(ctx_id, "CENTER"))
    return _inject_slide_id(reqs, slide_id)


def build_blank_slide(slide_id: str, content: dict) -> list[dict]:
    """Blank cream slide — for custom image/content layouts. content: {}"""
    return _inject_slide_id([_slide_bg(slide_id, "cream")], slide_id)


def build_stat_cards_slide(slide_id: str, content: dict) -> list[dict]:
    """Grid of stat cards with trend indicators. content: {label?, metrics: [{name, value, trend?, trend_up?}]}"""
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    if content.get("label"):
        lbl_id = f"{slide_id}_lbl"
        reqs.append(_rect(lbl_id, int(INCH * 0.6), int(INCH * 0.4),
                          int(INCH * 4), int(INCH * 0.35)))
        reqs.append(_fill(lbl_id, "cream"))
        reqs.append(_no_border(lbl_id))
        reqs.append(_text(lbl_id, content["label"].upper()))
        reqs.append(_text_style(lbl_id, FONT_BODY, 10, "charcoal"))
    metrics = content.get("metrics", [])[:6]
    cols, card_w, card_h = 3, int(INCH * 2.6), int(INCH * 1.6)
    margin_x, margin_y, gap = int(INCH * 0.5), int(INCH * 0.9), int(INCH * 0.15)
    for i, m in enumerate(metrics):
        row, col = divmod(i, cols)
        x = margin_x + col * (card_w + gap)
        y = margin_y + row * (card_h + gap)
        reqs.extend(_card(f"{slide_id}_card{i}", x, y, card_w, card_h))
        name_id = f"{slide_id}_mname{i}"
        reqs.append(_rect(name_id, x + int(INCH * 0.15), y + int(INCH * 0.1),
                          card_w - int(INCH * 0.3), int(INCH * 0.3)))
        reqs.append(_fill(name_id, "white"))
        reqs.append(_no_border(name_id))
        reqs.append(_text(name_id, m.get("name", "")))
        reqs.append(_text_style(name_id, FONT_BODY, 10, "charcoal"))
        val_id = f"{slide_id}_mval{i}"
        reqs.append(_rect(val_id, x + int(INCH * 0.15), y + int(INCH * 0.45),
                          card_w - int(INCH * 0.3), int(INCH * 0.6)))
        reqs.append(_fill(val_id, "white"))
        reqs.append(_no_border(val_id))
        reqs.append(_text(val_id, m.get("value", "")))
        reqs.append(_text_style(val_id, FONT_HEADING, 32, "text", bold=True))
        if m.get("trend"):
            reqs.extend(_pill(f"{slide_id}_mtrend{i}",
                               x + int(INCH * 0.15), y + int(INCH * 1.15),
                               m["trend"],
                               "lime" if m.get("trend_up", True) else "coral"))
    return _inject_slide_id(reqs, slide_id)


def build_numbered_items_slide(slide_id: str, content: dict) -> list[dict]:
    """Numbered list with optional status badges. content: {badge?, title, subtitle?, items: [{title, description?, status?}]}"""
    reqs: list[dict] = [_slide_bg(slide_id, "white")]
    if content.get("badge"):
        reqs.extend(_pill(f"{slide_id}_badge",
                           int(INCH * 0.6), int(INCH * 0.5),
                           content["badge"], "lime"))
    title_id = f"{slide_id}_title"
    reqs.append(_rect(title_id, int(INCH * 0.6), int(INCH * 1.0),
                      int(INCH * 4), int(INCH * 1.2)))
    reqs.append(_fill(title_id, "white"))
    reqs.append(_no_border(title_id))
    reqs.append(_text(title_id, content.get("title", "")))
    reqs.append(_text_style(title_id, FONT_HEADING, 40, "text", bold=True))
    if content.get("subtitle"):
        sub_id = f"{slide_id}_sub"
        reqs.append(_rect(sub_id, int(INCH * 0.6), int(INCH * 2.3),
                          int(INCH * 4), int(INCH * 0.6)))
        reqs.append(_fill(sub_id, "white"))
        reqs.append(_no_border(sub_id))
        reqs.append(_text(sub_id, content["subtitle"]))
        reqs.append(_text_style(sub_id, FONT_BODY, 13, "charcoal"))
    for i, item in enumerate(content.get("items", [])[:3]):
        y = int(INCH * 0.5) + i * int(INCH * 1.5)
        num_id = f"{slide_id}_num{i}"
        reqs.append(_rect(num_id, int(INCH * 4.9), y,
                          int(INCH * 0.7), int(INCH * 1.2)))
        reqs.append(_fill(num_id, "white"))
        reqs.append(_no_border(num_id))
        reqs.append(_text(num_id, str(i + 1)))
        reqs.append(_text_style(num_id, FONT_HEADING, 80, "coral"))
        card_id = f"{slide_id}_card{i}"
        reqs.extend(_card(card_id, int(INCH * 5.6), y,
                          int(INCH * 3.1), int(INCH * 1.3)))
        if item.get("status"):
            reqs.extend(_pill(f"{slide_id}_live{i}",
                               int(INCH * 5.7), y + int(INCH * 0.1),
                               item["status"], "lime"))
        text_id = f"{slide_id}_ctitle{i}"
        reqs.append(_rect(text_id, int(INCH * 5.7), y + int(INCH * 0.45),
                          int(INCH * 2.9), int(INCH * 0.85)))
        reqs.append(_fill(text_id, "white"))
        reqs.append(_no_border(text_id))
        it = item.get("title", "")
        id_ = item.get("description", "")
        full = it + ("\n" + id_ if id_ else "")
        reqs.append(_text(text_id, full))
        reqs.append(_text_style(text_id, FONT_BODY, 13, "text", bold=True,
                                 start=0, end=len(it)))
        if id_:
            reqs.append(_text_style(text_id, FONT_BODY, 11, "charcoal",
                                     start=len(it) + 1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


def build_card_grid_slide(slide_id: str, content: dict) -> list[dict]:
    """2×2 card grid with coloured pill labels. content: {label?, cards: [{label, title, description?}]}"""
    reqs: list[dict] = [_slide_bg(slide_id, "blush")]
    if content.get("label"):
        sec_id = f"{slide_id}_sec"
        reqs.append(_rect(sec_id, int(INCH * 0.6), int(INCH * 0.4),
                          int(INCH * 4), int(INCH * 0.3)))
        reqs.append(_fill(sec_id, "blush"))
        reqs.append(_no_border(sec_id))
        reqs.append(_text(sec_id, content["label"]))
        reqs.append(_text_style(sec_id, FONT_BODY, 10, "charcoal"))
    cards = content.get("cards", [])[:4]
    positions = [
        (int(INCH * 0.5), int(INCH * 0.9)),
        (int(INCH * 5.1), int(INCH * 0.9)),
        (int(INCH * 0.5), int(INCH * 3.0)),
        (int(INCH * 5.1), int(INCH * 3.0)),
    ]
    pill_colours = ["lime", "hotpink", "coral", "charcoal"]
    cw, ch = int(INCH * 4.3), int(INCH * 1.9)
    for i, (card_data, pos) in enumerate(zip(cards, positions)):
        reqs.extend(_card(f"{slide_id}_rcard{i}", pos[0], pos[1], cw, ch))
        tc = pill_colours[i % len(pill_colours)]
        if card_data.get("label"):
            reqs.extend(_pill(f"{slide_id}_rpill{i}",
                               pos[0] + int(INCH * 0.15), pos[1] + int(INCH * 0.1),
                               card_data["label"], tc,
                               "white" if tc in ("hotpink", "charcoal") else "text"))
        tid = f"{slide_id}_rtitle{i}"
        reqs.append(_rect(tid, pos[0] + int(INCH * 0.15), pos[1] + int(INCH * 0.55),
                          cw - int(INCH * 0.3), int(INCH * 0.6)))
        reqs.append(_fill(tid, "white"))
        reqs.append(_no_border(tid))
        ct = card_data.get("title", "")
        cd = card_data.get("description", "")
        full = ct + ("\n" + cd if cd else "")
        reqs.append(_text(tid, full))
        reqs.append(_text_style(tid, FONT_BODY, 14, "text", bold=True,
                                 start=0, end=len(ct)))
        if cd:
            reqs.append(_text_style(tid, FONT_BODY, 11, "charcoal",
                                     start=len(ct) + 1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


def build_timeline_slide(slide_id: str, content: dict) -> list[dict]:
    """Numbered list with timeline/date pills. content: {label?, title?, items: [{title, description?, timeline?}]}"""
    reqs: list[dict] = [_slide_bg(slide_id, "cream")]
    if content.get("label"):
        lbl_id = f"{slide_id}_lbl"
        reqs.append(_rect(lbl_id, int(INCH * 0.6), int(INCH * 0.4),
                          int(INCH * 2.5), int(INCH * 0.3)))
        reqs.append(_fill(lbl_id, "cream"))
        reqs.append(_no_border(lbl_id))
        reqs.append(_text(lbl_id, content["label"]))
        reqs.append(_text_style(lbl_id, FONT_BODY, 10, "charcoal"))
    if content.get("title"):
        ht_id = f"{slide_id}_htitle"
        reqs.append(_rect(ht_id, int(INCH * 0.6), int(INCH * 0.8),
                          int(INCH * 4), int(INCH * 1.0)))
        reqs.append(_fill(ht_id, "cream"))
        reqs.append(_no_border(ht_id))
        reqs.append(_text(ht_id, content["title"]))
        reqs.append(_text_style(ht_id, FONT_HEADING, 40, "text", bold=True))
    for i, item in enumerate(content.get("items", [])[:3]):
        y = int(INCH * 0.7) + i * int(INCH * 1.45)
        num_id = f"{slide_id}_rnum{i}"
        reqs.append(_rect(num_id, int(INCH * 4.8), y,
                          int(INCH * 0.8), int(INCH * 1.3)))
        reqs.append(_fill(num_id, "cream"))
        reqs.append(_no_border(num_id))
        reqs.append(_text(num_id, str(i + 1)))
        reqs.append(_text_style(num_id, FONT_HEADING, 120, "coral"))
        reqs.extend(_card(f"{slide_id}_rcard{i}",
                          int(INCH * 5.7), y, int(INCH * 3.0), int(INCH * 1.3)))
        if item.get("timeline"):
            reqs.extend(_pill(f"{slide_id}_rpill{i}",
                               int(INCH * 5.85), y + int(INCH * 0.08),
                               item["timeline"], "blush"))
        tid = f"{slide_id}_rtitle{i}"
        reqs.append(_rect(tid, int(INCH * 5.85), y + int(INCH * 0.42),
                          int(INCH * 2.8), int(INCH * 0.85)))
        reqs.append(_fill(tid, "white"))
        reqs.append(_no_border(tid))
        it = item.get("title", "")
        id_ = item.get("description", "")
        full = it + ("\n" + id_ if id_ else "")
        reqs.append(_text(tid, full))
        reqs.append(_text_style(tid, FONT_BODY, 13, "text", bold=True,
                                 start=0, end=len(it)))
        if id_:
            reqs.append(_text_style(tid, FONT_BODY, 11, "charcoal",
                                     start=len(it) + 1, end=len(full)))
    return _inject_slide_id(reqs, slide_id)


# ── Master dispatcher ──────────────────────────────────────────────────────

_TEMPLATES = {
    "title":          build_title_slide,
    "content":        build_content_slide,
    "two_column":     build_two_column_slide,
    "section":        build_section_slide,
    "big_number":     build_big_number_slide,
    "blank":          build_blank_slide,
    "stat_cards":     build_stat_cards_slide,
    "numbered_items": build_numbered_items_slide,
    "card_grid":      build_card_grid_slide,
    "timeline":       build_timeline_slide,
}

TEMPLATE_NAMES = list(_TEMPLATES.keys())


def build_slide_requests(slide_id: str, template_name: str,
                         content: dict) -> list[dict]:
    fn = _TEMPLATES.get(template_name)
    if fn is None:
        raise ValueError(
            f"Unknown template '{template_name}'. Choose from: {TEMPLATE_NAMES}"
        )
    return fn(slide_id, content)
