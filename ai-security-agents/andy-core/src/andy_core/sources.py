"""Narrow, allowlisted source retrieval for Android exported-component research."""
from __future__ import annotations

from datetime import datetime, timezone
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


APPROVED_SOURCES = (
    {
        "source_id": "android-exported-risk",
        "title": "Android Developers: android:exported",
        "url": "https://developer.android.com/privacy-and-security/risks/android-exported",
        "publisher": "Android Developers",
    },
    {
        "source_id": "android-component-access-control",
        "title": "Android Developers: Permission-based access control to exported components",
        "url": "https://developer.android.com/privacy-and-security/risks/access-control-to-exported-components",
        "publisher": "Android Developers",
    },
    {
        "source_id": "owasp-exported-activity-test",
        "title": "OWASP MASTG-TEST-0364: Exported and Unprotected Activities",
        "url": "https://mas.owasp.org/MASTG-TEST-0364/",
        "publisher": "OWASP",
    },
    {
        "source_id": "owasp-activity-knowledge",
        "title": "OWASP MASTG-KNOW-0132: Android Activities",
        "url": "https://mas.owasp.org/MASTG/knowledge/android/MASVS-PLATFORM/MASTG-KNOW-0132/",
        "publisher": "OWASP",
    },
)


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4", "br"} and not self.skip_depth:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        elif tag in {"p", "div", "li", "h1", "h2", "h3", "h4"} and not self.skip_depth:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth:
            text = " ".join(data.split())
            if text:
                self.parts.append(text)

    def text(self) -> str:
        return "\n".join(part for part in self.parts if part).strip()


class SourceFetchError(RuntimeError):
    pass


class ApprovedSourceFetcher:
    """Fetches only fixed URLs in APPROVED_SOURCES; task text cannot add URLs."""

    def __init__(self, timeout: float = 25.0, max_chars: int = 12000):
        self.timeout = timeout
        self.max_chars = max_chars

    def fetch_all(self) -> list[dict[str, str]]:
        documents = []
        for source in APPROVED_SOURCES:
            request = Request(
                source["url"],
                headers={"User-Agent": "AndyResearchBot/0.2 (source-backed research)"},
            )
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    raw = response.read(2_000_000)
                    charset = response.headers.get_content_charset() or "utf-8"
                html = raw.decode(charset, errors="replace")
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                raise SourceFetchError(
                    f"Could not retrieve approved source {source['source_id']}: {exc}"
                ) from exc

            parser = _TextExtractor()
            parser.feed(html)
            excerpt = parser.text()[: self.max_chars]
            if not excerpt:
                raise SourceFetchError(
                    f"Approved source {source['source_id']} returned no readable text."
                )
            documents.append({
                **source,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "excerpt": excerpt,
            })
        return documents
