"""Build static language mirrors from reviewed, local translation dictionaries.

The Chinese Astro output remains the source of truth for routes, figures and media.
English is generated first; French, Spanish and Arabic use that reviewed English
copy as their translation source. A normal build never calls a translation API.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LOCALES = ("en", "fr", "es", "ar")
LANGUAGE_LABELS = {"en": "EN", "fr": "FR", "es": "ES", "ar": "العربية"}
CHINESE = re.compile(r"[\u3400-\u9fff]")
LATIN = re.compile(r"[A-Za-z]")
MODEL_ID = re.compile(r"(?:YH|WP)-\d{4}")
ATTRIBUTE = re.compile(
    r"(\b(?:alt|aria-label|placeholder|title|content|data-[\w-]*(?:title|summary|label|alt|search))\s*=\s*)([\"'])(.*?)\2",
    re.I | re.S,
)
LINK = re.compile(r"(\b(?:href|action|data-yh-scene-url)\s*=\s*)([\"'])(.*?)\2", re.I | re.S)


class PageParser(HTMLParser):
    def __init__(self, dictionary: dict[str, str], locale: str, source_locale: str):
        super().__init__(convert_charrefs=False)
        self.dictionary = dictionary
        self.locale = locale
        self.source_locale = source_locale
        self.parts: list[str] = []
        self.missing: set[str] = set()
        self.in_script = 0
        self.in_head = False
        self.in_option = False
        self.in_language_current = False
        self.in_language_link = False
        self.in_technical_table = False
        self.in_technical_value = False
        self.skip_depth = 0

    def translate(self, value: str) -> str:
        stripped = value.strip()
        if MODEL_ID.fullmatch(stripped):
            return value
        pattern = CHINESE if self.source_locale == "zh" else LATIN
        if not pattern.search(stripped):
            return value
        translated = self.dictionary.get(stripped)
        if translated is None:
            self.missing.add(stripped)
            return value
        prefix = value[: len(value) - len(value.lstrip())]
        suffix = value[len(value.rstrip()) :]
        return prefix + translated + suffix

    def rewrite_path(self, value: str) -> str:
        if not value.startswith("/") or value.startswith(("/media/", "/_astro/", "/#")):
            return value
        if self.source_locale == "en" and value.startswith("/en/"):
            return f"/{self.locale}{value[3:]}"
        if value == "/":
            return f"/{self.locale}/"
        if not value.startswith(tuple(f"/{lang}/" for lang in LOCALES)):
            return f"/{self.locale}{value}"
        return value

    def tag(self, raw: str, tag: str, attrs: list[tuple[str, str | None]]) -> str:
        if tag == "html":
            raw = re.sub(r'\blang="[^"]*"', f'lang="{self.locale}"', raw)
            if self.locale == "ar":
                raw = raw.replace("<html ", '<html dir="rtl" ', 1)

        is_refresh = tag == "meta" and any(
            key == "http-equiv" and value == "refresh" for key, value in attrs
        )

        if not is_refresh:
            def localize_attribute(match: re.Match[str]) -> str:
                if tag == "meta" and match.group(1).lstrip().startswith("content"):
                    meta_key = next(
                        (value for key, value in attrs if key in {"name", "property"}),
                        None,
                    )
                    if meta_key not in {"description", "og:title", "og:description", "twitter:title", "twitter:description"}:
                        return match.group(0)
                original = html.unescape(match.group(3))
                changed = self.translate(original)
                return match.group(1) + match.group(2) + html.escape(changed, quote=True) + match.group(2)

            raw = ATTRIBUTE.sub(localize_attribute, raw)
        else:
            raw = re.sub(
                r"(url=)(/[^\s;\"']+)",
                lambda match: match.group(1) + self.rewrite_path(match.group(2)),
                raw,
            )

        if not self.in_language_link:
            def localize_link(match: re.Match[str]) -> str:
                value = self.rewrite_path(html.unescape(match.group(3)))
                return match.group(1) + match.group(2) + html.escape(value, quote=True) + match.group(2)

            raw = LINK.sub(localize_link, raw)
        return raw

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth:
            self.skip_depth += 1
            return
        if any(key == "data-en-remove" for key, _ in attrs):
            self.skip_depth = 1
            return
        if tag in {"script", "style", "svg"}:
            self.in_script += 1
        if tag == "head":
            self.in_head = True
        if tag == "option":
            self.in_option = True
        if tag == "span" and any(key == "data-current-language" for key, _ in attrs):
            self.in_language_current = True
        if tag == "a" and any(key == "data-language-link" for key, _ in attrs):
            self.in_language_link = True
        if tag == "table" and self.source_locale == "en" and any(
            key == "class" and value and
            ("catalog-spec-table" in value or "catalog-compare-table" in value)
            for key, value in attrs
        ):
            self.in_technical_table = True
        if tag == "td" and self.in_technical_table:
            self.in_technical_value = True
        self.parts.append(self.tag(self.get_starttag_text(), tag, attrs))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth or any(key == "data-en-remove" for key, _ in attrs):
            return
        self.parts.append(self.tag(self.get_starttag_text(), tag, attrs))

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            self.skip_depth -= 1
            return
        self.parts.append(f"</{tag}>")
        if tag in {"script", "style", "svg"}:
            self.in_script -= 1
        if tag == "head":
            self.in_head = False
        if tag == "option":
            self.in_option = False
        if tag == "span" and self.in_language_current:
            self.in_language_current = False
        if tag == "a" and self.in_language_link:
            self.in_language_link = False
        if tag == "td" and self.in_technical_table:
            self.in_technical_value = False
        if tag == "table" and self.in_technical_table:
            self.in_technical_table = False

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.in_language_current:
            self.parts.append(LANGUAGE_LABELS[self.locale])
        elif self.in_language_link or self.in_script:
            self.parts.append(data)
        elif self.in_technical_value and re.search(r"\d", data):
            # Keep source figures, units and model identifiers exact in data tables.
            self.parts.append(data)
        else:
            rendered = html.escape(self.translate(data), quote=False)
            if self.locale == "ar" and not self.in_head and not self.in_option:
                rendered = re.sub(
                    r"(?<![\w-])((?:YH|WP)-\d{4})(?![\w-])",
                    r'<bdi dir="ltr">\1</bdi>',
                    rendered,
                )
            self.parts.append(rendered)

    def handle_entityref(self, name: str) -> None:
        if not self.skip_depth:
            self.parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if not self.skip_depth:
            self.parts.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self.parts.append(f"<!{decl}>")


def build_locale(locale: str) -> None:
    source_dir = DIST if locale == "en" else DIST / "en"
    source_locale = "zh" if locale == "en" else "en"
    dictionary_path = ROOT / "src" / "data" / f"{locale}-strings.json"
    dictionary = json.loads(dictionary_path.read_text(encoding="utf-8"))
    pages = sorted(source_dir.rglob("*.html"))
    if locale == "en":
        pages = [page for page in pages if not set(page.relative_to(DIST).parts) & set(LOCALES)]
    missing: set[str] = set()
    for page in pages:
        relative = page.relative_to(source_dir)
        parser = PageParser(dictionary, locale, source_locale)
        parser.feed(page.read_text(encoding="utf-8"))
        missing.update(parser.missing)
        destination = DIST / locale / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("".join(parser.parts), encoding="utf-8")
    if missing:
        sample = "\n".join(sorted(missing)[:20])
        raise SystemExit(f"{len(missing)} {locale} strings missing. First entries:\n{sample}")
    print(f"Generated {len(pages)} {locale} pages in /{locale}/.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--locale", choices=LOCALES)
    args = parser.parse_args()
    for locale in (args.locale,) if args.locale else LOCALES:
        build_locale(locale)


if __name__ == "__main__":
    main()
