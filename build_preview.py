# -*- coding: utf-8 -*-
"""生成 preview.html：12 页 1280×720 的 HTML 预览（用于截图）。"""

import os
import sys

import deck_content as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "preview.html")


def x(v):
    return f"{v * 96:.1f}px"


def f(pt):
    return f"{pt * 4 / 3:.1f}px"


def text(xx, yy, ww, content, size, color, *, bold=False, font="body",
         align="left", lh=1.3, italic=False, extra=""):
    family = "var(--serif)" if font == "serif" else "var(--body)"
    style = (
        f"left:{x(xx)};top:{x(yy)};width:{x(ww)};font-size:{f(size)};"
        f"color:{color};line-height:{lh};font-weight:{700 if bold else 400};"
        f"font-family:{family};text-align:{align};font-style:{'italic' if italic else 'normal'};"
        f"{extra}"
    )
    return f'<div class="txt" style="{style}">{content}</div>'


def rule(xx, yy, ww, color, h=0.03):
    return (f'<div style="position:absolute;left:{x(xx)};top:{x(yy)};'
            f'width:{x(ww)};height:{max(2, round(h * 96))}px;background:{color}"></div>')


def footnote(xx, yy, ww, content, color, align="left"):
    return (f'<div class="txt" style="left:{x(xx)};top:{x(yy)};width:{x(ww)};'
            f'font-size:{f(9.5)};color:{color};text-align:{align}">{content}</div>')


def footer(n, color, dark=False):
    line = "" if dark else (f'<div style="position:absolute;left:{x(0.75)};top:{x(7.07)};'
                            f'width:{x(11.83)};height:1px;background:{C.COLORS["line"]}"></div>')
    return (
        line
        + footnote(0.75, 7.16, 7.0, "南京三日游 · 2026 旅行提案", color)
        + footnote(10.6, 7.16, 1.98, f"{n:02d} / 12", color, "right")
    )


def sections_html(items, xx, yy, ww, dark=False, gap=1.1):
    hcolor = C.COLORS["white"] if dark else C.COLORS["ink"]
    bcolor = C.COLORS["white_soft"] if dark else C.COLORS["muted"]
    lcolor = "#3B4B42" if dark else C.COLORS["line"]
    out = []
    for i, item in enumerate(items):
        by = yy + i * gap
        out.append(text(xx, by, ww, item["label"], 11, C.COLORS["gold"], bold=True, lh=1.1))
        out.append(text(xx, by + 0.24, ww, item["heading"], 15.5, hcolor, bold=True, lh=1.2))
        out.append(text(xx, by + 0.58, ww, item["body"], 12.5, bcolor, lh=1.35))
        if i < len(items) - 1:
            out.append(f'<div style="position:absolute;left:{x(xx)};top:{x(by + gap - 0.14)};'
                       f'width:{x(ww - 0.15)};height:1px;background:{lcolor}"></div>')
    return "".join(out)


def stats_html(stats, xx, yy, width=2.0, color=None, label_color=None):
    out = []
    for i, (value, label) in enumerate(stats):
        bx = xx + i * width
        out.append(text(bx, yy, width - 0.15, value, 25, color or C.COLORS["red"],
                        bold=True, font="serif", lh=1.05))
        out.append(text(bx, yy + 0.43, width - 0.15, label, 11,
                        label_color or C.COLORS["muted"], lh=1.2))
    return "".join(out)


def picture(filename, xx, yy, ww, hh):
    return (f'<img src="assets/{filename}" style="position:absolute;left:{x(xx)};top:{x(yy)};'
            f'width:{x(ww)};height:{x(hh)};object-fit:cover;object-position:center" alt="">')


def shade(xx, yy, ww, hh, color, alpha):
    return (f'<div style="position:absolute;left:{x(xx)};top:{x(yy)};width:{x(ww)};'
            f'height:{x(hh)};background:{color};opacity:{alpha}"></div>')


def slide(n, body, cls=""):
    return f'<section class="slide {cls}" id="p{n}">{body}</section>'


# ------------------------------------------------------------------ pages

