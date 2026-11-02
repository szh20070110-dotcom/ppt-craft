# -*- coding: utf-8 -*-
"""用 python-pptx 生成《南京三日游》12 页可编辑演示文稿。"""

import os
import sys

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

import deck_content as C

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, f"{C.TOPIC}.pptx")

SW, SH = 13.333, 7.5
LEFT = PP_ALIGN.LEFT
CENTER = PP_ALIGN.CENTER
RIGHT = PP_ALIGN.RIGHT
TOP = MSO_ANCHOR.TOP
MIDDLE = MSO_ANCHOR.MIDDLE


def rgb(value):
    value = value.lstrip("#")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def set_alpha(shape, color, alpha):
    """给纯色填充加透明度，alpha 取 0-100。"""
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(color)
    solid = shape.fill._xPr.find(qn("a:solidFill"))
    srgb = solid.find(qn("a:srgbClr"))
    node = etree.SubElement(srgb, qn("a:alpha"))
    node.set("val", str(int(alpha * 1000)))


def no_line(shape):
    shape.line.fill.background()
    shape.shadow.inherit = False


def add_rect(slide, x, y, w, h, color=None, alpha=None, shape=MSO_SHAPE.RECTANGLE,
             radius=None, name="Decor"):
    shp = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if color:
        if alpha is None:
            shp.fill.solid()
            shp.fill.fore_color.rgb = rgb(color)
        else:
            set_alpha(shp, color, alpha)
    else:
        shp.fill.background()
    no_line(shp)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        shp.adjustments[0] = radius
    shp.name = name
    return shp


def style_run(run, size, color, bold=False, font=C.BODY_FONT, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)
    run.font.name = font
    rpr = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        node = rpr.find(qn(tag))
        if node is None:
            node = etree.SubElement(rpr, qn(tag))
        node.set("typeface", font)


def add_text(slide, x, y, w, h, paragraphs, name="Body", anchor=TOP, align=LEFT,
             margins=(0, 0, 0, 0), line_spacing=1.2):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    box.name = name
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left, tf.margin_right, tf.margin_top, tf.margin_bottom = [
        Inches(v) for v in margins
    ]
    for i, item in enumerate(paragraphs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = item.get("align", align)
        p.line_spacing = item.get("line_spacing", line_spacing)
        if "space_before" in item:
            p.space_before = Pt(item["space_before"])
        p.space_after = Pt(item.get("space_after", 0))
        run = p.add_run()
        run.text = item["text"]
        style_run(
            run,
            item.get("size", 14),
            item.get("color", C.COLORS["ink"]),
            item.get("bold", False),
            item.get("font", C.BODY_FONT),
            item.get("italic", False),
        )
    return box


def set_title(slide, text, x, y, w, h, size=36, color=None, align=LEFT,
              font=C.TITLE_FONT, anchor=MIDDLE, bold=True):
    ph = slide.shapes.title
    ph.left, ph.top, ph.width, ph.height = Inches(x), Inches(y), Inches(w), Inches(h)
    tf = ph.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = 1.05
    run = p.add_run()
    run.text = text
    style_run(run, size, color or C.COLORS["ink"], bold=bold, font=font)
    ph.name = "Title"


def add_picture(slide, filename, x, y, w, h, name="Photo"):
    path = os.path.join(ASSETS, filename)
    pic = slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w), Inches(h))
    iw, ih = pic.image.size
    target, actual = w / h, iw / ih
    if actual > target:
        crop = (1 - target / actual) / 2
        pic.crop_left = crop
        pic.crop_right = crop
    else:
        crop = (1 - actual / target) / 2
        pic.crop_top = crop
        pic.crop_bottom = crop
    pic.name = name
    return pic


def new_slide(prs, bg):
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = rgb(bg)
    return slide


def footer(slide, n, color=None, rule=True):
    col = color or C.COLORS["muted"]
    if rule:
        add_rect(slide, 0.75, 7.07, 11.83, 0.008, C.COLORS[ "line"], name="FooterRule")
    add_text(slide, 0.75, 7.16, 7.0, 0.24,
             [{"text": "南京三日游 · 2026 旅行提案", "size": 9.5, "color": col}],
             name="Footer")
    add_text(slide, 10.6, 7.16, 1.98, 0.24,
             [{"text": f"{n:02d} / {C.TOTAL_PAGES:02d}", "size": 9.5, "color": col,
               "align": RIGHT}], name="Footer", align=RIGHT)


