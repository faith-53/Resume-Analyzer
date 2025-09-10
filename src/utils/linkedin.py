import re
from typing import Tuple

import requests
from bs4 import BeautifulSoup

HEADERS = {
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def fetch_job_description_from_url(url: str) -> Tuple[str, str]:
	"""Attempt to fetch job description text from a URL.
	Returns (text, note). Note may contain warnings for LinkedIn auth requirements.
	"""
	try:
		resp = requests.get(url, headers=HEADERS, timeout=10)
		resp.raise_for_status()
		html = resp.text
		soup = BeautifulSoup(html, "html.parser")
		# Heuristics: try common containers
		selectors = [
			{"name": "div", "attrs": {"class": re.compile(r"description|job|posting|content", re.I)}},
			{"name": "section", "attrs": {"class": re.compile(r"description|content", re.I)}},
			{"name": "article", "attrs": {}},
		]
		texts = []
		for sel in selectors:
			for node in soup.find_all(sel["name"], attrs=sel.get("attrs", {})):
				text = node.get_text(" ", strip=True)
				if text and len(text) > 200:
					texts.append(text)
		if texts:
			best = max(texts, key=len)
			note = "Fetched content via heuristic extraction."
			if "linkedin.com" in url:
				note += " LinkedIn pages may require sign-in; results can vary."
			return best, note
		return "", "Could not find a clear job description section. Paste text manually if needed."
	except Exception as e:
		return "", f"Failed to fetch URL: {e}. Paste text manually if needed."