def p1(p):
    body = picture(p["image"], 0, 0, 13.333, 7.5) + shade(0, 0, 13.333, 7.5, "#15241D", 0.52)
    body += rule(0.9, 0.78, 1.1, C.COLORS["gold"], 0.035)
    body += text(0.9, 1.0, 8.0, p["kicker"], 12, C.COLORS["gold_light"], lh=1.2, extra="letter-spacing:.08em")
    body += text(0.9, 1.35, 9.5, p["title"], 54, C.COLORS["white"], bold=True,
                 font="serif", lh=1.05)
    body += text(0.9, 2.85, 7.2, p["lead"], 17, C.COLORS["white_soft"], lh=1.5)
    for i, tag in enumerate(p["tags"]):
        body += (f'<div class="txt" style="left:{x(0.9 + i * 2.35)};top:{x(6.25)};'
                 f'width:{x(2.1)};height:{x(0.44)};border:1px solid {C.COLORS["gold_light"]};'
                 f'border-radius:22px;display:flex;align-items:center;justify-content:center;'
                 f'font-size:{f(12)};color:{C.COLORS["gold_light"]}">{tag}</div>')
    body += footnote(10.2, 6.78, 2.4, p["credit"], C.COLORS["white_soft"], "right")
    return slide(p["n"], body, "dark")


def p2(p):
    body = text(0.75, 0.52, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                extra="letter-spacing:.08em")
    body += text(0.75, 0.82, 5.6, p["title"], 34, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.75, 1.72, 1.0, C.COLORS["gold"])
    body += text(0.75, 1.95, 4.95, p["lead"], 13.5, C.COLORS["muted"], lh=1.55)
    body += picture(p["image"], 0.75, 3.2, 4.6, 2.55)
    body += footnote(0.75, 5.86, 4.6, p["credit"], C.COLORS["muted"])
    body += f'<div style="position:absolute;left:{x(6.62)};top:{x(1.4)};width:2px;height:{x(4.62)};background:{C.COLORS["line"]}"></div>'
    for i, day in enumerate(p["days"]):
        cy = 1.32 + i * 1.6
        body += (f'<div class="card" style="left:{x(6.95)};top:{x(cy)};width:{x(5.65)};'
                 f'height:{x(1.42)}"></div>')
        body += (f'<div style="position:absolute;left:{x(6.5)};top:{x(cy + 0.16)};'
                 f'width:{x(0.28)};height:{x(0.28)};border-radius:50%;background:{C.COLORS["gold"]}"></div>')
        body += (f'<div style="position:absolute;left:{x(6.63)};top:{x(cy + 0.29)};'
                 f'width:2px;height:{x(1.12)};background:{C.COLORS["gold"]}"></div>')
        body += text(7.25, cy + 0.16, 2.0, day["tag"], 11, C.COLORS["red"], bold=True, lh=1.1)
        body += text(7.25, cy + 0.42, 2.2, day["theme"], 19, C.COLORS["ink"], bold=True, font="serif")
        body += text(9.55, cy + 0.46, 2.9, day["spots"], 13, C.COLORS["green"], align="right")
        body += text(7.25, cy + 0.92, 5.0, day["note"], 12, C.COLORS["muted"])
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p3(p):
    body = picture(p["image"], 0, 0, 5.65, 7.5)
    body += shade(0, 6.5, 5.65, 1.0, "#15241D", 0.55)
    body += text(0.6, 6.72, 4.4, p["kicker"], 11, C.COLORS["gold_light"], bold=True, lh=1.1)
    body += footnote(0.6, 6.93, 4.4, p["credit"], C.COLORS["white_soft"])
    body += text(6.2, 0.52, 6.3, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                 extra="letter-spacing:.06em")
    body += text(6.2, 0.82, 6.3, p["title"], 36, C.COLORS["ink"], bold=True, font="serif")
    body += rule(6.2, 1.72, 1.0, C.COLORS["gold"])
    body += text(6.2, 1.93, 6.2, p["lead"], 13.5, C.COLORS["muted"], lh=1.5)
    body += sections_html(p["sections"], 6.2, 2.78, 6.2)
    body += stats_html(p["stats"], 6.2, 6.18, 2.05)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p4(p):
    body = picture(p["image"], 7.68, 0, 5.653, 7.5)
    body += shade(7.68, 6.5, 5.653, 1.0, "#15241D", 0.55)
    body += footnote(8.0, 6.93, 4.9, p["credit"], C.COLORS["white_soft"])
    body += text(0.9, 0.52, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                 extra="letter-spacing:.06em")
    body += text(0.9, 0.82, 6.3, p["title"], 36, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.9, 1.72, 1.0, C.COLORS["gold"])
    body += text(0.9, 1.93, 6.2, p["lead"], 13.5, C.COLORS["muted"], lh=1.5)
    body += sections_html(p["sections"], 0.9, 2.78, 6.2)
    body += stats_html(p["stats"], 0.9, 6.18, 2.05)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p5(p):
    body = picture(p["image"], 0, 0, 13.333, 3.55)
    body += shade(0, 0, 13.333, 3.55, "#15241D", 0.48)
    body += text(0.8, 0.55, 7.0, p["kicker"], 11, C.COLORS["gold_light"], bold=True, lh=1.1)
    body += text(0.8, 0.85, 8.2, p["title"], 38, C.COLORS["white"], bold=True, font="serif")
    body += text(0.8, 1.95, 7.4, p["lead"], 14, C.COLORS["white_soft"], lh=1.4)
    body += footnote(10.1, 3.18, 2.5, p["credit"], C.COLORS["white_soft"], "right")
    for i, item in enumerate(p["sections"]):
        cx = 0.75 + i * 4.15
        body += (f'<div class="card" style="left:{x(cx)};top:{x(3.98)};width:{x(3.65)};'
                 f'height:{x(2.5)}"></div>')
        body += text(cx + 0.32, 4.2, 3.0, item["label"], 10.5, C.COLORS["gold"], bold=True, lh=1.1)
        body += text(cx + 0.32, 4.5, 3.0, item["heading"], 16.5, C.COLORS["ink"], bold=True,
                     font="serif", lh=1.2)
        body += text(cx + 0.32, 5.18, 3.0, item["body"], 12.5, C.COLORS["muted"], lh=1.45)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p6(p):
    body = picture(p["image"], 5.55, 0, 7.783, 7.5) + shade(5.55, 0, 7.783, 7.5, "#15241D", 0.28)
    body += text(0.8, 0.55, 5.0, p["kicker"], 11, C.COLORS["gold_light"], bold=True, lh=1.1)
    body += text(0.8, 0.85, 5.2, p["title"], 39, C.COLORS["white"], bold=True, font="serif", lh=1.08)
    body += rule(0.8, 2.18, 1.0, C.COLORS["gold"])
    body += text(0.8, 2.38, 4.6, p["lead"], 13.5, C.COLORS["white_soft"], lh=1.5)
    body += sections_html(p["sections"], 0.8, 3.2, 4.55, dark=True, gap=1.08)
    body += stats_html(p["stats"], 0.8, 6.35, 1.75,
                       C.COLORS["gold_light"], C.COLORS["white_soft"])
    body += footnote(9.6, 6.95, 3.0, p["credit"], C.COLORS["white_soft"], "right")
    body += footer(p["n"], "#8C968D", dark=True)
    return slide(p["n"], body, "dark")


