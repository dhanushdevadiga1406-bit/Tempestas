# Tempestas — Weather forecasting app

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

2. (Optional) Configure Gemini integration by setting `GEMINI_API_KEY` and `GEMINI_ENDPOINT` in your environment or copy `.env.example` to `.env`.

3. Run the server:

```bash
python server.py
```

4. Open http://localhost:5000 in your browser.

Notes

- The backend geocodes places using Nominatim (OpenStreetMap) and fetches weather from Open-Meteo.
- If you provide a Gemini-compatible endpoint and API key, the server will forward a summarization request to it. Configure `GEMINI_ENDPOINT` accordingly.
