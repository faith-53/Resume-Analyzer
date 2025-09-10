from typing import Dict, List
import re
import textwrap

import textstat

SECTION_PATTERNS = [
	r"summary|objective",
	r"experience|employment|work history",
	r"education",
	r"skills|technologies|technical skills",
	r"projects",
	r"certifications|licenses",
	r"publications",
]

BULLET_CHARS = ["-", "•", "*", "·"]


def _detect_sections(text: str) -> List[str]:
	found = []
	lower = text.lower()
	for pat in SECTION_PATTERNS:
		if re.search(rf"\b({pat})\b", lower):
			found.append(pat.split("|")[0])
	return found


def _check_formatting_issues(text: str) -> List[str]:
	issues: List[str] = []
	# Excessive tables or columns are hard for ATS; heuristic: too many consecutive spaces
	if re.search(r" {4,}", text):
		issues.append("Detected multi-column spacing; consider single-column layout")
	# Images are invisible to ATS
	if re.search(r"\.(png|jpg|jpeg|gif)\b", text, flags=re.I):
		issues.append("Image references found; ATS may not parse images")
	# Uncommon headers/footers
	if len(text) > 20000:
		issues.append("Resume is very long; consider 1-2 pages")
	# Minimal bullets check
	lines = text.splitlines()
	bullet_lines = [ln for ln in lines if ln.strip().startswith(tuple(BULLET_CHARS))]
	if not bullet_lines:
		issues.append("Use bullet points for achievements and responsibilities")
	# Contact info heuristic
	if not re.search(r"@", text):
		issues.append("Email not detected; include professional contact info")
	return issues


def _readability_score(text: str) -> Dict:
	try:
		fk = textstat.flesch_kincaid_grade(text)
		reading_ease = textstat.flesch_reading_ease(text)
	except Exception:
		fk = 0.0
		reading_ease = 0.0
	return {"fk_grade": fk, "reading_ease": reading_ease}


def analyze_ats(text: str) -> Dict:
	sections = _detect_sections(text)
	issues = _check_formatting_issues(text)
	readability = _readability_score(text)
	# Simple scoring heuristic
	score = 60
	if len(sections) >= 4:
		score += 15
	if readability["reading_ease"] >= 50:
		score += 10
	if issues:
		score -= min(20, 5 * len(issues))
	score = max(0, min(100, score))
	return {
		"ats_score": score,
		"sections_found": sections,
		"issues": issues,
		"readability": readability,
	}
