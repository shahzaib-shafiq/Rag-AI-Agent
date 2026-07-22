from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


def load_pdf_pages(pdf_path: Path) -> list[PageText]:
    reader = PdfReader(str(pdf_path))
    pages: list[PageText] = []

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        cleaned = text.strip()
        if cleaned:
            pages.append(PageText(page=index + 1, text=cleaned))

    return pages
