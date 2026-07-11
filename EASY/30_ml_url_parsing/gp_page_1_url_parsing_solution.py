"""Extract reachable URLs from a text message."""

import re
from collections import Counter
from typing import Dict

import requests


URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?"
    r"((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:/[^\s]*)?)",
    flags=re.IGNORECASE,
)
TRAILING_CHARACTERS = ".,!?;:)]}'\"/"


def normalize_url(url: str) -> str:
    """Normalize the host while preserving the path character case."""
    cleaned_url = url.rstrip(TRAILING_CHARACTERS)
    host, separator, path = cleaned_url.partition("/")

    if not separator:
        return host.lower()

    return f"{host.lower()}/{path}"


def parse_urls(message: str) -> Dict[str, int]:
    """Return occurrence counts for reachable URLs in the message."""
    url_counts = Counter(
        normalize_url(url)
        for url in URL_PATTERN.findall(message)
    )
    reachable_urls = []

    for url in url_counts:
        try:
            response = requests.get(f"http://{url}", timeout=5)
            response.raise_for_status()
            reachable_urls.append(url)
        except requests.RequestException as error:
            print(error)

    return {url: url_counts[url] for url in reachable_urls}


if __name__ == "__main__":
    message = (
        "Check out this link www.example.com, example.com and"
        " also https://www.xn--80ak6aa92e.com/"
        " also www.xn--80ak6aa92e.com"
        " also xn--80ak6aa92e.com"
        " also apple.com"
        " Don't miss this great opportunity!"
        " www.google.com."
        " hello.ru"
    )
    print(parse_urls(message))
