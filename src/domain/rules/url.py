import hashlib
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        path,
        parsed.params,
        parsed.query,
        "",  # strip fragment
    ))


def url_hash(url: str) -> str:
    normalized = normalize_url(url)
    return hashlib.sha256(normalized.encode()).hexdigest()


def extract_domain(url: str) -> str:
    return urlparse(url).netloc


def get_base_url(url: str) -> str:
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
