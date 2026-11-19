"""Build the solutions and news data from the supplied inspection copy.

Run from any directory: python scripts/prepare_mission_content.py
The Word document supplies the article text; listed products supply image paths.
"""

import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "网站文案_巡逻救援侦察_2026-11-16" / "巡检救援侦察_解决方案与新闻活动.docx"
ADDITIONS = ROOT.parent / "网站文案_巡逻救援侦察_2026-11-16" / "巡检救援侦察_新增10篇_仅YH2000和YH3000.docx"
OUTPUT = ROOT / "src/data/mission-content.json"
NAMESPACE = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

SOLUTION_META = [
    ("boundary-river-inspection", "边界与河道巡检", ["YH-2000"], "YH-2000"),
    ("corridor-site-inspection", "通道与站点巡检", ["YH-2000"], "YH-2000"),
    ("mountain-search-recheck", "山区搜救", ["YH-2000", "YH-3000"], "YH-3000"),
    ("post-disaster-access", "灾后侦察", ["YH-2000", "YH-3000"], "YH-2000"),
    ("rescue-site-observation", "救援现场观察", ["YH-3000", "YH-2000"], "YH-3000"),
]
ARTICLE_META = [
    ("yh-2000-inspection-selection", "巡检选型", ["YH-2000"], "YH-2000"),
    ("cross-region-inspection-records", "巡检记录", ["YH-2000"], "YH-2000"),
    ("mountain-search-task-split", "救援协同", ["YH-2000", "YH-3000"], "YH-3000"),
    ("yh-3000-loaded-endurance", "载荷与航时", ["YH-3000"], "YH-3000"),
    ("post-disaster-verification", "灾后侦察", ["YH-2000", "YH-3000"], "YH-2000"),
]
ADDITIONAL_SOLUTION_META = [
    ("construction-stage-inspection", "建设项目巡检", ["YH-2000"], "YH-2000"),
    ("mountain-station-inspection", "山区场站巡检", ["YH-2000"], "YH-2000"),
    ("flood-response-updates", "洪涝救援", ["YH-2000", "YH-3000"], "YH-3000"),
    ("wildfire-access-recon", "林火外围侦察", ["YH-2000", "YH-3000"], "YH-2000"),
    ("post-earthquake-settlement-recon", "震后安置区域侦察", ["YH-2000", "YH-3000"], "YH-3000"),
]
ADDITIONAL_ARTICLE_META = [
    ("yh-2000-repeat-inspection-baseline", "复飞巡检", ["YH-2000"], "YH-2000"),
    ("mountain-station-link-and-endurance", "山区巡检", ["YH-2000"], "YH-2000"),
    ("flood-imagery-update-time", "洪涝救援", ["YH-2000", "YH-3000"], "YH-3000"),
    ("yh-3000-multi-point-sorties", "近距观察", ["YH-3000"], "YH-3000"),
    ("two-platform-handoff", "平台协作", ["YH-2000", "YH-3000"], "YH-2000"),
]


def read_paragraphs(path: Path) -> list[str]:
    with ZipFile(path) as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    return [
        text
        for paragraph in root.findall(".//w:p", NAMESPACE)
        if (text := "".join(node.text or "" for node in paragraph.findall(".//w:t", NAMESPACE)).strip())
    ]


def parse_items(lines: list[str], start: int, end: int, meta: list[tuple], catalog: dict) -> list[dict]:
    section = lines[start + 1:end]
    headings = [index for index, line in enumerate(section) if re.match(r"^0[1-5]\s{2,}", line)]
    if len(headings) != len(meta):
        raise ValueError(f"Expected {len(meta)} articles, found {len(headings)}")

    items = []
    for index, heading_pos in enumerate(headings):
        chunk = section[heading_pos:(headings[index + 1] if index + 1 < len(headings) else len(section))]
        if len(chunk) != 7:
            raise ValueError(f"Article {index + 1} needs a title, product line and five paragraphs: {len(chunk)}")

        slug, topic, expected_models, image_model = meta[index]
        product_names = list(dict.fromkeys(re.findall(r"YH-\d{4}", chunk[1])))
        if product_names != expected_models:
            raise ValueError(f"Unexpected products for {slug}: {product_names}")
        image_product = catalog[image_model]
        image = image_product["bestImage"]
        if not (ROOT / "public" / image.lstrip("/")).is_file():
            raise ValueError(f"Missing product image for {slug}: {image}")

        paragraphs = chunk[2:]
        items.append({
            "slug": slug,
            "title": re.sub(r"^0[1-5]\s+", "", chunk[0]),
            "topic": topic,
            "summary": paragraphs[0].split("。", 1)[0] + "。",
            "paragraphs": paragraphs,
            "productNames": product_names,
            "productIds": [catalog[model]["id"] for model in product_names],
            "image": image,
            "imageAlt": image_product["bestImageAlt"],
            "imageModel": image_model,
        })
    return items


def main() -> None:
    products = json.loads((ROOT / "src/data/products.json").read_text(encoding="utf-8"))["products"]
    catalog = {product["model"]: product for product in products}
    original = read_paragraphs(SOURCE)
    additions = read_paragraphs(ADDITIONS)
    original_articles = original.index("新闻与活动")
    additional_articles = additions.index("新闻与活动")
    data = {
        "sourceDocument": SOURCE.name,
        "additionalDocument": ADDITIONS.name,
        "solutions": [
            *parse_items(original, original.index("解决方案"), original_articles, SOLUTION_META, catalog),
            *parse_items(additions, additions.index("解决方案"), additional_articles, ADDITIONAL_SOLUTION_META, catalog),
        ],
        "articles": [
            *parse_items(original, original_articles, len(original), ARTICLE_META, catalog),
            *parse_items(additions, additional_articles, len(additions), ADDITIONAL_ARTICLE_META, catalog),
        ],
    }
    if "画册" in json.dumps(data, ensure_ascii=False):
        raise ValueError("Public copy must not mention catalogues")
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(data['solutions'])} solutions and {len(data['articles'])} news articles from two source documents")


if __name__ == "__main__":
    main()