def caption(slide, text, x, y, w, color=None, align=LEFT):
    add_text(slide, x, y, w, 0.22,
             [{"text": text, "size": 9.5, "color": color or C.COLORS["muted"],
               "align": align}], name="Caption", align=align)


def stat_row(slide, stats, x, y, width=2.0, color=None, label_color=None):
    for i, (value, label) in enumerate(stats):
        bx = x + i * width
        add_text(slide, bx, y, width - 0.15, 0.45,
                 [{"text": value, "size": 25, "bold": True, "font": C.TITLE_FONT,
                   "color": color or C.COLORS["red"]}], name="Stat")
        add_text(slide, bx, y + 0.43, width - 0.15, 0.24,
                 [{"text": label, "size": 11, "color": label_color or C.COLORS["muted"]}],
                 name="Stat")


def sections(slide, items, x, y, w, dark=False, gap=1.1):
    heading_color = C.COLORS["white"] if dark else C.COLORS["ink"]
    body_color = C.COLORS["white_soft"] if dark else C.COLORS["muted"]
    line_color = "#3B4B42" if dark else C.COLORS["line"]
    for i, item in enumerate(items):
        by = y + i * gap
        add_text(slide, x, by, w, 0.24,
                 [{"text": item["label"], "size": 11, "bold": True,
                   "color": C.COLORS["gold"]}], name="Kicker")
        add_text(slide, x, by + 0.24, w, 0.3,
                 [{"text": item["heading"], "size": 15.5, "bold": True,
                   "color": heading_color}], name="Body")
        add_text(slide, x, by + 0.58, w, 0.42,
                 [{"text": item["body"], "size": 12.5, "color": body_color,
                   "line_spacing": 1.3}], name="Body")
        if i < len(items) - 1:
            add_rect(slide, x, by + gap - 0.14, w - 0.15, 0.008, line_color)


# ---------------------------------------------------------------- pages

def page_cover(prs, p):
    s = new_slide(prs, C.COLORS["green_deep"])
    add_picture(s, p["image"], 0, 0, SW, SH)
    add_rect(s, 0, 0, SW, SH, C.COLORS["green_deep"], alpha=52, name="Overlay")
    add_rect(s, 0.9, 0.78, 1.1, 0.035, C.COLORS["gold"], name="Rule")
    add_text(s, 0.9, 1.0, 8.0, 0.3,
             [{"text": p["kicker"], "size": 12, "color": C.COLORS["gold_light"]}],
             name="Kicker")
    set_title(s, p["title"], 0.9, 1.35, 9.5, 1.25, size=54, color=C.COLORS["white"])
    add_text(s, 0.9, 2.85, 7.2, 0.9,
             [{"text": p["lead"], "size": 17, "color": C.COLORS["white_soft"],
               "line_spacing": 1.35}], name="Body")
    for i, tag in enumerate(p["tags"]):
        tx = 0.9 + i * 2.35
        add_rect(s, tx, 6.25, 2.1, 0.44, None, shape=MSO_SHAPE.ROUNDED_RECTANGLE,
                 radius=0.5, name="TagBox")
        add_rect(s, tx, 6.25, 2.1, 0.44, C.COLORS["gold"], alpha=0,
                 shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5, name="TagBox")
        box = s.shapes[-1]
        box.fill.background()
        box.line.color.rgb = rgb(C.COLORS["gold_light"])
        box.line.width = Pt(0.75)
        add_text(s, tx, 6.35, 2.1, 0.26,
                 [{"text": tag, "size": 12, "color": C.COLORS["gold_light"],
                   "align": CENTER}], name="Tag", align=CENTER)
    caption(s, p["credit"], 10.2, 6.78, 2.4, C.COLORS["white_soft"], RIGHT)


