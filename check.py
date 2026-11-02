# -*- coding: utf-8 -*-
"""验收脚本：打开生成的 PPTX，执行 10 项硬性断言。"""

import os
import sys

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

HERE = os.path.dirname(os.path.abspath(__file__))
PPTX = os.path.join(HERE, "南京三日游.pptx")
EXPECTED_PAGES = 12
MIN_IMAGES = 10
MIN_BODY_PT = 12.0
MIN_BYTES = 200 * 1024
EXPECTED_AUTHOR = "南京三日游 · AI 开发者空间实践"
EXPECTED_W, EXPECTED_H = 12192000, 6858000  # 13.333in × 7.5in = 1280×720 @96dpi

results = []
details = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


def is_picture(shape):
    return shape.shape_type == MSO_SHAPE_TYPE.PICTURE


def text_shapes(slide):
    return [s for s in slide.shapes if s.has_text_frame and s.text.strip()]


def main():
    if not os.path.exists(PPTX):
        print(f"找不到 {PPTX}")
        return 1

    prs = Presentation(PPTX)
    slides = list(prs.slides)
    size = os.path.getsize(PPTX)

    # 1. 页数
    check("页数 = 12", len(slides) == EXPECTED_PAGES, f"实际 {len(slides)} 页")

    # 2. 每页标题文本
    titles = []
    empty_titles = []
    for i, slide in enumerate(slides, 1):
        title = slide.shapes.title
        value = title.text.strip() if title is not None else ""
        titles.append(value)
        if len(value) < 2:
            empty_titles.append(i)
    check("每页都有标题文本", not empty_titles,
          "缺失页：" + ",".join(map(str, empty_titles)) if empty_titles else
          "12/12 页标题非空")

    # 3. 图片总数与每页至少一张
    total_images = sum(1 for s in slides for sh in s.shapes if is_picture(sh))
    pages_without_image = [
        i for i, s in enumerate(slides, 1)
        if not any(is_picture(sh) for sh in s.shapes)
    ]
    check("图片总数 ≥ 10", total_images >= MIN_IMAGES and not pages_without_image,
          f"共 {total_images} 张，每页至少 1 张"
          + (f"，缺图页 {pages_without_image}" if pages_without_image else ""))

    # 4. 正文字号下限
    min_pt = None
    problems = []
    for i, slide in enumerate(slides, 1):
        for shape in slide.shapes:
            if not shape.has_text_frame or not shape.name.startswith("Body"):
                continue
            for p in shape.text_frame.paragraphs:
                for run in p.runs:
                    if not run.text.strip():
                        continue
                    if run.font.size is None:
                        problems.append(f"P{i} 未显式设字号")
                        continue
                    pt = run.font.size.pt
                    min_pt = pt if min_pt is None else min(min_pt, pt)
                    if pt < MIN_BODY_PT:
                        problems.append(f"P{i} {pt}pt")
    check("正文字号 ≥ 12pt", min_pt is not None and not problems,
          f"最小 {min_pt}pt" if not problems else "；".join(problems[:4]))

    # 5. 无空页
    empty_pages = []
    for i, slide in enumerate(slides, 1):
        images = sum(1 for sh in slide.shapes if is_picture(sh))
        texts = text_shapes(slide)
        chars = sum(len(sh.text.strip()) for sh in texts)
        if images < 1 or len(texts) < 3 or chars < 30:
            empty_pages.append(i)
    check("无空页", not empty_pages,
          "12/12 页均有图、≥3 个文本块、≥30 字" if not empty_pages
          else f"疑似空页 {empty_pages}")

    # 6. 文件大小
    check("文件大小 > 200KB", size > MIN_BYTES, f"{size / 1024 / 1024:.2f} MB")

    # 7. 作者元数据
    author = (prs.core_properties.author or "").strip()
    check("作者元数据非空", bool(author) and author != "python-pptx", f'author="{author}"')

    # 8. 每页标题不重复
    check("12 个标题互不重复", len(set(titles)) == EXPECTED_PAGES,
          f"唯一标题 {len(set(titles))}/{EXPECTED_PAGES}")

    # 9. 画布尺寸 1280×720
    check("画布 = 1280×720 (16:9)",
          prs.slide_width == EXPECTED_W and prs.slide_height == EXPECTED_H,
          f"{prs.slide_width}×{prs.slide_height} EMU")

    # 10. 形状不越界 + 可编辑文本充足
    overflow = []
    for i, slide in enumerate(slides, 1):
        for sh in slide.shapes:
            left, top = sh.left or 0, sh.top or 0
            right = left + (sh.width or 0)
            bottom = top + (sh.height or 0)
            if left < -5000 or top < -5000 or right > prs.slide_width + 5000 \
                    or bottom > prs.slide_height + 5000:
                overflow.append(f"P{i}:{sh.name}")
    editable = sum(len(text_shapes(s)) for s in slides)
    check("形状不越界且文本可编辑", not overflow and editable >= 36,
          f"0 越界，{editable} 个可编辑文本块" if not overflow
          else "；".join(overflow[:4]))

    print("南京三日游.pptx 验收结果")
    print("-" * 66)
    for idx, (name, ok, detail) in enumerate(results, 1):
        print(f"[{'PASS' if ok else 'FAIL'}] {idx:02d}  {name:<24}  {detail}")
    passed = sum(1 for _, ok, _ in results if ok)
    print("-" * 66)
    print(f"通过 {passed}/{len(results)} 项")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())