def p7(p):
    body = picture(p["image"], 7.55, 0, 5.783, 7.5)
    body += shade(7.55, 6.5, 5.783, 1.0, "#15241D", 0.58)
    body += footnote(7.85, 6.93, 5.0, p["credit"], C.COLORS["white_soft"])
    body += text(0.8, 0.55, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1)
    body += text(0.8, 0.85, 6.4, p["title"], 36, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.8, 1.75, 1.0, C.COLORS["gold"])
    body += text(0.8, 1.96, 6.2, p["lead"], 13.5, C.COLORS["muted"], lh=1.5)
    body += sections_html(p["sections"], 0.8, 2.82, 6.3)
    body += stats_html(p["stats"], 0.8, 6.18, 2.05)
    body += text(0.8, 6.82, 6.4, p["note"], 9.5, C.COLORS["muted"], italic=True, lh=1.2)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body, "light")


def p8(p):
    body = picture(p["image"], 7.1, 0, 6.233, 7.5) + shade(7.1, 0, 6.233, 7.5, "#15241D", 0.22)
    body += footnote(9.2, 6.95, 3.4, p["credit"], C.COLORS["white_soft"], "right")
    body += text(0.8, 0.55, 5.0, p["kicker"], 11, C.COLORS["gold_light"], bold=True, lh=1.1)
    body += text(0.8, 0.85, 6.0, p["title"], 38, C.COLORS["white"], bold=True, font="serif")
    body += rule(0.8, 1.75, 1.0, C.COLORS["gold"])
    body += text(0.8, 1.96, 5.8, p["lead"], 13.5, C.COLORS["white_soft"], lh=1.5)
    body += sections_html(p["sections"], 0.8, 2.92, 5.9, dark=True, gap=1.12)
    body += footer(p["n"], "#93A198", dark=True)
    return slide(p["n"], body, "forest")


