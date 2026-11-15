"""Convert the supplied editorial illustrations to web-ready local assets.

Usage: python source/content/prepare_assets.py --source "C:/.../建站资料"
The output preserves the image content; only format and maximum pixel size change.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps


ASSETS = [
    ("y200-field", "产品原图/Y-200_现场图.jpg", "Y-200 产品小图"),
    ("y500-product", "产品原图/Y-500_产品图.jpg", "Y-500 产品图"),
    ("y40-scene", "产品原图/Y-40_场景图.jpg", "Y-40 场景图"),
    ("yh2000-view", "产品原图/YH-2000_产品视图.jpg", "YH-2000 产品视图"),
    ("mdg48-scene", "产品原图/MD-G48_场景图.png", "MD-G48 场景图"),
    ("mdx8-view", "产品原图/MD-X8_产品视图.png", "MD-X8 产品视图"),
    ("hw61600-top", "产品原图/HW61600_产品俯视图.png", "HW61600 产品俯视图"),
    ("workshop", "产品原图/明德新材_车间场景.png", "画册车间场景"),
    ("usgs-2016-orthomosaic", "公开案例/USGS_2016_生态修复正射影像.jpg", "USGS 2016 正射影像"),
    ("usgs-2023-meadow", "公开案例/USGS_2023_草甸测绘现场.jpg", "USGS 2023 草甸测绘现场"),
    ("usgs-2021-burn", "公开案例/USGS_2021_火烧迹地无人机测绘.jpg", "USGS 2021 火烧迹地测绘"),
    ("usgs-2018-fire", "公开案例/USGS_2018_火灾区域无人机调查.jpg", "USGS 2018 火灾区域调查"),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    source_folder = args.source / "网站文案_案例版_2026-11-14" / "配图"
    project_root = Path(__file__).resolve().parents[2]
    output_folder = project_root / "public" / "media" / "editorial"
    output_folder.mkdir(parents=True, exist_ok=True)
    manifest: list[dict] = []
    for stem, relative_path, description in ASSETS:
        original = source_folder / relative_path
        if not original.is_file():
            raise FileNotFoundError(original)
        output = output_folder / f"{stem}.webp"
        mobile_output = output_folder / f"{stem}-sm.webp"
        with Image.open(original) as opened:
            image = ImageOps.exif_transpose(opened)
            original_size = image.size
            image.thumbnail((1800, 1400), Image.Resampling.LANCZOS)
            if image.mode not in ("RGB", "RGBA"):
                image = image.convert("RGB")
            image.save(output, "WEBP", quality=84, method=5)
            output_size = image.size
            mobile_image = image.copy()
            mobile_image.thumbnail((900, 700), Image.Resampling.LANCZOS)
            mobile_image.save(mobile_output, "WEBP", quality=82, method=5)
        manifest.append(
            {
                "name": stem,
                "source": relative_path.replace("\\", "/"),
                "description": description,
                "sourceDimensions": list(original_size),
                "webDimensions": list(output_size),
                "webPath": f"/media/editorial/{stem}.webp",
                "mobilePath": f"/media/editorial/{stem}-sm.webp",
                "bytes": output.stat().st_size,
                "mobileBytes": mobile_output.stat().st_size,
            }
        )
    manifest_path = project_root / "source" / "content" / "editorial_image_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(manifest)} editorial images, {sum(item['bytes'] for item in manifest):,} bytes")


if __name__ == "__main__":
    main()
