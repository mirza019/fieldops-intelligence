# Streamlit Community Cloud

Push the repository to GitHub, create a Community Cloud app, select `streamlit_app/app.py`, and use Python 3.12. The checked-in `data/demo` Parquet snapshot avoids localhost PostgreSQL and credentials. Optional secrets are `GEMINI_API_KEY`, `POWERBI_REPORT_URL`, and `POWERBI_PUBLIC_EMBED_URL`; none is required.

Verify all eight navigation modes, filters, charts, evidence output, read-only Lean workspace, simulation, and pipeline view. A missing snapshot means the repository omitted `data/demo`; regenerate it with `python -m scripts.build_demo_data --profile small`. Do not invent a public URL when deployment has not been performed.
