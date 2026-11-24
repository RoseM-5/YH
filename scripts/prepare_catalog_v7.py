"""Generate the published product catalog from PRODUCT_CATALOGUE_V7.

Usage: python scripts/prepare_catalog_v7.py "C:/.../PRODUCT_CATALOGUE_V7"
The source catalog is intentionally kept outside the public repository.
"""

import csv
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image
from catalog_full_specs import FULL_SPECS, SOURCE_ISSUES


ROOT = Path(__file__).resolve().parents[1]
SOURCE = next(
    (Path(arg) for arg in sys.argv[1:] if not arg.startswith("--")),
    Path(os.environ.get("YH_CATALOG_SOURCE", Path.home() / "Desktop" / "建站资料" / "上架资料" / "PRODUCT_CATALOGUE_V7")),
)
DATA_ONLY = "--data-only" in sys.argv
OUTPUT = ROOT / "public/media/products/v7"

CATEGORIES = [
    ("fixed-wing", "固定翼无人机", "按最大载重与飞行航程查看固定翼平台。"),
    ("vtol", "垂直起降固定翼无人机", "按载重与空载航时查看垂起平台。"),
    ("multirotor", "多旋翼无人机", "按载重与对应工况的续航查看多旋翼平台。"),
    ("loitering", "巡飞器", "按最大飞行航程与任务载荷查看型号。"),
    ("fpv-kit", "FPV无人机套件", "按最大载重与空载续航查看套件。"),
    ("fpv-frame", "FPV无人机机架", "按轴距、重量与结构尺寸查看机架。"),
    ("engine", "发动机", "按功率、重量或推力查看动力产品。"),
]
KEY_BY_CATEGORY = {name: key for key, name, _ in CATEGORIES}
DISPLAY_CATEGORY = {"巡飞器": "巡飞弹"}
USER_CONFIRMED_ENGINE = {f"YH-{number}": "电动发电机" for number in range(2001, 2006)}

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

