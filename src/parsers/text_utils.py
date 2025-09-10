import re
from typing import List

import nltk
from nltk.corpus import stopwords

# Ensure required NLTK data is available
try:
	_ = stopwords.words("english")
except LookupError:
	nltk.download("stopwords")
	nltk.download("punkt")


def clean_text(text: str) -> str:
	if not text:
		return ""
	text = text.replace("\r", " ").replace("\n", " ")
	text = re.sub(r"\s+", " ", text)
	return text.strip()


def tokenize_lower(text: str) -> List[str]:
	if not text:
		return []
	text = text.lower()
	# Simple word tokens; fallback if punkt missing
	try:
		from nltk.tokenize import word_tokenize
		tokens = word_tokenize(text)
	except Exception:
		tokens = re.findall(r"[a-zA-Z0-9+#.]+", text)
	return tokens


def remove_stopwords(tokens: List[str]) -> List[str]:
	if not tokens:
		return []
	stop = set(stopwords.words("english"))
	return [t for t in tokens if t not in stop and len(t) > 1]
