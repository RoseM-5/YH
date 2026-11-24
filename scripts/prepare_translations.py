"""One-time helper to draft local dictionaries from the public English pages.

The generated JSON is stored locally and normal site builds are entirely offline.
Review product names, figures and technical terminology before publishing.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from localize_site import DIST, ROOT, PageParser


ENDPOINT = "https://translate.googleapis.com/translate_a/single"
LANGUAGES = ("fr", "es", "ar")


def collect_strings() -> list[str]:
    strings: set[str] = set()
    for page in (DIST / "en").rglob("*.html"):
        parser = PageParser({}, "fr", "en")
        parser.feed(page.read_text(encoding="utf-8"))
        strings.update(parser.missing)
    return sorted(strings)


def batches(strings: list[str]) -> list[list[str]]:
    result: list[list[str]] = []
    current: list[str] = []
    length = 0
    for value in strings:
        size = len(value.encode("utf-8")) + 1
        if current and (len(current) >= 18 or length + size > 3000):
            result.append(current)
            current, length = [], 0
        current.append(value)
        length += size
    if current:
        result.append(current)
    return result


def request_translation(locale: str, values: list[str]) -> list[str]:
    source = "\n".join(re.sub(r"\s+", " ", value) for value in values)
    query = urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": locale, "dt": "t", "q": source}
    )
    request = urllib.request.Request(
        f"{ENDPOINT}?{query}", headers={"User-Agent": "Mozilla/5.0"}
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                data = json.load(response)
            translated = "".join(part[0] or "" for part in data[0]).split("\n")
            if len(translated) == len(values):
                return [text.strip() for text in translated]
            if len(values) == 1:
                return [" ".join(translated).strip()]
            midpoint = len(values) // 2
            return request_translation(locale, values[:midpoint]) + request_translation(
                locale, values[midpoint:]
            )
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            if attempt == 3:
                raise RuntimeError(f"Translation failed for {locale}: {values[0][:60]}") from error
            time.sleep(2**attempt)
    raise RuntimeError("Unreachable translation retry state")


def build_dictionary(locale: str, strings: list[str]) -> None:
    destination = ROOT / "src" / "data" / f"{locale}-strings.json"
    existing = json.loads(destination.read_text(encoding="utf-8")) if destination.exists() else {}
    needed = [value for value in strings if value not in existing]
    jobs = batches(needed)
    print(f"{locale}: {len(needed)} new strings in {len(jobs)} batches", flush=True)
    if not jobs:
        return
    with ThreadPoolExecutor(max_workers=5) as pool:
        futures = {pool.submit(request_translation, locale, batch): batch for batch in jobs}
        for count, future in enumerate(as_completed(futures), 1):
            batch = futures[future]
            translations = future.result()
            existing.update(zip(batch, translations, strict=True))
            if count % 10 == 0 or count == len(jobs):
                destination.write_text(
                    json.dumps(existing, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                print(f"{locale}: {count}/{len(jobs)} batches saved", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("locales", nargs="*", choices=LANGUAGES, default=list(LANGUAGES))
    args = parser.parse_args()
    strings = collect_strings()
    print(f"English source: {len(strings)} unique visible strings", flush=True)
    for locale in args.locales:
        build_dictionary(locale, strings)


if __name__ == "__main__":
    main()
