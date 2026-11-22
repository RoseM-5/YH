"""Create the static English mirror from the reviewed local translation dictionary.

The Chinese Astro output remains the source of truth for routes, figures and media.
Run after `astro build`; no network service is needed during a normal build.
"""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
TRANSLATIONS = ROOT / "src" / "data" / "en-strings.json"
CHINESE = re.compile(r"[\u3400-\u9fff]")
ATTRIBUTE = re.compile(
    r"(\b(?:alt|aria-label|placeholder|title|content|data-search|data-mega-alt|data-mission-title|data-mission-summary)\s*=\s*)([\"'])(.*?)\2",
    re.I | re.S,
)
LINK = re.compile(r"(\b(?:href|action)\s*=\s*)([\"'])(.*?)\2", re.I | re.S)


class PageParser(HTMLParser):
    def __init__(self, dictionary: dict[str, str], english: bool):
        super().__init__(convert_charrefs=False)
        self.dictionary = dictionary
        self.english = english
        self.parts: list[str] = []
        self.missing: set[str] = set()
        self.in_script = 0
        self.in_language_switch = False
        self.skip_depth = 0

    def translate(self, value: str) -> str:
        stripped = value.strip()
        if not CHINESE.search(stripped):
            return value
        translated = self.dictionary.get(stripped)
        if translated is None:
            self.missing.add(stripped)
            return value
        prefix = value[: len(value) - len(value.lstrip())]
        suffix = value[len(value.rstrip()) :]
        return prefix + translated + suffix

    def tag(self, raw: str) -> str:
        if not self.english:
            return raw

        def localize_attribute(match: re.Match[str]) -> str:
            original = html.unescape(match.group(3))
            changed = self.translate(original)
            return match.group(1) + match.group(2) + html.escape(changed, quote=True) + match.group(2)

        raw = ATTRIBUTE.sub(localize_attribute, raw)

        def localize_link(match: re.Match[str]) -> str:
            value = html.unescape(match.group(3))
            if self.in_language_switch and value.startswith("/en/"):
                value = value[3:]
            elif value == "/":
                value = "/en/"
            elif value.startswith("/") and not value.startswith(("/en/", "/media/", "/_astro/", "/#")):
                value = "/en" + value
            return match.group(1) + match.group(2) + html.escape(value, quote=True) + match.group(2)

        return LINK.sub(localize_link, raw)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth:
            self.skip_depth += 1
            return
        if self.english and any(key == "data-en-remove" for key, _ in attrs):
            self.skip_depth = 1
            return
        raw = self.get_starttag_text()
        if tag in {"script", "style", "svg"}:
            self.in_script += 1
        if tag == "a" and any(key == "class" and value and "language-switch" in value for key, value in attrs):
            self.in_language_switch = True
        if self.english and tag == "html":
            raw = re.sub(r'\blang="zh-CN"', 'lang="en"', raw)
        if self.english and tag == "meta" and any(key == "http-equiv" and value == "refresh" for key, value in attrs):
            raw = re.sub(r'(url=)/(?!en/|media/|_astro/)', r'\1/en/', raw)
        if self.english and self.in_language_switch and tag == "a":
            raw = re.sub(r'aria-label="[^"]*"', 'aria-label="Switch to Chinese"', raw)
        self.parts.append(self.tag(raw))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth or (self.english and any(key == "data-en-remove" for key, _ in attrs)):
            return
        self.parts.append(self.tag(self.get_starttag_text()))

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1
            return
        self.parts.append(f"</{tag}>")
        if tag in {"script", "style", "svg"}:
            self.in_script -= 1
        if tag == "a" and self.in_language_switch:
            self.in_language_switch = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.english and self.in_language_switch:
            self.parts.append("中文")
        elif self.english and not self.in_script:
            self.parts.append(html.escape(self.translate(data), quote=False))
        else:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self.skip_depth:
            return
        self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self.skip_depth:
            return
        self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if self.skip_depth:
            return
        self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")


def main() -> None:
    dictionary = json.loads(TRANSLATIONS.read_text(encoding="utf-8"))
    pages = sorted(DIST.rglob("*.html"))
    pages = [page for page in pages if "en" not in page.relative_to(DIST).parts]
    missing: set[str] = set()
    for page in pages:
        relative = page.relative_to(DIST)
        source = page.read_text(encoding="utf-8")
        parser = PageParser(dictionary, True)
        parser.feed(source)
        missing.update(parser.missing)
        destination = DIST / "en" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("".join(parser.parts), encoding="utf-8")
    if missing:
        sample = "\n".join(sorted(missing)[:20])
        raise SystemExit(f"{len(missing)} English strings missing. First entries:\n{sample}")
    print(f"Generated {len(pages)} English pages in /en/.")


if __name__ == "__main__":
    main()
