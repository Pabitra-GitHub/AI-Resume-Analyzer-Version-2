# AI-Powered Resume & ATS Analyzer 🚀

An intelligent, production-ready Resume & ATS (Applicant Tracking System) Analyzer powered by **Google Gemini AI** and **Gradio**.

This platform evaluates resumes against job descriptions, calculates multi-dimensional ATS compatibility scores, identifies keyword and skill gaps, and generates strategic interview preparation guides.

---

## 🌟 Key Features

- **Multi-Factor ATS Compatibility Scoring**: Evaluates match rate across 4 key pillars:
  - 🔑 Keyword Match (40%)
  - 💼 Experience Relevance (30%)
  - 🛠️ Technical & Hard Skills (20%)
  - 📄 Resume Formatting & Readability (10%)
- **Flexible Input**: Upload resume PDFs (with page count & size validation) or paste text directly.
- **Deep Gap Analysis**: Highlights missing critical skills, weak bullet points, and formatting warnings.
- **Actionable Optimization**: Provides line-by-line rewrite suggestions using the STAR/XYZ formula.
- **Interview Strategy Deck**: Tailored technical questions, behavioral scenarios, and talking points.
- **Exportable Reports**: Download comprehensive analysis reports directly in formatted Markdown.
- **Flexible Gemini Model Selection**: Supports `gemini-3.5-flash`, `gemini-3.5-flash-lite`, `gemini-3.8-flash`, and others.
- **Secure Key Management**: Set `GEMINI_API_KEY` via `.env` or input it securely through the browser interface.

---

## 🛠️ Tech Stack

- **Backend / Core**: Python 3.10+
- **AI Engine**: Google Gemini API (`google-genai` SDK)
- **Web UI**: Gradio 6.x
- **PDF Extraction**: `pypdf`
- **Sanitization & Security**: `bleach`, `pydantic`

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/AI-Resume-Analyzer.git
cd AI-Resume-Analyzer
```

### 2. Set Up Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and add your Google Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

*(You can get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/)).*

### 5. Run the Application

```bash
python app.py
```

Open your browser and navigate to:
```
http://localhost:7860
```

---

## 📁 Project Structure

```
├── app.py                  # Application entry point & Gradio launch
├── config.py               # Constants, scoring weights, themes & styles
├── requirements.txt        # Python package dependencies
├── .env.example            # Template for environment configuration
├── .gitignore              # Pre-configured Git ignore rules
├── services/
│   ├── gemini_service.py   # Gemini API client, retries, and prompt generation
│   ├── pdf_service.py      # PDF text extraction and validation
│   ├── scoring_service.py  # Multi-factor score calculation and UI dashboard
│   └── export_service.py   # Report export and temporary file cleanup
└── ui/
    └── layout.py           # Gradio interface layout and event handlers
```

---

## 🔒 Security & Privacy

- **No Stored Secrets**: API keys in `.env` are strictly excluded from version control via `.gitignore`.
- **Private Data Safe**: Resumes and candidate data are processed in-memory and not stored on any remote database.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
