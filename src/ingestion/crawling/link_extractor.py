from __future__ import annotations

from urllib.parse import urljoin

from lxml import etree, html


def extract_links(content: str, base_url: str) -> list[str]:
    try:
        tree = html.fromstring(content)
        hrefs = tree.xpath("//a/@href")
        links = []
        for href in hrefs:
            # Skip empty or whitespace-only hrefs
            if not href or not href.strip():
                continue
            # Resolve relative URLs against base URL
            resolved = urljoin(base_url, href.strip())
            # Only include URLs with http:// or https:// schemes
            if resolved.startswith("http://") or resolved.startswith("https://"):
                links.append(resolved)
        return links
    except (ValueError, TypeError, etree.ParserError, etree.XMLSyntaxError):
        return []
