"""Generate the published product catalog from PRODUCT_CATALOGUE_V7.

Usage: python scripts/prepare_catalog_v7.py "C:/.../PRODUCT_CATALOGUE_V7"
The source catalog is intentionally kept outside the public repository.
"""

import csv
import json
import re
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\SHU\Desktop\建站资料\上架资料\PRODUCT_CATALOGUE_V7")
OUTPUT = ROOT / "public/media/products/v7"

CATEGORIES = [
    ("fixed-wing", "固定翼无人机", "按最大载重与飞行航程查看固定翼平台。"),
    ("vtol", "垂直起降固定翼无人机", "按载重与画册标注的空载航时查看垂起平台。"),
    ("multirotor", "多旋翼无人机", "按载重与对应工况的续航查看多旋翼平台。"),
    ("loitering", "巡飞器", "按最大飞行航程与任务载荷查看型号。"),
    ("fpv-kit", "FPV无人机套件", "按最大载重与画册标注的空载续航查看套件。"),
    ("fpv-frame", "FPV无人机机架", "按轴距、重量与结构尺寸查看机架。"),
    ("engine", "发动机", "按功率、重量或推力查看动力产品。"),
]
KEY_BY_CATEGORY = {name: key for key, name, _ in CATEGORIES}

# Values below are transcribed from each model's 原页文字.txt.  They retain
# qualification such as ≥, ≤, no-load, and payload-conditioned endurance.
METRICS = {
    "YH-1000": [("最大载荷", "≤ 7 kg"), ("飞行航程", "≥ 100 km")],
    "YH-1001": [("最大载荷", "≤ 7 kg"), ("飞行航程", "≥ 80 km")],
    "YH-1002": [("最大载荷", "50 kg"), ("飞行航程", "≥ 1600 km")],
    "YH-1003": [("最大载荷", "50 kg"), ("最大飞行航程", "1500 km")],
    "YH-2000": [("最大载荷", "15 kg"), ("标准空载航时", "10 h")],
    "YH-2001": [("最大载荷", "2.5 kg"), ("标准空载航时", "240 min")],
    "YH-2002": [("最大载荷", "2.5 kg"), ("标准空载航时", "240 min")],
    "YH-2003": [("最大载荷", "5 kg"), ("标准空载航时", "240 min")],
    "YH-2004": [("最大载荷", "10 kg"), ("标准空载航时", "190 min")],
    "YH-2005": [("最大载荷", "5 kg"), ("标准空载航时", "240 min")],
    "YH-2006": [("最大载荷", "10 kg"), ("标准空载航时", "480 min")],
    "YH-2008": [("最大载荷", "15 kg"), ("标准空载航时", "780 min")],
    "YH-2009": [("最大载荷", "40 kg"), ("标准空载航时", "600 min")],
    "YH-3000": [("最大载重", "60 kg"), ("60 kg 载重续航", "18 min")],
    "YH-3001": [("最大载重", "7 kg"), ("7 kg 载重续航", "25 min")],
    "YH-3002": [("最大载重", "5 kg"), ("5 kg 载重续航", "30 min")],
    "YH-4000": [("最大飞行航程", "110 km"), ("最大任务载荷", "1 kg")],
    "YH-4001": [("最大飞行航程", "180 km"), ("最大任务载荷", "2 kg")],
    "YH-4002": [("最大飞行航程", "320 km"), ("最大任务载荷", "5 kg")],
    "YH-5000": [("最大载重", "2 kg"), ("空载续航", "12 min")],
    "YH-5001": [("最大载重", "2 kg"), ("空载续航", "29 min")],
    "YH-5002": [("最大载重", "4 kg"), ("空载续航", "28 min")],
    "YH-5003": [("最大载重", "6 kg"), ("空载续航", "30 min")],
    "YH-5004": [("最大载重", "7 kg"), ("空载续航", "38 min")],
    "YH-5005": [("最大载重", "8 kg"), ("空载续航", "42 min")],
    "YH-5006": [("最大载重", "18 kg"), ("空载续航", "50 min")],
    "YH-5007": [("最大载重", "12 kg"), ("空载续航", "50 min")],
    "YH-5008": [("最大载重", "15 kg"), ("空载续航", "58 min")],
    "YH-5009": [("轴距", "277 mm"), ("机架重量", "120 g")],
    "YH-5010": [("轴距", "311 mm"), ("机架重量", "178.6 g")],
    "YH-5011": [("轴距", "396 mm"), ("机架重量", "248 g")],
    "YH-5012": [("轴距", "427 mm"), ("机架重量", "228 g")],
    "YH-5013": [("轴距", "600 mm"), ("机架重量", "738 g")],
    "YH-5014": [("轴距", "647 mm"), ("机架重量", "768 g")],
    "YH-5015": [("轴距", "840 mm"), ("机架重量", "1150 g")],
    "YH-5016": [("轴距", "1160 mm"), ("臂管直径", "φ30 mm")],
    "WP-4000": [("最大功率", "39 kW @ 6500 r/min"), ("裸机重量", "18.6 kg")],
    "WP-4001": [("MTJ-80 推力", "8 kgf"), ("MTJ-220 推力", "22 kgf")],
}