# Additional fields read from each model's original catalog page. Keep the
# two short METRICS values above for card summaries; use both sets on details.
DETAIL_METRICS = {
    "YH-1000": [("动力", "电动螺旋桨（电机驱动）"), ("最大起飞重量", "20 kg"), ("最大航时", "≥ 60 min"), ("翼展", "1234 mm")],
    "YH-1001": [("动力", "涡喷发动机"), ("最大起飞重量", "20 kg"), ("最大航时", "约 20 min"), ("翼展", "1234 mm")],
    "YH-1002": [("动力", "汽油发动机（电喷、电启动）"), ("最大起飞重量", "180 kg"), ("最大航时", "≥ 8 h"), ("翼展", "2500 mm"), ("抗风等级", "Level 7")],
    "YH-1003": [("最大起飞重量", "180 kg"), ("最大航时", "9 h"), ("翼展", "2590 mm"), ("巡航速度", "180 km/h"), ("最大速度", "230 km/h")],
    "YH-2000": [("标准起飞重量", "60 kg"), ("最大起飞高度", "4000 m"), ("巡航速度", "85 km/h"), ("最大飞行速度", "130 km/h"), ("油箱容量", "18 L"), ("机身尺寸", "4800 × 2580 × 850 mm")],
    "YH-2001": [("外形尺寸", "2.1 × 0.98 × 0.24 m"), ("最大起飞重量", "14 kg"), ("巡航速度", "20 m/s"), ("最大飞行高度", "4800 m"), ("防水等级", "IP54")],
    "YH-2002": [("外形尺寸", "2.5 × 1.26 × 0.39 m"), ("最大起飞重量", "14 kg"), ("巡航速度", "20 m/s"), ("最大飞行高度", "4800 m"), ("防水等级", "IP54")],
    "YH-2003": [("外形尺寸", "3.2 × 1.83 × 0.46 m"), ("最大起飞重量", "26 kg"), ("巡航速度", "21 m/s"), ("最大飞行高度", "4200 m"), ("防水等级", "IP54")],
    "YH-2004": [("外形尺寸", "3.5 × 1.88 × 0.64 m"), ("最大起飞重量", "35 kg"), ("巡航速度", "21 m/s"), ("最大飞行高度", "4200 m"), ("防水等级", "IP54")],
    "YH-2005": [("外形尺寸", "3.95 × 1.83 × 0.57 m"), ("最大起飞重量", "28 kg"), ("巡航速度", "21 m/s"), ("最大飞行高度", "4200 m"), ("防水等级", "IP54")],
    "YH-2006": [("外形尺寸", "4.42 × 2.075 × 0.788 m"), ("最大起飞重量", "40 kg"), ("巡航速度", "20 m/s"), ("最大飞行高度", "6000 m"), ("油箱容量", "8 L"), ("防水等级", "IP54")],
    "YH-2008": [("外形尺寸", "4.80 × 2.79 × 0.51 m"), ("最大起飞重量", "64 kg"), ("巡航速度", "37 m/s"), ("最大飞行高度", "6000 m"), ("油箱容量", "26 L"), ("防水等级", "IP54")],
    "YH-2009": [("外形尺寸", "6.935 × 3.270 × 1.307 m"), ("最大起飞重量", "150 kg"), ("巡航速度", "35 m/s"), ("最大飞行高度", "6000 m"), ("油箱容量", "35 L"), ("防水等级", "IP54")],
    "YH-3000": [("机身材料", "TORAY 3K carbon fiber"), ("轴距", "2400 mm"), ("整体高度", "1000 mm"), ("机箱重量", "15.5 kg"), ("空载续航", "55 min")],
    "YH-3001": [("机身材料", "TORAY 3K carbon fiber"), ("轴距", "1600 mm"), ("整体高度", "500 mm"), ("机箱重量", "2200 g"), ("空载续航", "75 min")],
    "YH-3002": [("机身材料", "TORAY 3K carbon fiber"), ("轴距", "1200 mm"), ("整体高度", "500 mm"), ("机箱重量", "2100 g"), ("空载续航", "70 min")],
    "YH-4000": [("外形尺寸", "机长 0.9 m · 翼展 1.2 m"), ("飞行速度", "40 m/s"), ("最大飞行高度", "4000 m"), ("最大起飞重量", "6.5 kg"), ("抗风等级", "Level 5")],
    "YH-4001": [("外形尺寸", "机长 1.1 m · 翼展 1.4 m"), ("飞行速度", "50 m/s"), ("最大飞行高度", "5000 m"), ("最大起飞重量", "10 kg"), ("抗风等级", "Level 6")],
    "YH-4002": [("外形尺寸", "机长 1.7 m · 翼展 2.3 m"), ("飞行速度", "50 m/s"), ("最大飞行高度", "5000 m"), ("最大起飞重量", "22 kg"), ("抗风等级", "Level 6")],
    "YH-5000": [("额定载重", "1 kg"), ("最大速度", "150 km/h"), ("产品尺寸", "196 × 196 × 40.3 mm"), ("轴距", "277 mm"), ("净重", "406 g")],
    "YH-5001": [("额定载重", "1.5 kg"), ("最大速度", "150 km/h"), ("产品尺寸", "276 × 242 × 60 mm"), ("轴距", "312 mm"), ("净重", "540 g")],
    "YH-5002": [("额定载重", "3 kg"), ("最大速度", "160 km/h"), ("产品尺寸", "344 × 294 × 60 mm"), ("轴距", "396 mm"), ("净重", "793 g")],
    "YH-5003": [("额定载重", "5 kg"), ("最大速度", "130 km/h"), ("产品尺寸", "740 × 540 × 51.5 mm"), ("轴距", "740 mm"), ("净重", "1665 g")],
    "YH-5004": [("额定载重", "6 kg"), ("最大速度", "130 km/h"), ("产品尺寸", "489 × 489 × 80 mm"), ("轴距", "600 mm"), ("净重", "1850 g")],
    "YH-5005": [("额定载重", "7 kg"), ("最大速度", "130 km/h"), ("产品尺寸", "517 × 517 × 80 mm"), ("轴距", "647 mm"), ("净重", "2050 g")],
    "YH-5006": [("额定载重", "15 kg"), ("最大速度", "130 km/h"), ("产品尺寸", "827 × 827 × 80 mm"), ("轴距", "780 mm"), ("净重", "4280 g")],
    "YH-5007": [("额定载重", "10 kg"), ("最大速度", "165 km/h"), ("产品尺寸", "596 × 596 × 87.9 mm"), ("轴距", "840 mm"), ("净重", "3971 g")],
    "YH-5008": [("额定载重", "12 kg"), ("最大速度", "160 km/h"), ("轴距", "1160 mm"), ("净重", "6895 g")],
    "YH-5009": [("规格", "5 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "6 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "5 inch")],
    "YH-5010": [("规格", "7 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "6 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "7 inch")],
    "YH-5011": [("规格", "10 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "7 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "10 inch")],
    "YH-5012": [("规格", "10 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "7 mm"), ("顶板厚度", "2.5 mm"), ("适配桨叶", "10 inch")],
    "YH-5013": [("规格", "13 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "10 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "13 inch")],
    "YH-5014": [("规格", "15 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "10 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "15 inch")],
    "YH-5015": [("规格", "18 inch"), ("材质", "3K Carbon Fiber T300"), ("机臂厚度", "13 mm"), ("顶板厚度", "2 mm"), ("适配桨叶", "18 inch")],
    "YH-5016": [("规格", "22 inch"), ("材质", "3K Carbon Fiber T300"), ("顶板厚度", "3 mm"), ("臂管直径", "φ30 mm")],
    "WP-4000": [("最大转速", "6800 r/min"), ("排量", "630 CC"), ("最大扭矩", "56 Nm @ 4000 r/min"), ("工作海拔", "≤ 5000 m"), ("尺寸", "475 × 300 × 490 mm")],
    "WP-4001": [("MTJ-80 最高转速", "160,000 RPM"), ("MTJ-220 最高转速", "110,000 RPM"), ("MTJ-80 最大油耗", "280 ml/min"), ("MTJ-220 最大油耗", "700 ml/min"), ("最高排气温度", "750 °C")],
}

# Embedded images are numbered by `pdfimages -list`. These are independent
# views/details of the named model, not complete catalog pages or stock scenes.
DETAIL_VIEWS = {
    "YH-1002": [(4, "structure", "机体结构图"), (5, "left", "左侧产品图"), (6, "right", "右侧产品图"), (7, "top", "俯视产品图")],
    "YH-1003": [(4, "rear", "后视产品图"), (6, "angle", "斜侧产品图")],
    "YH-2000": [(2, "waterproof", "机身防水细节"), (3, "engine", "动力系统细节"), (4, "modular", "模块化结构细节")],
    **{model: [(2, "assembly", "快速拆装视图"), (3, "top", "俯视图"), (4, "side", "侧视图")]
       for model in ("YH-2001", "YH-2002", "YH-2003", "YH-2004", "YH-2005")},
    "YH-2006": [(2, "rear", "后视图"), (3, "engine", "发动机细节"), (4, "wing", "机翼连接细节")],
    "YH-2008": [(2, "side", "侧视图"), (3, "front", "正视图"), (4, "top", "俯视图")],
    "YH-2009": [(2, "right", "右侧视图"), (3, "rear", "后视图"), (4, "front", "正视图")],
    "YH-3000": [(2, "left", "左视图"), (4, "side", "侧视图"), (6, "front", "正视图")],
    "YH-3001": [(2, "assembly", "快速拆装视图"), (4, "top", "俯视图"), (6, "side", "侧视图")],
    "YH-3002": [(2, "top", "俯视图"), (4, "side", "侧视图")],
}


def describe_product(model: str, category: str, metrics: list, details: list) -> str:
    values = dict(metrics + details)
    if model == "YH-2000":
        return "YH-2000 采用四旋翼与固定翼结合的复合布局，可垂直起降。采用油电混合动力，最大载荷 15 kg，标准空载航时 10 h。"
    if model == "WP-4000":
        return "WP-4000 是喷油、风冷、二冲程的水平对置双缸汽油航空活塞发动机。最大功率 39 kW @ 6500 r/min，裸机重量 18.6 kg。"
    if model == "WP-4001":
        return "WP-4001 包含 MTJ-80 与 MTJ-220 两款涡喷发动机，推力分别为 8 kgf 和 22 kgf。"
    if category == "固定翼无人机":
        power = values.get("动力")
        power_text = {
            "电动螺旋桨（电机驱动）": "采用电动螺旋桨动力，",
            "涡喷发动机": "采用涡喷发动机，",
            "汽油发动机（电喷、电启动）": "采用带电喷与电启动的汽油发动机，",
        }.get(power, "")
        return (f"{model} 为固定翼无人机，{power_text}最大起飞重量 {values['最大起飞重量']}、"
                f"最大航时 {values['最大航时']}，{metrics[1][0]} {metrics[1][1]}。")
    if category == "垂直起降固定翼无人机":
        return (f"{model} 为垂直起降固定翼无人机。最大起飞重量 {values['最大起飞重量']}、"
                f"最大载荷 {values['最大载荷']}，标准空载航时 {values['标准空载航时']}。")
    if category == "多旋翼无人机":
        return (f"{model} 为多旋翼无人机，机身材料为 {values['机身材料']}、轴距 {values['轴距']}。"
                f"{metrics[1][0]} {metrics[1][1]}，空载续航 {values['空载续航']}。")
    if category == "巡飞器":
        return (f"{model} 为巡飞弹，外形尺寸为 {values['外形尺寸']}，"
                f"最大飞行航程 {values['最大飞行航程']}、最大任务载荷 {values['最大任务载荷']}。")
    if category == "FPV无人机套件":
        return (f"{model} 为 FPV 无人机套件，轴距 {values['轴距']}、额定载重 {values['额定载重']}，"
                f"最大载重 {values['最大载重']}，空载续航 {values['空载续航']}。")
    if category == "FPV无人机机架":
        structure = (f"机架重量 {values['机架重量']}" if "机架重量" in values
                     else f"臂管直径 {values['臂管直径']}")
        return (f"{model} 为 FPV 无人机机架，材质为 {values['材质']}、轴距 {values['轴距']}，"
                f"{structure}，规格 {values['规格']}。")
    raise ValueError(f"No description template for {model}")


def extract_detail_views(model: str, source_dir: Path, page: int, manifest: list) -> list:
    views = DETAIL_VIEWS.get(model, [])
    if not views:
        return []
    images = []
    with tempfile.TemporaryDirectory() as temp_dir:
        prefix = Path(temp_dir) / "page"
        subprocess.run(["pdfimages", "-j", str(source_dir / "产品页.pdf"), str(prefix)], check=True)
        for number, slug, label in views:
            matches = list(Path(temp_dir).glob(f"page-{number:03d}.*"))
            if len(matches) != 1:
                raise ValueError(f"{model}: embedded detail image {number} missing or ambiguous")
            destination = OUTPUT / f"{model.lower()}-detail-{slug}.webp"
            mask_path = Path(temp_dir) / f"page-{number + 1:03d}.ppm"
            dimensions = convert_image(matches[0], destination, 900, mask_path if mask_path.exists() else None)
            item = {
                "src": f"/media/products/v7/{destination.name}",
                "role": "product_detail",
                "alt": f"{model} {label}细节图",
                **dimensions,
                "sourceFile": f"产品目录/{model}/产品页.pdf#image-{number:03d}",
            }
            images.append(item)
            manifest.append({"model": model, "role": item["role"], "source": item["sourceFile"], "output": item["src"], **dimensions})
    return images


def ensure_source_value(model: str, value: str, source_text: str) -> None:
    """Catch accidental changes to the curated values against the source text."""
    compact = re.sub(r"\s+", "", source_text).lower()
    number = re.search(r"\d+(?:\.\d+)?", value)
    if number and number.group() not in compact:
        raise ValueError(f"{model}: {value} was not found in 原页文字.txt")


def convert_image(path: Path, destination: Path, max_edge: int, mask_path: Path | None = None) -> dict:
    with Image.open(path) as image:
        image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)
        if mask_path:
            with Image.open(mask_path) as mask:
                mask = mask.convert("L").resize(image.size, Image.Resampling.LANCZOS)
                composite = Image.new("RGB", image.size, "white")
                composite.paste(image.convert("RGB"), mask=mask)
                composite.save(destination, "WEBP", quality=86, method=6)
        else:
            image.save(destination, "WEBP", quality=86, method=6)
        return {"width": image.width, "height": image.height}


def comparison_cell(product: dict, field: str) -> tuple[str, str]:
    """Keep the V7 wording visible when related VTOL fields share a column."""
    specs = {item["label"]: item["value"] for item in product["specs"]}
    if product["categoryKey"] == "vtol":
        aliases = {
            "起飞重量": ("标准起飞重量", "最大起飞重量"),
            "最大高度": ("最大起飞高度", "最大飞行高度"),
        }
        for source_label in aliases.get(field, ()):
            if source_label in specs:
                return specs[source_label], source_label
        if field == "发动机":
            engine = specs.get("发动机")
            if engine:
                match = re.fullmatch(r"(LiDe \d+) (二冲程发动机)", engine)
                return (match.group(1), match.group(2)) if match else (engine, "")
            if product["model"] == "YH-2000" and "动力形式" in specs:
                return "油电混合动力", ""
            if product["model"] in USER_CONFIRMED_ENGINE:
                return USER_CONFIRMED_ENGINE[product["model"]], ""
            return "—", ""
    return specs.get(field, "—"), ""


def main() -> None:
    with (SOURCE / "产品索引.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    models = [row["型号"] for row in rows]
    if len(models) != 38 or len(set(models)) != 38 or set(models) != set(METRICS) or set(models) != set(DETAIL_METRICS) or set(models) != set(FULL_SPECS):
        raise ValueError("The V7 index and curated model list differ")
    category_order = {name: index for index, (_, name, _) in enumerate(CATEGORIES)}
    rows.sort(key=lambda row: category_order[row["类别"]])
    OUTPUT.mkdir(parents=True, exist_ok=True)
    products = []
    manifest = [] if not DATA_ONLY else json.loads((ROOT / "src/data/product-image-manifest-v7.json").read_text(encoding="utf-8"))
    existing_products = {} if not DATA_ONLY else {
        item["model"]: item for item in json.loads((ROOT / "src/data/products.json").read_text(encoding="utf-8"))["products"]
    }
    for row in rows:
        model = row["型号"]
        category = row["类别"]
        display_category = DISPLAY_CATEGORY.get(category, category)
        page = int(row["画册页码"])
        source_dir = SOURCE / "产品目录" / model
        source_text = (source_dir / "原页文字.txt").read_text(encoding="utf-8")
        metrics = METRICS[model]
        details = DETAIL_METRICS[model]
        for _, value in metrics + details:
            ensure_source_value(model, value, source_text)
        spec_pairs = []
        seen_specs = {}
        for label, value in metrics + details + FULL_SPECS[model]:
            if label in seen_specs:
                if seen_specs[label] != value:
                    raise ValueError(f"{model}: conflicting specification {label}")
                continue
            seen_specs[label] = value
            spec_pairs.append((label, value))
        if DATA_ONLY:
            gallery = existing_products[model]["gallery"]
            detail_images = existing_products[model]["imageTypes"]["product_detail"]
            variants = existing_products[model]["imageTypes"]["product_variant"]
        else:
            gallery = []
            for source_name, suffix, role, alt in [
                ("透明产品图.png", "main", "product_main", f"{model} {display_category}产品主图"),
                ("产品页.png", "page", "catalog_page", f"{model} 产品参数页"),
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
            detail_images = extract_detail_views(model, source_dir, page, manifest)
            gallery.extend(detail_images)
            variants = []
            alternate_image = source_dir / "透明产品图_另一型号.png"
            if alternate_image.exists():
                destination = OUTPUT / f"{model.lower()}-alternate.webp"
                dimensions = convert_image(alternate_image, destination, 1400)
                alternate = {
                    "src": f"/media/products/v7/{destination.name}",
                    "role": "product_variant",
                    "alt": f"{model} 同系列另一型号发动机产品图",
                    **dimensions,
                    "sourceFile": str(alternate_image.relative_to(SOURCE)).replace("\\", "/"),
                }
                variants.append(alternate)
                gallery.append(alternate)
                manifest.append({"model": model, "role": "product_variant", "source": alternate["sourceFile"], "output": alternate["src"], **dimensions})
        summary = " · ".join(f"{label} {value}" for label, value in metrics)
        products.append({
            "id": f"yh-{model.lower()}",
            "model": model,
            "name": model,
            "categoryKey": KEY_BY_CATEGORY[category],
            "categoryName": display_category,
            "originalCategory": category,
            "summary": summary,
            "description": describe_product(model, category, metrics, details),
            "variantNote": {
                "YH-1000": "YH-1000 使用电动螺旋桨；YH-1001 使用涡喷发动机。两者最大航时分别为 ≥ 60 min 与约 20 min。",
                "YH-1001": "YH-1001 使用涡喷发动机；YH-1000 使用电动螺旋桨。两者最高速度分别为 360 km/h（海平面）与 160 km/h。",
                "YH-2001": "与 YH-2002 的载荷、空载航时和起飞重量相同；主要区别是机身尺寸与运输箱尺寸。",
                "YH-2002": "与 YH-2001 的载荷、空载航时和起飞重量相同；主要区别是机身尺寸与运输箱尺寸。",
                "YH-3001": "与 YH-3002 相比，YH-3001 轴距更大，最大载重 7 kg，空载续航 75 min。",
                "YH-3002": "与 YH-3001 相比，YH-3002 轴距更小，最大载重 5 kg，空载续航 70 min。",
                "WP-4000": "WP-4000 为汽油活塞发动机；WP-4001 为 MTJ-80 / MTJ-220 涡喷发动机系列。",
                "WP-4001": "WP-4001 为涡喷发动机系列；WP-4000 为汽油活塞发动机。MTJ-80 与 MTJ-220 的推力分别为 8 kgf 和 22 kgf。",
            }.get(model, ""),
            "descriptionOriginal": "",
            "bestImage": gallery[0]["src"],
            "bestImageAlt": gallery[0]["alt"],
            "gallery": gallery,
            "imageTypes": {"product_main": [gallery[0]], "catalog_page": [gallery[1]], "product_detail": detail_images, "product_variant": variants},
            "specs": [{"label": label, "value": value} for label, value in spec_pairs],
            "sourceIssue": SOURCE_ISSUES.get(model, ""),
            "sourcePage": page,
            "sourceCatalog": "YH 产品资料",
            "sourceNotes": row["备注"].replace("画册原有", "原始图片中的"),
        })
    comparison_fields = {
        "fixed-wing": ["动力", "最大载荷", "最大航时", "飞行航程", "最大飞行航程", "巡航速度", "最大速度"],
        "vtol": ["最大载荷", "标准空载航时", "起飞重量", "巡航速度", "最大高度", "发动机"],
        "multirotor": ["最大载重", "空载续航", "轴距", "最大起飞重量", "最大适配桨叶"],
        "loitering": ["最大飞行航程", "最大任务载荷", "飞行速度", "最大起飞重量", "抗风等级"],
        "fpv-kit": ["规格", "额定载重", "最大载重", "空载续航", "额定载重续航", "轴距"],
        "fpv-frame": ["规格", "轴距", "机架重量", "顶板厚度", "机臂厚度", "臂管直径"],
        "engine": ["动力形式", "最大功率", "裸机重量", "MTJ-80 推力", "MTJ-220 推力"],
    }
    for product in products:
        siblings = [other for other in products if other["categoryKey"] == product["categoryKey"]]
        fields = comparison_fields[product["categoryKey"]]
        product["comparison"] = {
            "fields": fields,
            "models": [
                {
                    "model": other["model"],
                    "id": other["id"],
                    "values": [comparison_cell(other, field)[0] for field in fields],
                    **({"notes": [comparison_cell(other, field)[1] for field in fields]} if product["categoryKey"] == "vtol" else {}),
                }
                for other in siblings
            ],
        }
    data = {"brand": "YH", "categories": [{"key": key, "name": DISPLAY_CATEGORY.get(name, name), "intro": intro} for key, name, intro in CATEGORIES], "products": products}
    (ROOT / "src/data/products.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "src/data/product-image-manifest-v7.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {len(products)} products, {len(CATEGORIES)} categories, {len(manifest)} images")


if __name__ == "__main__":
    main()
