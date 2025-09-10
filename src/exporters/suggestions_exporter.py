from io import BytesIO
from typing import Tuple

try:
	from docx import Document
except Exception:
	Document = None  # type: ignore


def export_suggestions_txt(suggestions: str) -> Tuple[bytes, str]:
	content = suggestions.encode("utf-8")
	return content, "suggestions.txt"


def export_suggestions_docx(suggestions: str) -> Tuple[bytes, str]:
	if Document is None:
		# Fallback to TXT if python-docx unavailable
		return export_suggestions_txt(suggestions)
	doc = Document()
	for line in suggestions.splitlines():
		doc.add_paragraph(line)
	buf = BytesIO()
	doc.save(buf)
	buf.seek(0)
	return buf.read(), "suggestions.docx"
