from io import BytesIO
from typing import Union

from docx import Document


def extract_text_from_docx(file_like: Union[BytesIO, any]) -> str:
	try:
		doc = Document(file_like)
		texts = []
		for para in doc.paragraphs:
			texts.append(para.text)
		return "\n".join(texts).strip()
	except Exception:
		return ""