def ensure_source_value(model: str, value: str, source_text: str) -> None:
    """Catch accidental changes to the curated values against the source text."""
    compact = re.sub(r"\s+", "", source_text).lower()
    number = re.search(r"\d+(?:\.\d+)?", value)
    if number and number.group() not in compact:
        raise ValueError(f"{model}: {value} was not found in 原页文字.txt")


def convert_image(path: Path, destination: Path, max_edge: int) -> dict:
    with Image.open(path) as image:
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        image.save(destination, "WEBP", quality=86, method=6)
        return {"width": image.width, "height": image.height}


def main() -> None:
    with (SOURCE / "产品索引.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    models = [row["型号"] for row in rows]
    if len(models) != 38 or len(set(models)) != 38 or set(models) != set(METRICS):
        raise ValueError("The V7 index and curated model list differ")
    category_order = {name: index for index, (_, name, _) in enumerate(CATEGORIES)}
    rows.sort(key=lambda row: category_order[row["类别"]])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    products = []
    manifest = []
    for row in rows:
        model = row["型号"]
        category = row["类别"]
        page = int(row["画册页码"])
        source_dir = SOURCE / "产品目录" / model
        source_text = (source_dir / "原页文字.txt").read_text(encoding="utf-8")
        metrics = METRICS[model]
        for _, value in metrics:
            ensure_source_value(model, value, source_text)
        gallery = []
        for source_name, suffix, role, alt in [
            ("透明产品图.png", "main", "product_main", f"{model} {category}产品图，取自 V7 画册第 {page} 页"),
            ("产品页.png", "page", "catalog_page", f"{model} 在 V7 画册第 {page} 页的产品资料"),
        ]:
            source_image = source_dir / source_name
            destination = OUTPUT / f"{model.lower()}-{suffix}.webp"
            dimensions = convert_image(source_image, destination, 1400 if suffix == "main" else 1100)
            gallery.append({
                "src": f"/media/products/v7/{destination.name}",
                "role": role,
                "alt": alt,
                **dimensions,
                "sourceFile": str(source_image.relative_to(SOURCE)).replace("\\", "/"),
            })
            manifest.append({"model": model, "role": role, "source": gallery[-1]["sourceFile"], "output": gallery[-1]["src"], **dimensions})
        alternate_image = source_dir / "透明产品图_另一型号.png"
        if alternate_image.exists():
            destination = OUTPUT / f"{model.lower()}-alternate.webp"
            dimensions = convert_image(alternate_image, destination, 1400)
            alternate = {
                "src": f"/media/products/v7/{destination.name}",
                "role": "product_detail",
                "alt": f"{model} 同页另一型号发动机产品图，取自 V7 画册第 {page} 页",
                **dimensions,
                "sourceFile": str(alternate_image.relative_to(SOURCE)).replace("\\", "/"),
            }
            gallery.append(alternate)
            manifest.append({"model": model, "role": "product_detail", "source": alternate["sourceFile"], "output": alternate["src"], **dimensions})
        summary = " · ".join(f"{label} {value}" for label, value in metrics)
        products.append({
            "id": f"yh-{model.lower()}",
            "model": model,
            "name": model,
            "categoryKey": KEY_BY_CATEGORY[category],
            "categoryName": category,
            "originalCategory": category,
            "summary": summary,
            "descriptionOriginal": "",
            "bestImage": gallery[0]["src"],
            "bestImageAlt": gallery[0]["alt"],
            "gallery": gallery,
            "imageTypes": {"product_main": [gallery[0]], "catalog_page": [gallery[1]], "product_detail": gallery[2:]},
            "specs": [{"label": label, "value": value} for label, value in metrics],
            "sourcePage": page,
            "sourceCatalog": "PRODUCT CATALOGUE V7",
            "sourceNotes": row["备注"],
        })
    data = {"brand": "YH", "categories": [{"key": key, "name": name, "intro": intro} for key, name, intro in CATEGORIES], "products": products}
    (ROOT / "src/data/products.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "src/data/product-image-manifest-v7.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(products)} products, {len(CATEGORIES)} categories, {len(manifest)} images")


if __name__ == "__main__":
    main()
