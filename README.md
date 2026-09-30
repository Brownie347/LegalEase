# LegalEase - AI Legal Document Generator

Streamlit frontend + FastAPI backend + Google Gemini. Generates contracts, NDAs,
leases, offer letters and more, lets you edit the draft, and exports it as
.txt, .docx (logo, terms table, footer) and .pdf (logo + footer on every page).

## Project layout

```
LegalEase/
├── ai_core/
│   ├── gemini_generator.py   # Gemini call, retries, model fallback
│   └── generator.py          # sanitize_text, format_docx, format_pdf, format_html_preview
├── frontend/app.py           # Streamlit UI
├── legalEaseAPI/
│   ├── main.py               # FastAPI app, GET /
│   └── routes.py             # POST /generate, GET /health
├── Image/                    # Logo.png (documents) + inverseLogo.png (dark web UI)
├── scripts/generate_logos.py # regenerates the placeholder logos
├── tests/                    # pytest suite (Gemini is mocked)
├── config.py                 # settings loaded from .env
├── .env.example              # copy to .env and add your key
├── requirements.txt / requirements-dev.txt
└── run.sh / run.bat          # start backend + frontend together
```

## Setup (VS Code, Python 3.10+)

```bash
# 1. open the LegalEase folder in VS Code (File > Open Folder), then Terminal > New Terminal

# 2. create + activate a virtual environment
python -m venv venv
venv\Scripts\activate            # Windows PowerShell / cmd
source venv/bin/activate         # macOS / Linux

# 3. install dependencies
pip install -r requirements.txt

# 4. add your Gemini key
copy .env.example .env           # Windows      (macOS/Linux: cp .env.example .env)
# open .env and replace your_api_key_here  (key: https://aistudio.google.com/apikey)
```

In VS Code press `Ctrl+Shift+P` > **Python: Select Interpreter** > choose the `venv` one.

## Run

Two terminals (both with the venv active, both in the project root):

```bash
# Terminal 1 - backend  -> http://127.0.0.1:8000  (docs at /docs)
uvicorn legalEaseAPI.main:app --reload

# Terminal 2 - frontend -> http://localhost:8501
streamlit run frontend/app.py
```

Shortcut: `run.bat` (Windows) or `./run.sh` (macOS/Linux/Git-Bash).

## Test

```bash
pip install -r requirements-dev.txt
pytest -q                        # 26 tests, no API key or internet needed
```

Manual check: open http://localhost:8501 and enter

| Field | Example |
|---|---|
| Document Type | Freelance Work Contract |
| Parties Involved | Jane Doe (Service Provider), TechNova Inc. (Client) |
| Terms & Conditions | Work must be delivered by May 15, 2025; Payment within 7 days of invoice; The client retains intellectual property rights; Confidentiality must be maintained at all times |
| Effective Date | April 15, 2025 |

Click **Generate Document**, then try **Click to Edit Document** and the three
download buttons. API check without the UI: `curl http://localhost:8000/health`.

## Configuration (.env)

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | - | required |
| `GEMINI_MODEL` | `gemini-3-flash-preview` | primary model |
| `GEMINI_FALLBACK_MODELS` | `gemini-3.1-pro-preview,gemini-3.1-flash-lite-preview` | tried if the primary is missing/overloaded |
| `BACKEND_URL` | `http://localhost:8000` | where Streamlit finds FastAPI |
| `FOOTER_TEXT` | LegalEase Inc. ... | footer in DOCX/PDF |

**Model note:** the brief specifies `gemini-1.5-pro`, but Google has retired the
1.5 family (the API returns 404) and is also shutting down 2.5. Model names
change often - check https://ai.google.dev/gemini-api/docs/models and update
`GEMINI_MODEL` if you see "All configured models failed".

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Cannot reach the backend" | start the uvicorn terminal first |
| "GEMINI_API_KEY is not set" | create `.env` (not `.env.example`) and restart uvicorn |
| "API key was rejected" | re-copy the key from AI Studio, no quotes or spaces |
| "All configured models failed" | update `GEMINI_MODEL` (see model note) |
| `ModuleNotFoundError: fpdf` or odd PDF errors | `pip uninstall fpdf` then `pip install fpdf2` (the two packages clash) |
| Port already in use | `uvicorn ... --port 8001` and set `BACKEND_URL=http://localhost:8001` |

AI drafts are not legal advice; have a qualified lawyer review before signing.