def page_overview(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_text(s, 0.75, 0.52, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True, "color": C.COLORS["red"]}],
             name="Kicker")
    set_title(s, p["title"], 0.75, 0.82, 5.6, 0.8, size=34)
    add_rect(s, 0.75, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.75, 1.95, 4.95, 1.0,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["muted"],
               "line_spacing": 1.45}], name="Body")
    add_picture(s, p["image"], 0.75, 3.2, 4.6, 2.55)
    caption(s, p["credit"], 0.75, 5.86, 4.6)
    add_rect(s, 6.62, 1.4, 0.02, 4.62, C.COLORS["line"], name="Timeline")
    for i, day in enumerate(p["days"]):
        cy = 1.32 + i * 1.6
        card = add_rect(s, 6.95, cy, 5.65, 1.42, C.COLORS["paper"],
                        shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06, name="Card")
        card.line.color.rgb = rgb("#E8DECB")
        card.line.width = Pt(0.75)
        add_rect(s, 6.5, cy + 0.16, 0.28, 0.28, C.COLORS["gold"],
                 shape=MSO_SHAPE.OVAL, name="Dot")
        add_rect(s, 6.63, cy + 0.29, 0.02, 1.12, C.COLORS["gold"], name="Timeline")
        add_text(s, 7.25, cy + 0.16, 2.0, 0.24,
                 [{"text": day["tag"], "size": 11, "bold": True, "color": C.COLORS["red"]}],
                 name="Kicker")
        add_text(s, 7.25, cy + 0.42, 2.2, 0.34,
                 [{"text": day["theme"], "size": 19, "bold": True,
                   "font": C.TITLE_FONT, "color": C.COLORS["ink"]}], name="Body")
        add_text(s, 9.55, cy + 0.46, 2.9, 0.3,
                 [{"text": day["spots"], "size": 13, "color": C.COLORS["green"],
                   "align": RIGHT}], name="Body", align=RIGHT)
        add_text(s, 7.25, cy + 0.92, 5.0, 0.3,
                 [{"text": day["note"], "size": 12, "color": C.COLORS["muted"]}],
                 name="Body")
    footer(s, p["n"])


def page_content_left(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_picture(s, p["image"], 0, 0, 5.65, SH)
    add_rect(s, 0, 6.5, 5.65, 1.0, C.COLORS["green_deep"], alpha=55, name="Overlay")
    add_text(s, 0.6, 6.72, 4.4, 0.3,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["gold_light"]}], name="Kicker")
    caption(s, p["credit"], 0.6, 6.93, 4.4, C.COLORS["white_soft"])
    add_text(s, 6.2, 0.52, 6.3, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 6.2, 0.82, 6.3, 0.8, size=36)
    add_rect(s, 6.2, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 6.2, 1.93, 6.2, 0.7,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["muted"],
               "line_spacing": 1.4}], name="Body")
    sections(s, p["sections"], 6.2, 2.78, 6.2)
    stat_row(s, p["stats"], 6.2, 6.18, width=2.05)
    footer(s, p["n"])


def page_content_right(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_picture(s, p["image"], 7.68, 0, 5.653, SH)
    add_rect(s, 7.68, 6.5, 5.653, 1.0, C.COLORS["green_deep"], alpha=55, name="Overlay")
    caption(s, p["credit"], 8.0, 6.93, 4.9, C.COLORS["white_soft"])
    add_text(s, 0.9, 0.52, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 0.9, 0.82, 6.3, 0.8, size=36)
    add_rect(s, 0.9, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.9, 1.93, 6.2, 0.7,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["muted"],
               "line_spacing": 1.4}], name="Body")
    sections(s, p["sections"], 0.9, 2.78, 6.2)
    stat_row(s, p["stats"], 0.9, 6.18, width=2.05)
    footer(s, p["n"])