def p9(p):
    body = text(0.75, 0.52, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                extra="letter-spacing:.08em")
    body += text(0.75, 0.82, 8.2, p["title"], 34, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.75, 1.72, 1.0, C.COLORS["gold"])
    body += text(0.75, 1.93, 7.4, p["lead"], 13.5, C.COLORS["muted"], lh=1.4)
    for i, item in enumerate(p["items"]):
        cx = 0.75 + (i % 2) * 3.85
        cy = 2.55 + (i // 2) * 1.9
        body += (f'<div class="card" style="left:{x(cx)};top:{x(cy)};width:{x(3.6)};'
                 f'height:{x(1.7)}"></div>')
        body += (f'<div style="position:absolute;left:{x(cx)};top:{x(cy)};width:{x(0.06)};'
                 f'height:{x(1.7)};background:{C.COLORS["red"]}"></div>')
        body += text(cx + 0.28, cy + 0.2, 3.0, item["name"], 17, C.COLORS["ink"], bold=True, font="serif")
        body += text(cx + 0.28, cy + 0.58, 3.0, item["price"], 12, C.COLORS["red"], bold=True)
        body += text(cx + 0.28, cy + 0.92, 3.0, item["note"], 12, C.COLORS["muted"])
    body += picture(p["image"], 9.2, 2.55, 3.35, 3.85)
    body += footnote(9.2, 6.47, 3.35, p["credit"], C.COLORS["muted"])
    body += text(9.2, 6.75, 3.35, p["quote"], 12, C.COLORS["gold"], bold=True)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p10(p):
    body = picture(p["image"], 10.35, 0.55, 2.25, 1.55)
    body += text(0.75, 0.52, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                 extra="letter-spacing:.08em")
    body += text(0.75, 0.82, 8.0, p["title"], 34, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.75, 1.72, 1.0, C.COLORS["gold"])
    body += text(0.75, 1.93, 8.6, p["lead"], 13, C.COLORS["muted"], lh=1.4)
    body += text(0.72, 2.42, 2.95, p["total"], 76, C.COLORS["red"], bold=True, font="serif", lh=1.0)
    body += text(3.75, 3.28, 2.0, p["total_unit"], 14, C.COLORS["muted"])
    body += text(0.75, 3.85, 5.1, "两人同行 · 舒适型 · 三天两晚", 12.5, C.COLORS["ink"], lh=1.4)
    body += text(0.75, 4.3, 5.1, p["budget_note"], 12, C.COLORS["muted"], lh=1.45)
    for i, item in enumerate(p["items"]):
        by = 2.42 + i * 0.78
        body += text(6.0, by, 1.45, item["name"], 12, C.COLORS["ink"])
        body += (f'<div style="position:absolute;left:{x(7.55)};top:{x(by + 0.1)};'
                 f'width:{x(3.55)};height:{x(0.13)};background:#E6DDCB"></div>')
        body += (f'<div style="position:absolute;left:{x(7.55)};top:{x(by + 0.1)};'
                 f'width:{x(3.55 * item["pct"] / 100)};height:{x(0.13)};'
                 f'background:{C.COLORS["red"] if i == 0 else C.COLORS["gold"]}"></div>')
        body += text(11.28, by, 1.25, f'{item["amount"]} 元', 12, C.COLORS["ink"], bold=True, align="right")
        body += text(7.55, by + 0.28, 3.4, item["note"], 10.5, C.COLORS["muted"])
    body += text(6.0, 6.55, 6.5, p["note"], 11, C.COLORS["muted"], italic=True)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p11(p):
    body = picture(p["image"], 8.4, 0, 4.933, 7.5) + shade(8.4, 0, 4.933, 7.5, "#15241D", 0.2)
    body += footnote(8.75, 6.85, 4.2, p["credit"], C.COLORS["white_soft"])
    body += text(0.75, 0.52, 6.0, p["kicker"], 11, C.COLORS["red"], bold=True, lh=1.1,
                 extra="letter-spacing:.08em")
    body += text(0.75, 0.82, 7.2, p["title"], 34, C.COLORS["ink"], bold=True, font="serif")
    body += rule(0.75, 1.72, 1.0, C.COLORS["gold"])
    body += text(0.75, 1.93, 7.0, p["lead"], 13, C.COLORS["muted"])
    for i, item in enumerate(p["items"]):
        cx = 0.75 + (i % 2) * 3.8
        cy = 2.55 + (i // 2) * 1.42
        body += text(cx, cy, 0.45, f"{i + 1:02d}", 11, C.COLORS["gold"], bold=True, lh=1.1)
        body += text(cx + 0.48, cy, 3.05, item, 12.5, C.COLORS["ink"], lh=1.55)
    body += footer(p["n"], C.COLORS["muted"])
    return slide(p["n"], body)


def p12(p):
    body = picture(p["image"], 0, 0, 13.333, 7.5) + shade(0, 0, 13.333, 7.5, "#15241D", 0.58)
    body += text(1.0, 1.5, 11.33, p["kicker"], 12, C.COLORS["gold_light"], align="center",
                 extra="letter-spacing:.1em")
    body += text(1.0, 1.95, 11.33, p["title"], 44, C.COLORS["white"], bold=True, font="serif", align="center")
    body += text(1.0, 3.25, 11.33, p["quote"], 21, C.COLORS["gold_light"], font="serif", align="center")
    body += text(1.0, 3.9, 11.33, p["lead"], 14, C.COLORS["white_soft"], align="center")
    body += f'<div style="position:absolute;left:{x(6.17)};top:{x(4.65)};width:{x(1.0)};height:2px;background:{C.COLORS["gold"]}"></div>'
    body += text(1.0, 4.95, 11.33, "南京三日游 · 2026", 12, C.COLORS["white_soft"], align="center")
    body += footnote(10.2, 6.9, 2.4, p["credit"], C.COLORS["white_soft"], "right")
    return slide(p["n"], body, "dark")


BUILDERS = {1: p1, 2: p2, 3: p3, 4: p4, 5: p5, 6: p6,
            7: p7, 8: p8, 9: p9, 10: p10, 11: p11, 12: p12}

CSS = """
:root {
  --ink: #22251F; --muted: #5F635A; --cream: #F7F2E8; --paper: #FFFDF7;
  --red: #A63A32; --green: #24483B; --gold: #B8913F;
  --serif: "SimSun", "Songti SC", serif;
  --body: "Microsoft YaHei", "PingFang SC", sans-serif;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #23262B; }
body { font-family: var(--body); }
.deck { width: 1280px; margin: 0 auto; padding: 28px 0 40px; }
.slide {
  position: relative; width: 1280px; height: 720px; overflow: hidden;
  background: var(--cream); margin: 0 auto 28px;
  box-shadow: 0 6px 24px rgba(0,0,0,.28);
}
.slide.dark { background: #15241D; }
.slide.light { background: #EDF2E8; }
.slide.forest { background: #24483B; }
.txt { position: absolute; margin: 0; white-space: pre-wrap; }
.card { background: var(--paper); border: 1px solid #E8DECB; border-radius: 6px; }
img { display: block; }
"""


def render(page_numbers=None):
    pages = [p for p in C.PAGES if not page_numbers or p["n"] in page_numbers]
    body = "".join(BUILDERS[p["n"]](p) for p in pages)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=1280">
<title>{C.TOPIC} · 12 页预览</title>
<style>{CSS}</style>
</head>
<body>
<main class="deck">
{body}
</main>
</body>
</html>
"""


def main():
    if "--page" in sys.argv:
        n = int(sys.argv[sys.argv.index("--page") + 1])
        out = sys.argv[sys.argv.index("--out") + 1]
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render([n]))
        print(f"OK -> {out}")
        return
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(render())
    print(f"OK -> {OUT}")


if __name__ == "__main__":
    main()