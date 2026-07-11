"""Extract product information from an HTML product card."""

import re
from html import unescape
from typing import Pattern


def _make_tag_pattern(tag_name: str, class_name: str) -> Pattern[str]:
    """Build a pattern for an HTML tag with the required CSS class."""
    escaped_class = re.escape(class_name)
    return re.compile(
        rf'<{tag_name}\b[^>]*\bclass\s*=\s*["\'][^"\']*'
        rf'(?<![\w-]){escaped_class}(?![\w-])[^"\']*["\'][^>]*>'
        rf'(?P<content>.*?)</{tag_name}\s*>',
        flags=re.IGNORECASE | re.DOTALL,
    )


TITLE_PATTERN = _make_tag_pattern("h1", "product-title")
CATEGORY_PATTERN = _make_tag_pattern("div", "product-category")
OLD_PRICE_PATTERN = _make_tag_pattern("span", "price-old")
NEW_PRICE_PATTERN = _make_tag_pattern("span", "price-new")
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def _extract_text(html: str, pattern: Pattern[str]) -> str:
    """Extract and clean text from the first tag matched by pattern."""
    match = pattern.search(html)
    if match is None:
        return ""

    inner_html = match.group("content")
    text_without_tags = HTML_TAG_PATTERN.sub("", inner_html)
    decoded_text = unescape(text_without_tags)
    return WHITESPACE_PATTERN.sub(" ", decoded_text).strip()


def parse_product_info(html: str) -> dict:
    """Extract product title, category, old price, and current price."""
    product_info = {
        "title": _extract_text(html, TITLE_PATTERN),
        "category": _extract_text(html, CATEGORY_PATTERN),
        "old_price": _extract_text(html, OLD_PRICE_PATTERN),
        "new_price": _extract_text(html, NEW_PRICE_PATTERN),
    }
    return product_info
