"""Check published V7 specifications against their model pages and mappings.

The numeric check only finds candidates for manual review: shared numbers on a
page do not prove that a source value belongs to the claimed field.
"""

import csv
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageChops

from catalog_full_specs import FULL_SPECS, SOURCE_ISSUES
from prepare_catalog_v7 import DETAIL_METRICS, DISPLAY_CATEGORY, KEY_BY_CATEGORY, METRICS, ROOT, SOURCE, describe_product


UNSAFE_FIELDS = {
    "YH-5016": {"飞控 / 电调安装孔", "电机安装孔", "相机安装孔", "图传安装孔", "底板厚度", "内部空间高度", "适配桨叶", "机架重量"},
}


def numbers(value: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", value.replace(",", ""))


def main() -> int:
    catalog = json.loads((ROOT / "src/data/products.json").read_text(encoding="utf-8"))
    products = catalog["products"]
    with (SOURCE / "产品索引.csv").open(encoding="utf-8-sig", newline="") as handle:
        index = {row["型号"]: row for row in csv.DictReader(handle)}
    problems = []
    candidates = []
    image_count = 0
    if set(index) != {product["model"] for product in products}:
        problems.append("Product models differ from the V7 index")
    by_model = {product["model"]: product for product in products}
    for product in products:
        model = product["model"]
        if product["originalCategory"] != index[model]["类别"]:
            problems.append(f"{model}: category differs from V7 index")
        if product["categoryKey"] != KEY_BY_CATEGORY[index[model]["类别"]] or product["categoryName"] != DISPLAY_CATEGORY.get(index[model]["类别"], index[model]["类别"]):
            problems.append(f"{model}: category key or display name differs from V7 index")
        if product["sourcePage"] != int(index[model]["画册页码"]):
            problems.append(f"{model}: source page differs from V7 index")
        if product["name"] != model or product["id"] != f"yh-{model.lower()}":
            problems.append(f"{model}: model name or route id differs")
        if product["sourceIssue"] != SOURCE_ISSUES.get(model, ""):
            problems.append(f"{model}: source issue note differs")
        if product["summary"] != " · ".join(f"{label} {value}" for label, value in METRICS[model]):
            problems.append(f"{model}: card summary differs from selected source values")
        if product["description"] != describe_product(model, index[model]["类别"], METRICS[model], DETAIL_METRICS[model]):
            problems.append(f"{model}: detail description differs from selected source values")
        gallery = product["gallery"]
        if not gallery or product["bestImage"] != gallery[0]["src"]:
            problems.append(f"{model}: main image does not match gallery")
        for item in gallery:
            image_count += 1
            source_file = item["sourceFile"].split("#", 1)[0]
            if not source_file.startswith(f"产品目录/{model}/"):
                problems.append(f"{model}: image belongs to another model: {source_file}")
            if not (SOURCE / source_file).is_file() or not (ROOT / "public" / item["src"].lstrip("/")).is_file():
                problems.append(f"{model}: image source or output missing: {source_file}")
        if gallery:
            with Image.open(SOURCE / gallery[0]["sourceFile"]) as original, Image.open(ROOT / "public" / product["bestImage"].lstrip("/")) as published:
                left = original.convert("RGBA").resize((64, 64))
                right = published.convert("RGBA").resize((64, 64))
                difference = ImageChops.difference(left, right)
                average = sum(sum(channel.getdata()) / (64 * 64) for channel in difference.split()) / 4
                if average > 2:
                    problems.append(f"{model}: published main image differs from source ({average:.2f})")
        expected = dict(METRICS[model] + DETAIL_METRICS[model] + FULL_SPECS[model])
        actual = {spec["label"]: spec["value"] for spec in product["specs"]}
        if len(actual) != len(product["specs"]):
            problems.append(f"{model}: duplicated label")
        for label in UNSAFE_FIELDS.get(model, set()) & actual.keys():
            problems.append(f"{model}: unresolved source field was published: {label}")
        if actual != expected:
            problems.append(f"{model}: published specifications differ from curated source mapping")
        source = (SOURCE / "产品目录" / model / "原页文字.txt").read_text(encoding="utf-8")
        lines = [re.sub(r"\s+", "", line).replace(",", "") for line in source.splitlines() if line.strip()]
        windows = ["".join(lines[index:index + span]) for span in (1, 2, 3) for index in range(len(lines) - span + 1)]
        for spec in product["specs"]:
            tokens = numbers(spec["value"])
            if tokens and not any(all(token in window for token in tokens) for window in windows):
                candidates.append(f"{model} | {spec['label']} | {spec['value']} | numbers not together in adjacent source lines")
        expected_models = [item["model"] for item in products if item["categoryKey"] == product["categoryKey"]]
        if [item["model"] for item in product["comparison"]["models"]] != expected_models:
            problems.append(f"{model}: comparison model order or category mismatch")
        for item in product["comparison"]["models"]:
            sibling = by_model[item["model"]]
            specs = {spec["label"]: spec["value"] for spec in sibling["specs"]}
            expected_values = []
            expected_notes = []
            for field in product["comparison"]["fields"]:
                source_label = field
                if product["categoryKey"] == "vtol":
                    if field == "起飞重量":
                        source_label = "标准起飞重量" if sibling["model"] == "YH-2000" else "最大起飞重量"
                    elif field == "最大高度":
                        source_label = "最大起飞高度" if sibling["model"] == "YH-2000" else "最大飞行高度"
                    elif field == "发动机":
                        if sibling["model"] == "YH-2000":
                            expected_values.append("油电混合动力")
                            expected_notes.append("")
                        elif sibling["model"] in {"YH-2001", "YH-2002", "YH-2003", "YH-2004", "YH-2005"}:
                            expected_values.append("电动发电机")
                            expected_notes.append("")
                        elif "发动机" in specs:
                            match = re.fullmatch(r"(LiDe \d+) (二冲程发动机)", specs["发动机"])
                            if match:
                                expected_values.append(match.group(1))
                                expected_notes.append(match.group(2))
                            else:
                                expected_values.append(specs["发动机"])
                                expected_notes.append("")
                        else:
                            expected_values.append("—")
                            expected_notes.append("")
                        continue
                expected_values.append(specs.get(source_label, "—"))
                expected_notes.append(source_label if source_label != field else "")
            if item["values"] != expected_values or (product["categoryKey"] == "vtol" and item.get("notes") != expected_notes):
                problems.append(f"{model}: comparison values for {item['model']} are misplaced")
    print(f"Models: {len(products)}; specification rows: {sum(len(product['specs']) for product in products)}")
    print(f"Gallery assets checked: {image_count}")
    print(f"Structural or mapping problems: {len(problems)}")
    for problem in problems:
        print("PROBLEM", problem)
    print(f"Numeric source candidates for manual review: {len(candidates)}")
    for candidate in candidates:
        print("REVIEW", candidate)
    return bool(problems)


if __name__ == "__main__":
    sys.exit(main())
