from typing import Dict, List, Tuple

import spacy
from rapidfuzz import fuzz

from src.parsers.text_utils import clean_text, tokenize_lower, remove_stopwords

# Lazy-load spacy model
_NLP = None

def _nlp():
	global _NLP
	if _NLP is None:
		try:
			_NLP = spacy.load("en_core_web_sm")
		except OSError:
			# Model not available, create blank English as fallback
			_NLP = spacy.blank("en")
	return _NLP


def _extract_noun_phrases_and_entities(text: str) -> List[str]:
	doc = _nlp()(text)
	phrases = set()
	# Noun chunks when available
	if hasattr(doc, "noun_chunks"):
		for chunk in getattr(doc, "noun_chunks", []):
			phrases.add(chunk.text.strip().lower())
	# Entities
	for ent in doc.ents:
		phrases.add(ent.text.strip().lower())
	return list(phrases)


def _top_keywords(text: str, max_items: int = 30) -> List[str]:
	tokens = remove_stopwords(tokenize_lower(text))
	# naive frequency
	freq: Dict[str, int] = {}
	for t in tokens:
		freq[t] = freq.get(t, 0) + 1
	# include noun phrases/entities to capture multi-word terms
	for phrase in _extract_noun_phrases_and_entities(text):
		freq[phrase] = freq.get(phrase, 0) + 2
	return [k for k, _ in sorted(freq.items(), key=lambda kv: kv[1], reverse=True)[:max_items]]


def _match_keywords(resume_terms: List[str], jd_terms: List[str]) -> Tuple[List[str], List[str]]:
	matched: List[str] = []
	missing: List[str] = []
	for jd in jd_terms:
		best = 0
		best_term = None
		for r in resume_terms:
			score = fuzz.token_set_ratio(jd, r)
			if score > best:
				best = score
				best_term = r
		if best >= 80:
			matched.append(best_term or jd)
		else:
			missing.append(jd)
	return matched, missing


def analyze_keyword_alignment(resume_text: str, jd_text: str) -> Dict:
	resume_text = clean_text(resume_text)
	jd_text = clean_text(jd_text)
	resume_terms = _top_keywords(resume_text, max_items=60)
	jd_terms = _top_keywords(jd_text, max_items=40) if jd_text else []
	matched, missing = _match_keywords(resume_terms, jd_terms)
	match_score = 0
	if jd_terms:
		match_score = int(round(100 * (len(matched) / max(1, len(jd_terms)))))
	result = {
		"match_score": match_score,
		"top_matched_keywords": matched[:15],
		"missing_keywords": missing[:15],
		"resume_terms": resume_terms,
		"jd_terms": jd_terms,
	}
	return result
