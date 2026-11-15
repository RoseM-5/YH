"""Normalize the three supplied catalog exports into one source-grounded site catalog.

Run from the project root:
    python scripts/prepare_catalog.py --source-dir <path-to-建站资料>

The image manifest is written before products.json is created. The second pass adds
actual product-page usage to the same manifest after the canonical data is built.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image, UnidentifiedImageError


SITE_ROOT = Path(__file__).resolve().parents[1]
PACKS = (
    ("yh", "product cate/全册提取", "PRODUCT CATALOGUE V6.pdf"),
    ("uav", "uav/全册提取", "UAV_CN&ENG.pdf"),
    ("md", "明德新材/全册提取", "明德新材画册——（去联系方式） .pdf"),
)

CATEGORIES = {
    "vtol": {"name": "垂起复合翼", "intro": "垂直起降与固定翼巡航形态，按任务需求选择平台。"},
    "fixed-wing": {"name": "固定翼无人机", "intro": "固定翼平台与不同动力配置。"},
    "multirotor": {"name": "多旋翼无人机", "intro": "面向近距观察与多样化任务的旋翼平台。"},
    "target": {"name": "靶机平台", "intro": "画册中的靶机系列型号。"},
    "special": {"name": "特种飞行平台", "intro": "画册中的巡飞及察侦类平台。"},
    "power": {"name": "动力系统", "intro": "画册列出的涡喷及发动机产品。"},
    "frame": {"name": "碳纤维机架", "intro": "碳纤维一体机架与壳体系列。"},
}

ROLE_TYPES = {
    "product": "product_main",
    "product_view": "product_main",
    "detail": "product_detail",
    "scene": "application",
    "diagram": "diagram_structure",
    "accessory": "product_detail",
    "description_image": "product_detail",
    "catalog_thumbnail": "small_asset",
    "cover_product": "small_asset",
    "source_table": "small_asset",
    "company_scene": "factory",
}


def category_for(source_key: str, product: dict) -> str:
    model = product["model"]
    if source_key == "md":
        return "frame" if model.startswith(("MD-X", "HW", "HI", "HD")) else "vtol"
    if source_key == "yh":
        if model.startswith("YH-100"): return "fixed-wing"
        if model.startswith("YH-200"): return "vtol"
        if model.startswith("YH-300"): return "multirotor"
        if model.startswith("YH-400"): return "special"
        return "power"
    if model in {"Y-500", "Y-200"}: return "vtol"
    if model in {"Y-40", "Y-60", "Y-80"}: return "multirotor"
    if model in {"Y-280", "Y-240", "Y-150", "Y-70"}: return "target"
    return "special"


def read_catalogs(source_root: Path) -> list[dict]:
    catalogs = []
    saved = SITE_ROOT / "source" / "catalogs"
    saved.mkdir(parents=True, exist_ok=True)
    for key, folder, pdf in PACKS:
        base = source_root / folder
        catalog_path = base / "catalog.json"
        csv_path = base / "images.csv"
        if not catalog_path.is_file() or not csv_path.is_file():
            raise FileNotFoundError(f"Missing catalog source: {catalog_path} or {csv_path}")
        shutil.copyfile(csv_path, saved / f"{key}-images.csv")
        with catalog_path.open(encoding="utf-8") as handle:
            catalog = json.load(handle)
        catalog["source_pdf"] = pdf
        (saved / f"{key}.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")
        with csv_path.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        catalogs.append({"key": key, "folder": folder, "pdf": pdf, "base": base, "catalog": catalog, "rows": rows})
    return catalogs


def build_initial_manifest(catalogs: list[dict]) -> tuple[list[dict], dict[tuple[str, str], dict]]:
    entries: list[dict] = []
    lookup: dict[tuple[str, str], dict] = {}
    for pack in catalogs:
        for row in pack["rows"]:
            file = row.get("file") or row.get("path")
            if not file:
                continue
            source = pack["base"] / file
            if not source.is_file():
                raise FileNotFoundError(source)
            role = row.get("role") or row.get("kind") or "unknown"
            models = [model for model in re.split(r"[;,]", row.get("models") or row.get("model") or "") if model]
            entry = {
                "source": pack["key"],
                "file": file.replace("\\", "/"),
                "sourcePdf": pack["pdf"],
                "sourcePage": int(row.get("source_page") or 0),
                "role": role,
                "imageType": ROLE_TYPES.get(role, "small_asset"),
                "caption": row.get("caption") or row.get("view") or "",
                "models": models,
                "width": int(row.get("width") or 0),
                "height": int(row.get("height") or 0),
                "sourceBytes": source.stat().st_size,
                "publicPath": None,
                "usage": [],
                "unusedReason": None,
            }
            entries.append(entry)
            lookup[(pack["key"], entry["file"])] = entry
    return entries, lookup


def image_paths(product: dict) -> list[str]:
    paths = []
    for item in product.get("images", []):
        path = item.get("path") if isinstance(item, dict) else item
        if path:
            paths.append(path.replace("\\", "/"))
    return list(dict.fromkeys(paths))


def sorted_relevant(paths: list[str], key: str, lookup: dict) -> list[dict]:
    entries = [lookup[(key, path)] for path in paths if (key, path) in lookup]
    entries = [entry for entry in entries if entry["imageType"] not in {"small_asset", "factory"}]
    rank = {"product_main": 0, "product_detail": 1, "application": 2, "diagram_structure": 3}
    return sorted(entries, key=lambda item: (rank.get(item["imageType"], 4), -(item["width"] * item["height"])))


def convert_image(pack: dict, entry: dict) -> str:
    if entry["publicPath"]:
        return entry["publicPath"]
    source = pack["base"] / entry["file"]
    filename = Path(entry["file"]).stem + ".webp"
    relative = Path("media") / "products" / pack["key"] / filename
    target = SITE_ROOT / "public" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.stat().st_mtime >= source.stat().st_mtime:
        with Image.open(target) as optimized:
            entry["outputWidth"], entry["outputHeight"] = optimized.size
        entry["publicPath"] = "/" + relative.as_posix()
        return entry["publicPath"]
    try:
        with Image.open(source) as opened:
            opened.load()
            image = opened.convert("RGBA") if "A" in opened.getbands() else opened.convert("RGB")
            max_width = 1800 if entry["imageType"] == "application" else 1400
            if image.width > max_width:
                new_height = round(image.height * max_width / image.width)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            image.save(target, "WEBP", quality=83, method=5)
            entry["outputWidth"], entry["outputHeight"] = image.size
    except (OSError, UnidentifiedImageError) as error:
        raise RuntimeError(f"Cannot convert {source}: {error}") from error
    entry["publicPath"] = "/" + relative.as_posix()
    return entry["publicPath"]


def display_summary(pack_key: str, product: dict, category_name: str) -> str:
    if pack_key == "yh" and not product["model"].startswith("YH-400"):
        wanted = (
            ("max payload", "最大载荷"), ("maximum payload", "最大载荷"),
            ("standard no-load duration", "空载航时"), ("max endurance", "最大续航"),
            ("mtow", "最大起飞重量"), ("wheelbase", "轴距"),
            ("max power", "最大功率"), ("type", "型号"),
        )
        highlights = []
        for term, label in wanted:
            match = next((spec for spec in product.get("specifications", []) if term in spec.get("name_original", "").lower()), None)
            if match and (label, match["value_original"]) not in highlights:
                highlights.append((label, match["value_original"]))
            if len(highlights) == 2:
                break
        if highlights:
            return f"{category_name} · " + " / ".join(f"{label} {value}" for label, value in highlights)
    text = product.get("description_original_zh") or product.get("description_original") or ""
    if pack_key == "md":
        highlights = product.get("highlights_original") or []
        return "；".join(highlights[:2]) if highlights else category_name
    text = re.sub(r"\s+", " ", text).strip()
    if text:
        return text[:120]
    return f"{category_name}，具体配置与参数见原画册。"


def specs_for(pack_key: str, product: dict) -> list[dict]:
    if pack_key == "md":
        return [{"label": item["label"], "value": item["value"]} for item in product.get("parameters", [])]
    return [{"label": item["name_original"], "value": item["value_original"]} for item in product.get("specifications", [])]


def build_products(catalogs: list[dict], lookup: dict) -> list[dict]:
    result = []
    for pack in catalogs:
        for raw in pack["catalog"]["products"]:
            model = raw["model"]
            category_key = category_for(pack["key"], raw)
            category_name = CATEGORIES[category_key]["name"]
            id_ = f'{pack["key"]}-{model.lower()}'
            entries = sorted_relevant(image_paths(raw), pack["key"], lookup)
            primary = next((item for item in entries if item["imageType"] == "product_main"), None)
            confidence = "direct product view"
            if primary is None:
                primary = next((item for item in entries if item["imageType"] == "product_detail"), None)
                confidence = "product detail used because no main view exists"
            if primary is None:
                primary = next((item for item in entries if item["imageType"] == "application"), None)
                confidence = "scene used because no product view exists"
            unresolved = []
            if primary is None:
                unresolved.append("No usable product image in source")
            if not raw.get("description_original") and not raw.get("description_original_zh"):
                unresolved.append("No product-specific prose in source")
            if model == "Y-80":
                unresolved.append("Page heading is Y-80, but a raster description panel says ZY-80")
            if model == "Y-500":
                unresolved.append("Some resolution digits in the source text layer lack multiplication signs")
            gallery = []
            for entry in entries:
                src = convert_image(pack, entry)
                usage = f"/products/{id_}/"
                if usage not in entry["usage"]:
                    entry["usage"].append(usage)
                gallery.append({
                    "src": src,
                    "role": entry["imageType"],
                    "alt": f"{model} {entry['caption'] or category_name}，画册第 {entry['sourcePage']} 页",
                    "width": entry.get("outputWidth") or entry["width"],
                    "height": entry.get("outputHeight") or entry["height"],
                    "sourceFile": entry["file"],
                })
            if primary:
                primary["usage"].append(f"/products/ card: {id_}")
            original_category = raw.get("category_original") or raw.get("category_en_original") or ""
            product = {
                "id": id_,
                "model": model,
                "name": raw.get("title_zh_original") or model,
                "categoryKey": category_key,
                "categoryName": category_name,
                "originalCategory": original_category,
                "summary": display_summary(pack["key"], raw, category_name),
                "descriptionOriginal": raw.get("description_original_zh") or raw.get("description_original") or "",
                "bestImage": primary["publicPath"] if primary else "",
                "bestImageAlt": (
                    f"{model} {category_name}画册场景图" if primary and primary["imageType"] == "application"
                    else f"{model} {category_name}画册细节图" if primary and primary["imageType"] == "product_detail"
                    else f"{model} {category_name}画册产品图" if primary else ""
                ),
                "gallery": gallery,
                "imageTypes": {role: [image for image in gallery if image["role"] == role] for role in sorted({image["role"] for image in gallery})},
                "imageConfidence": confidence,
                "specs": specs_for(pack["key"], raw),
                "sourceKey": pack["key"],
                "sourcePdf": pack["pdf"],
                "sourcePage": int(raw.get("source_page") or 0),
                "sourceNotes": raw.get("notes") or "",
                "unresolved": unresolved,
            }
            result.append(product)
    return result


def apply_media_overrides(products: list[dict], entries: list[dict]) -> None:
    """Apply user-supplied product views after the catalog import."""
    override_path = SITE_ROOT / "source" / "content" / "product_media_overrides.json"
    if not override_path.is_file():
        return
    overrides = json.loads(override_path.read_text(encoding="utf-8"))["products"]
    by_id = {product["id"]: product for product in products}
    for product_id, override in overrides.items():
        if product_id not in by_id:
            raise ValueError(f"Media override refers to unknown product: {product_id}")
        product = by_id[product_id]
        keep_roles = set(override.get("keepRoles", []))
        kept = [image for image in product["gallery"] if image["role"] in keep_roles]
        removed_paths = {image["src"] for image in product["gallery"] if image["role"] not in keep_roles}
        for entry in entries:
            if entry["publicPath"] in removed_paths:
                entry["usage"] = [use for use in entry["usage"] if product_id not in use]
        new_images = []
        for index, image in enumerate(override["images"]):
            asset = SITE_ROOT / "public" / image["src"].lstrip("/")
            if not asset.is_file():
                raise FileNotFoundError(f"Media override asset is missing: {asset}")
            new_images.append({key: image[key] for key in ("src", "role", "alt", "width", "height", "sourceFile")})
            usage = [f"/products/{product_id}/"]
            if index == 0:
                usage.append(f"/products/ card: {product_id}")
            usage.extend(image.get("additionalUsage", []))
            entries.append({
                "source": image["source"],
                "file": image["file"],
                "sourcePdf": None,
                "sourcePage": None,
                "role": "product",
                "imageType": image["role"],
                "caption": image["caption"],
                "models": [product["model"]],
                "width": image["width"],
                "height": image["height"],
                "sourceBytes": asset.stat().st_size,
                "publicPath": image["src"],
                "usage": usage,
                "unusedReason": None,
            })
        product["gallery"] = new_images + kept
        product["imageTypes"] = {
            role: [image for image in product["gallery"] if image["role"] == role]
            for role in sorted({image["role"] for image in product["gallery"]})
        }
        product["bestImage"] = new_images[0]["src"]
        product["bestImageAlt"] = new_images[0]["alt"]
        product["imageConfidence"] = override["imageConfidence"]
        product["sourceNotes"] = " ".join(filter(None, [product["sourceNotes"], override["sourceNote"]]))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-dir", type=Path, required=True)
    args = parser.parse_args()
    catalogs = read_catalogs(args.source_dir)
    entries, lookup = build_initial_manifest(catalogs)
    manifest_path = SITE_ROOT / "image_manifest.json"
    manifest_path.write_text(json.dumps({"images": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    products = build_products(catalogs, lookup)
    apply_media_overrides(products, entries)
    for entry in entries:
        if not entry["usage"]:
            entry["unusedReason"] = "目录缩略图、封面资源或未用于产品页的公司/来源图片"
    manifest_path.write_text(json.dumps({"images": entries}, ensure_ascii=False, indent=2), encoding="utf-8")
    output = {"brand": "YH", "categories": [{"key": key, **data} for key, data in CATEGORIES.items()], "products": products}
    data_file = SITE_ROOT / "src" / "data" / "products.json"
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"products": len(products), "images_in_source": len(entries), "images_used": sum(bool(entry["usage"]) for entry in entries), "with_best_image": sum(bool(p["bestImage"]) for p in products), "with_gallery": sum(bool(p["gallery"]) for p in products)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
