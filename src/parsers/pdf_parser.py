from io import BytesIO
from typing import Union

from PyPDF2 import PdfReader


def extract_text_from_pdf(file_like: Union[BytesIO, any]) -> str:
	try:
		reader = PdfReader(file_like)
		texts = []
		for page in reader.pages:
			texts.append(page.extract_text() or "")
		return "\n".join(texts).strip()
	except Exception:
		return ""
