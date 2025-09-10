import os
from typing import Optional, Tuple, List, Dict

import streamlit as st
from dotenv import load_dotenv

from src.parsers.pdf_parser import extract_text_from_pdf
from src.parsers.docx_parser import extract_text_from_docx
from src.parsers.text_utils import clean_text
from src.analyzers.keywords import analyze_keyword_alignment
from src.analyzers.ats import analyze_ats
from src.suggestions.openai_suggester import generate_improvement_suggestions
from src.exporters.suggestions_exporter import export_suggestions_txt, export_suggestions_docx
from src.utils.linkedin import fetch_job_description_from_url

load_dotenv()

st.set_page_config(page_title="AI Resume Analyzer", layout="wide")


if "analyses" not in st.session_state:
	st.session_state["analyses"] = []


def read_resume(upload) -> str:
	if upload is None:
		return ""
	name = upload.name.lower()
	if name.endswith(".pdf"):
		return extract_text_from_pdf(upload)
	if name.endswith(".docx"):
		return extract_text_from_docx(upload)
	return upload.read().decode("utf-8", errors="ignore")


def read_job_description(upload, text) -> str:
	if upload is not None:
		name = upload.name.lower()
		if name.endswith(".pdf"):
			return extract_text_from_pdf(upload)
		if name.endswith(".docx"):
			return extract_text_from_docx(upload)
		return upload.read().decode("utf-8", errors="ignore")
	return text or ""


def analyze_once(resume_text: str, job_description: str, label: str) -> Dict:
	clean_resume = clean_text(resume_text)
	clean_jd = clean_text(job_description) if job_description else ""
	kw_result = analyze_keyword_alignment(clean_resume, clean_jd)
	ats_result = analyze_ats(resume_text)
	return {
		"label": label,
		"kw": kw_result,
		"ats": ats_result,
		"resume_excerpt": clean_resume[:5000],
		"jd_excerpt": clean_jd[:5000],
	}


def page_analyze():
	st.title("AI Resume Analyzer")
	st.caption("Analyze keyword alignment, ATS-friendliness, and get AI suggestions")

	col_left, col_right = st.columns(2)

	with col_left:
		st.subheader("1) Upload Resume")
		resume_file = st.file_uploader("Upload PDF or DOCX", type=["pdf", "docx"], key="resume")
		resume_text = read_resume(resume_file)
		if resume_text:
			st.success("Resume loaded")
			with st.expander("Preview Resume Text"):
				st.text_area("", resume_text[:5000], height=200)

	with col_right:
		st.subheader("2) Job Description")
		jd_file = st.file_uploader("(Optional) Upload JD (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"], key="jd")
		jd_text_input = st.text_area("Or paste job description", height=200)
		job_description = read_job_description(jd_file, jd_text_input)
		if job_description:
			st.success("Job description ready")

	st.markdown("---")
	analyze_clicked = st.button("Analyze", type="primary", use_container_width=True)

	if analyze_clicked:
		if not resume_text:
			st.error("Please upload a resume.")
			st.stop()
		if not job_description:
			st.warning("No job description provided. Analysis will focus on ATS only.")

		with st.spinner("Running analyses..."):
			result = analyze_once(resume_text, job_description, label=resume_file.name if resume_file else "Resume")
			st.session_state["analyses"].append(result)

		st.subheader("Results")
		col1, col2 = st.columns(2)

		with col1:
			st.markdown("**Keyword Alignment**")
			st.metric("Match Score", f"{result['kw']['match_score']}%")
			st.write("Top Matched Keywords:", ", ".join(result["kw"]["top_matched_keywords"]) or "-")
			st.write("Missing High-Value Keywords:")
			if result["kw"]["missing_keywords"]:
				st.write(", ".join(result["kw"]["missing_keywords"]))
			else:
				st.write("None detected")

		with col2:
			st.markdown("**ATS Friendliness**")
			st.metric("ATS Score", f"{result['ats']['ats_score']}%")
			st.write("Sections Found:", ", ".join(result["ats"]["sections_found"]) or "-")
			st.write("Issues:")
			if result["ats"]["issues"]:
				for issue in result["ats"]["issues"]:
					st.write(f"- {issue}")
			else:
				st.write("No major issues detected")

		st.markdown("---")
		st.subheader("AI Suggestions & Export")
		api_key = os.getenv("OPENAI_API_KEY", "")
		if not api_key:
			st.info("Set OPENAI_API_KEY to enable AI suggestions.")
			suggestions = (
				"Consider adding missing keywords and addressing ATS issues listed above."
			)
		else:
			with st.spinner("Generating suggestions..."):
				suggestions = generate_improvement_suggestions(result["kw"], result["ats"], result["resume_excerpt"], result["jd_excerpt"])
			st.write(suggestions)

			# Export buttons
			txt_bytes, txt_name = export_suggestions_txt(suggestions)
			st.download_button("Download Suggestions (TXT)", txt_bytes, file_name=txt_name, mime="text/plain")
			docx_bytes, docx_name = export_suggestions_docx(suggestions)
			st.download_button("Download Suggestions (DOCX)", docx_bytes, file_name=docx_name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def page_dashboard():
	st.title("Resume Analyses Dashboard")
	st.caption("Compare multiple resume analyses")

	analyses: List[Dict] = st.session_state.get("analyses", [])
	if not analyses:
		st.info("No analyses yet. Run an analysis on the Analyze page.")
		return

	# Summary table
	rows = []
	for idx, a in enumerate(analyses):
		rows.append({
			"#": idx + 1,
			"Label": a["label"],
			"Match Score": a["kw"]["match_score"],
			"ATS Score": a["ats"]["ats_score"],
			"Missing Keywords": ", ".join(a["kw"]["missing_keywords"][:8])
		})
	st.dataframe(rows, use_container_width=True)

	sel = st.selectbox("Select an analysis to view details", options=list(range(len(analyses))), format_func=lambda i: analyses[i]["label"]) 
	chosen = analyses[sel]
	st.markdown("---")
	col1, col2 = st.columns(2)
	with col1:
		st.markdown("**Keyword Alignment**")
		st.metric("Match Score", f"{chosen['kw']['match_score']}%")
		st.write("Missing Keywords:")
		st.write(", ".join(chosen["kw"]["missing_keywords"]) or "-")
	with col2:
		st.markdown("**ATS**")
		st.metric("ATS Score", f"{chosen['ats']['ats_score']}%")
		st.write("Issues:")
		for issue in chosen["ats"]["issues"]:
			st.write(f"- {issue}")


def page_linkedin():
	st.title("LinkedIn Job Description Ingestion")
	st.caption("Paste a LinkedIn (or other) job description URL to fetch text")
	url = st.text_input("Job description URL")
	if st.button("Fetch"):
		if not url:
			st.error("Please enter a URL")
			st.stop()
		with st.spinner("Fetching and extracting description..."):
			text, note = fetch_job_description_from_url(url)
			if text:
				st.success("Fetched job description")
				st.write(note)
				with st.expander("Preview Extracted Text"):
					st.text_area("", text[:8000], height=300)
				st.session_state["last_fetched_jd"] = text
			else:
				st.warning(note)


def main() -> None:
	st.sidebar.title("Navigation")
	page = st.sidebar.radio("Go to", ["Analyze", "Dashboard", "LinkedIn JD"], index=0)
	if page == "Analyze":
		page_analyze()
	elif page == "Dashboard":
		page_dashboard()
	else:
		page_linkedin()


if __name__ == "__main__":
	main()
