"""One-time helper: collect new Chinese page strings and propose English translations.

The committed en-strings.json is used offline by normal builds. Review changes
to that file before publishing, especially product specifications and caveats.
"""

from __future__ import annotations

import json
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from localize_site import DIST, TRANSLATIONS, PageParser


dictionary = json.loads(TRANSLATIONS.read_text(encoding="utf-8")) if TRANSLATIONS.exists() else {}
missing: set[str] = set()
for page in DIST.rglob("*.html"):
    if "en" in page.relative_to(DIST).parts:
        continue
    parser = PageParser(dictionary, True)
    parser.feed(page.read_text(encoding="utf-8"))
    missing.update(parser.missing)

entries = sorted(missing)
batches: list[list[str]] = []
for entry in entries:
    if not batches or sum(len(item) + 20 for item in batches[-1]) + len(entry) > 1800:
        batches.append([])
    batches[-1].append(entry)

for batch_number, batch in enumerate(batches, 1):
    query = "\n".join(f"<YH{index:04d}>\n{entry}" for index, entry in enumerate(batch))
    for attempt in range(4):
        try:
            params = urlencode({"client": "gtx", "sl": "zh-CN", "tl": "en", "dt": "t", "q": query})
            with urlopen(f"https://translate.googleapis.com/translate_a/single?{params}", timeout=30) as response:
                payload = json.load(response)
            translated = "".join(segment[0] for segment in payload[0])
            markers = list(re.finditer(r"<YH(\d{4})>", translated))
            if len(markers) != len(batch):
                raise ValueError(f"Expected {len(batch)} markers, received {len(markers)}")
            for index, marker in enumerate(markers):
                end = markers[index + 1].start() if index + 1 < len(markers) else len(translated)
                value = translated[marker.end():end].strip()
                if not value:
                    raise ValueError(f"Blank translation in batch {batch_number}, entry {index}")
                dictionary[batch[index]] = value
            break
        except (HTTPError, URLError, ValueError) as error:
            if attempt == 3:
                raise RuntimeError(f"Translation batch {batch_number} failed") from error
            time.sleep(2 * (attempt + 1))
    print(f"Translated batch {batch_number}/{len(batches)}", flush=True)
    TRANSLATIONS.write_text(
        json.dumps(dict(sorted(dictionary.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    time.sleep(0.4)

print(f"Added {len(entries)} strings to {TRANSLATIONS}")