def page_content_top(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_picture(s, p["image"], 0, 0, SW, 3.55)
    add_rect(s, 0, 0, SW, 3.55, C.COLORS["green_deep"], alpha=48, name="Overlay")
    add_text(s, 0.8, 0.55, 7.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["gold_light"]}], name="Kicker")
    set_title(s, p["title"], 0.8, 0.85, 8.2, 0.85, size=38, color=C.COLORS["white"])
    add_text(s, 0.8, 1.95, 7.4, 0.55,
             [{"text": p["lead"], "size": 14, "color": C.COLORS["white_soft"]}],
             name="Body")
    caption(s, p["credit"], 10.1, 3.18, 2.5, C.COLORS["white_soft"], RIGHT)
    for i, item in enumerate(p["sections"]):
        cx = 0.75 + i * 4.15
        card = add_rect(s, cx, 3.98, 3.65, 2.5, C.COLORS["paper"],
                        shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05, name="Card")
        card.line.color.rgb = rgb("#E8DECB")
        card.line.width = Pt(0.75)
        add_text(s, cx + 0.32, 4.2, 3.0, 0.24,
                 [{"text": item["label"], "size": 10.5, "bold": True,
                   "color": C.COLORS["gold"]}], name="Kicker")
        add_text(s, cx + 0.32, 4.5, 3.0, 0.58,
                 [{"text": item["heading"], "size": 16.5, "bold": True,
                   "font": C.TITLE_FONT, "color": C.COLORS["ink"],
                   "line_spacing": 1.15}], name="Body")
        add_text(s, cx + 0.32, 5.18, 3.0, 1.05,
                 [{"text": item["body"], "size": 12.5, "color": C.COLORS["muted"],
                   "line_spacing": 1.35}], name="Body")
    footer(s, p["n"])


def page_content_dark(prs, p):
    s = new_slide(prs, C.COLORS["green_deep"])
    add_picture(s, p["image"], 5.55, 0, 7.783, SH)
    add_rect(s, 5.55, 0, 7.783, SH, C.COLORS["green_deep"], alpha=28, name="Overlay")
    add_text(s, 0.8, 0.55, 5.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["gold_light"]}], name="Kicker")
    set_title(s, p["title"], 0.8, 0.85, 5.2, 1.15, size=39, color=C.COLORS["white"])
    add_rect(s, 0.8, 2.18, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.8, 2.38, 4.6, 0.7,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["white_soft"],
               "line_spacing": 1.4}], name="Body")
    sections(s, p["sections"], 0.8, 3.2, 4.55, dark=True, gap=1.08)
    stat_row(s, p["stats"], 0.8, 6.35, width=1.75,
             color=C.COLORS["gold_light"], label_color=C.COLORS["white_soft"])
    caption(s, p["credit"], 9.6, 6.95, 3.0, C.COLORS["white_soft"], RIGHT)
    footer(s, p["n"], color="#8C968D", rule=False)


def page_content_light(prs, p):
    s = new_slide(prs, C.COLORS["green_light"])
    add_picture(s, p["image"], 7.55, 0, 5.783, SH)
    add_rect(s, 7.55, 6.5, 5.783, 1.0, C.COLORS["green_deep"], alpha=58, name="Overlay")
    caption(s, p["credit"], 7.85, 6.93, 5.0, C.COLORS["white_soft"])
    add_text(s, 0.8, 0.55, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 0.8, 0.85, 6.4, 0.8, size=36)
    add_rect(s, 0.8, 1.75, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.8, 1.96, 6.2, 0.7,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["muted"],
               "line_spacing": 1.4}], name="Body")
    sections(s, p["sections"], 0.8, 2.82, 6.3)
    stat_row(s, p["stats"], 0.8, 6.18, width=2.05)
    add_text(s, 0.8, 6.82, 6.4, 0.22,
             [{"text": p["note"], "size": 9.5, "color": C.COLORS["muted"],
               "italic": True}], name="Note")
    footer(s, p["n"])


def page_content_forest(prs, p):
    s = new_slide(prs, C.COLORS["green"])
    add_picture(s, p["image"], 7.1, 0, 6.233, SH)
    add_rect(s, 7.1, 0, 6.233, SH, C.COLORS["green_deep"], alpha=22, name="Overlay")
    caption(s, p["credit"], 9.2, 6.95, 3.4, C.COLORS["white_soft"], RIGHT)
    add_text(s, 0.8, 0.55, 5.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["gold_light"]}], name="Kicker")
    set_title(s, p["title"], 0.8, 0.85, 6.0, 0.8, size=38, color=C.COLORS["white"])
    add_rect(s, 0.8, 1.75, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.8, 1.96, 5.8, 0.7,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["white_soft"],
               "line_spacing": 1.4}], name="Body")
    sections(s, p["sections"], 0.8, 2.92, 5.9, dark=True, gap=1.12)
    footer(s, p["n"], color="#93A198", rule=False)


