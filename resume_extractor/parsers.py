"""Text parsers for supported resume formats."""

from __future__ import annotations

from pathlib import Path


class ResumeParseError(ValueError):
    """Raised when a resume cannot be parsed safely."""


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


def parse_file(path: str | Path) -> str:
    """Return text from a PDF or DOCX file.

    Parsing is entirely local. Image-only/scanned PDFs are rejected with a clear
    message because OCR is intentionally not performed by this small project.
    """
    resume_path = Path(path)
    if not resume_path.is_file():
        raise FileNotFoundError(f"Resume not found: {resume_path}")

    suffix = resume_path.suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ResumeParseError(
            f"Unsupported file type '{suffix or '(none)'}'. Use PDF or DOCX."
        )

    if suffix == ".pdf":
        return _parse_pdf(resume_path)
    return _parse_docx(resume_path)


def _parse_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:  # malformed/encrypted input varies by pypdf version
        raise ResumeParseError(f"Could not read PDF: {exc}") from exc

    text = "\n".join(page for page in pages if page).strip()
    if not text:
        raise ResumeParseError(
            "No selectable text found in PDF. The file may be scanned; run OCR first."
        )
    return text


def _parse_docx(path: Path) -> str:
    try:
        from docx import Document

        document = Document(str(path))
    except Exception as exc:
        raise ResumeParseError(f"Could not read DOCX: {exc}") from exc

    chunks: list[str] = []

    # Keep document order for paragraphs and tables. The XML tag test avoids
    # losing table-based resume layouts, which are common in Word templates.
    for child in document.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            text = "".join(node.text or "" for node in child.iter() if node.tag.endswith("}t"))
            if text.strip():
                chunks.append(text.strip())
        elif tag == "tbl":
            for row in child.iter():
                if not row.tag.endswith("}tr"):
                    continue
                cells: list[str] = []
                for cell in row:
                    if cell.tag.endswith("}tc"):
                        value = " ".join(
                            node.text or "" for node in cell.iter() if node.tag.endswith("}t")
                        ).strip()
                        if value:
                            cells.append(value)
                if cells:
                    chunks.append(" | ".join(cells))

    # Contact details sometimes live in headers or footers.
    for section in document.sections:
        for container in (section.header, section.footer):
            for paragraph in container.paragraphs:
                if paragraph.text.strip():
                    chunks.append(paragraph.text.strip())

    text = "\n".join(chunks).strip()
    if not text:
        raise ResumeParseError("No text found in DOCX.")
    return text

