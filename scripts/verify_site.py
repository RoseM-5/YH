"""Check built routes and source-backed media; write verification_report.md."""

from __future__ import annotations

import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class AssetParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.paths: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        for attribute in ("src", "poster"):
            value = values.get(attribute)
            if value and value.startswith("/media/"):
                self.paths.add(value)
        for item in (values.get("srcset") or "").split(","):
            value = item.strip().split(" ")[0]
            if value.startswith("/media/"):
                self.paths.add(value)


def main() -> None:
    if not (DIST / "index.html").exists():
        raise SystemExit("Run npm run build first")
    catalog = json.loads((ROOT / "src/data/products.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "image_manifest.json").read_text(encoding="utf-8"))["images"]
    products = catalog["products"]
    html_files = sorted(DIST.rglob("*.html"))
    missing_routes = [p["id"] for p in products if not (DIST / "products" / p["id"] / "index.html").exists()]
    parser = AssetParser()
    for html in html_files:
        parser.feed(html.read_text(encoding="utf-8"))
    missing_assets = [path for path in parser.paths if not (DIST / path.lstrip("/")).is_file()]
    missing_main_images = [p["id"] for p in products if not p.get("bestImage") or not (DIST / p["bestImage"].lstrip("/")).is_file()]
    missing_gallery = [p["id"] for p in products if not p.get("gallery")]
    missing_types = [p["id"] for p in products if not p.get("imageTypes")]
    old_brand = [str(path.relative_to(DIST)) for path in html_files if re.search(r"KYSERA|极序工业", path.read_text(encoding="utf-8"))]
    index = (DIST / "index.html").read_text(encoding="utf-8")
    video_paths = sorted(set(re.findall(r'[^"\s]+\.mp4', index)))
    product_media = list((DIST / "media/products").rglob("*.webp"))
    used_product_media = {path for path in parser.paths if path.startswith("/media/products/")}
    categories = Counter(p["categoryName"] for p in products)

    result = {
        "routes": len(html_files),
        "products": len(products),
        "categories": len(categories),
        "source_images": len(manifest),
        "copied_product_images": len(product_media),
        "used_product_images": len(used_product_media),
        "missing_routes": missing_routes,
        "missing_assets": missing_assets,
        "missing_main_images": missing_main_images,
        "missing_gallery": missing_gallery,
        "missing_image_types": missing_types,
        "old_brand_pages": old_brand,
        "homepage_video_paths": video_paths,
    }
    (ROOT / "verification_summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    failures = [
        missing_routes,
        missing_assets,
        missing_main_images,
        missing_gallery,
        missing_types,
        old_brand,
    ]
    if video_paths != ["/media/hero/hero.mp4"]:
        failures.append(video_paths)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if any(failures):
        raise SystemExit("Verification failed; see verification_summary.json")


if __name__ == "__main__":
    main()