def page_food(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_text(s, 0.75, 0.52, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 0.75, 0.82, 8.2, 0.8, size=34)
    add_rect(s, 0.75, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.75, 1.93, 7.4, 0.5,
             [{"text": p["lead"], "size": 13.5, "color": C.COLORS["muted"]}],
             name="Body")
    for i, item in enumerate(p["items"]):
        cx = 0.75 + (i % 2) * 3.85
        cy = 2.55 + (i // 2) * 1.9
        card = add_rect(s, cx, cy, 3.6, 1.7, C.COLORS["paper"],
                        shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.05, name="Card")
        card.line.color.rgb = rgb("#E8DECB")
        card.line.width = Pt(0.75)
        add_rect(s, cx, cy, 0.06, 1.7, C.COLORS["red"], name="Accent")
        add_text(s, cx + 0.28, cy + 0.2, 3.0, 0.3,
                 [{"text": item["name"], "size": 17, "bold": True,
                   "font": C.TITLE_FONT, "color": C.COLORS["ink"]}], name="Body")
        add_text(s, cx + 0.28, cy + 0.58, 3.0, 0.26,
                 [{"text": item["price"], "size": 12, "bold": True,
                   "color": C.COLORS["red"]}], name="Body")
        add_text(s, cx + 0.28, cy + 0.92, 3.0, 0.5,
                 [{"text": item["note"], "size": 12, "color": C.COLORS["muted"]}],
                 name="Body")
    add_picture(s, p["image"], 9.2, 2.55, 3.35, 3.85)
    caption(s, p["credit"], 9.2, 6.47, 3.35)
    add_text(s, 9.2, 6.75, 3.35, 0.3,
             [{"text": p["quote"], "size": 12, "bold": True,
               "color": C.COLORS["gold"]}], name="Body")
    footer(s, p["n"])


def page_budget(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_picture(s, p["image"], 10.35, 0.55, 2.25, 1.55)
    add_text(s, 0.75, 0.52, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 0.75, 0.82, 8.0, 0.8, size=34)
    add_rect(s, 0.75, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.75, 1.93, 8.6, 0.4,
             [{"text": p["lead"], "size": 13, "color": C.COLORS["muted"]}],
             name="Body")
    add_text(s, 0.72, 2.42, 2.95, 1.3,
             [{"text": p["total"], "size": 76, "bold": True,
               "font": C.TITLE_FONT, "color": C.COLORS["red"]}], name="Body")
    add_text(s, 3.75, 3.28, 2.0, 0.35,
             [{"text": p["total_unit"], "size": 14, "color": C.COLORS["muted"]}],
             name="Body")
    add_text(s, 0.75, 3.85, 5.1, 0.7,
             [{"text": "两人同行 · 舒适型 · 三天两晚", "size": 12.5,
               "color": C.COLORS["ink"], "line_spacing": 1.4}], name="Body")
    add_text(s, 0.75, 4.3, 5.1, 1.2,
             [{"text": p["budget_note"], "size": 12, "color": C.COLORS["muted"],
               "line_spacing": 1.4}], name="Body")
    for i, item in enumerate(p["items"]):
        by = 2.42 + i * 0.78
        add_text(s, 6.0, by, 1.45, 0.28,
                 [{"text": item["name"], "size": 12, "color": C.COLORS["ink"]}],
                 name="Body")
        add_rect(s, 7.55, by + 0.1, 3.55, 0.13, "#E6DDCB", name="BarTrack")
        add_rect(s, 7.55, by + 0.1, 3.55 * item["pct"] / 100, 0.13,
                 C.COLORS["red"] if i == 0 else C.COLORS["gold"], name="Bar")
        add_text(s, 11.28, by, 1.25, 0.28,
                 [{"text": f"{item['amount']} 元", "size": 12, "bold": True,
                   "color": C.COLORS["ink"], "align": RIGHT}], name="Body", align=RIGHT)
        add_text(s, 7.55, by + 0.28, 3.4, 0.25,
                 [{"text": item["note"], "size": 10.5, "color": C.COLORS["muted"]}],
                 name="Caption")
    add_text(s, 6.0, 6.55, 6.5, 0.3,
             [{"text": p["note"], "size": 11, "color": C.COLORS["muted"],
               "italic": True}], name="Caption")
    footer(s, p["n"])


def page_tips(prs, p):
    s = new_slide(prs, C.COLORS["cream"])
    add_picture(s, p["image"], 8.4, 0, 4.933, SH)
    add_rect(s, 8.4, 0, 4.933, SH, C.COLORS["green_deep"], alpha=20, name="Overlay")
    add_text(s, 8.75, 6.85, 4.2, 0.25,
             [{"text": p["credit"], "size": 9.5, "color": C.COLORS["white_soft"]}],
             name="Caption")
    add_text(s, 0.75, 0.52, 6.0, 0.26,
             [{"text": p["kicker"], "size": 11, "bold": True,
               "color": C.COLORS["red"]}], name="Kicker")
    set_title(s, p["title"], 0.75, 0.82, 7.2, 0.8, size=34)
    add_rect(s, 0.75, 1.72, 1.0, 0.03, C.COLORS["gold"], name="Rule")
    add_text(s, 0.75, 1.93, 7.0, 0.4,
             [{"text": p["lead"], "size": 13, "color": C.COLORS["muted"]}],
             name="Body")
    for i, text in enumerate(p["items"]):
        col = i % 2
        row = i // 2
        cx = 0.75 + col * 3.8
        cy = 2.55 + row * 1.42
        add_text(s, cx, cy, 0.45, 0.25,
                 [{"text": f"{i + 1:02d}", "size": 11, "bold": True,
                   "color": C.COLORS["gold"]}], name="Kicker")
        add_text(s, cx + 0.48, cy, 3.05, 1.1,
                 [{"text": text, "size": 12.5, "color": C.COLORS["ink"],
                   "line_spacing": 1.45}], name="Body")
    footer(s, p["n"])


def page_ending(prs, p):
    s = new_slide(prs, C.COLORS["green_deep"])
    add_picture(s, p["image"], 0, 0, SW, SH)
    add_rect(s, 0, 0, SW, SH, C.COLORS["green_deep"], alpha=58, name="Overlay")
    add_text(s, 1.0, 1.5, 11.33, 0.3,
             [{"text": p["kicker"], "size": 12, "color": C.COLORS["gold_light"],
               "align": CENTER}], name="Kicker", align=CENTER)
    set_title(s, p["title"], 1.0, 1.95, 11.33, 1.0, size=44,
              color=C.COLORS["white"], align=CENTER)
    add_text(s, 1.0, 3.25, 11.33, 0.5,
             [{"text": p["quote"], "size": 21, "font": C.TITLE_FONT,
               "color": C.COLORS["gold_light"], "align": CENTER}], name="Body",
             align=CENTER)
    add_text(s, 1.0, 3.9, 11.33, 0.4,
             [{"text": p["lead"], "size": 14, "color": C.COLORS["white_soft"],
               "align": CENTER}], name="Body", align=CENTER)
    add_rect(s, 6.17, 4.65, 1.0, 0.025, C.COLORS["gold"], name="Rule")
    add_text(s, 1.0, 4.95, 11.33, 0.3,
             [{"text": "南京三日游 · 2026", "size": 12,
               "color": C.COLORS["white_soft"], "align": CENTER}], name="Body",
             align=CENTER)
    caption(s, p["credit"], 10.2, 6.9, 2.4, C.COLORS["white_soft"], RIGHT)


BUILDERS = {
    "cover": page_cover,
    "overview": page_overview,
    "content_left": page_content_left,
    "content_right": page_content_right,
    "content_top": page_content_top,
    "content_dark": page_content_dark,
    "content_light": page_content_light,
    "content_forest": page_content_forest,
    "food": page_food,
    "budget": page_budget,
    "tips": page_tips,
    "ending": page_ending,
}


def main():
    prs = Presentation()
    prs.slide_width = Emu(12192000)
    prs.slide_height = Emu(6858000)
    cp = prs.core_properties
    cp.title = C.TOPIC
    cp.subject = "南京三日游旅行提案：行程、景点、美食与预算"
    cp.author = "南京三日游 · AI 开发者空间实践"
    cp.last_modified_by = "CodeArts"
    cp.keywords = "南京,三日游,旅行,中山陵,明孝陵,夫子庙,秦淮河,玄武湖,紫金山"
    cp.comments = (
        "由 python-pptx 生成，文本框与图片均可编辑。"
        "原始 html-to-pptx 路线因 Playwright Chromium 下载超时改用 python-pptx。"
    )
    cp.category = "旅行提案"

    for page in C.PAGES:
        BUILDERS[page["type"]](prs, page)

    prs.save(OUT)
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()