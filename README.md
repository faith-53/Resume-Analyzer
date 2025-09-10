# AI Resume Analyzer

An interactive Streamlit app that analyzes resumes for keyword alignment with a target job description, ATS-friendliness, and provides AI-powered improvement suggestions.

## Features
- Upload resume (PDF/DOCX)
- Paste or upload target job description
- Keyword matching and missing skills
- ATS heuristics: sections, structure, readability
- AI suggestions via OpenAI
- Export suggestions to TXT/DOCX
- Dashboard to compare multiple analyses
- LinkedIn (and generic) job description ingestion via URL (best-effort)

## Quick Start
1. Create and activate a virtual environment.
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Download spaCy model (small English):
```bash
python -m spacy download en_core_web_sm
```
4. Set environment variable `OPENAI_API_KEY` or create a `.env` file with:
```bash
OPENAI_API_KEY=your_key_here
```
5. Run the app:
```bash
streamlit run app.py
```

## Usage Tips
- Use the sidebar to navigate: Analyze | Dashboard | LinkedIn JD
- On LinkedIn JD page, paste a job URL and fetch text. Some pages require sign-in; results are best-effort.
- After running analyses, the Dashboard shows a summary table and details for each run.
- Export AI suggestions from the Analyze page as TXT/DOCX.

## Notes
- If PDF text extraction fails, try converting to DOCX.
- OpenAI is optional; the app will still run and provide heuristic results without it.

## Stretch Goals
- Export improved resume suggestions (implemented)
- Dashboard for multiple resumes (implemented)
- LinkedIn job description ingestion (implemented)
