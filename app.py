"""
AI Resume Analyzer | Gemini 3.8 Flash
Main application entry point: assembly, initialization, and launch.
"""
import os
import gradio as gr
from config import (
    CUSTOM_CSS,
    logger,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    MAX_RESUME_CHARS,
    MAX_JD_CHARS,
    MAX_PDF_SIZE_BYTES,
    MAX_PDF_PAGES,
    MIN_EXTRACTED_CHARS,
    REPORT_DIR,
)
from services.gemini_service import (
    init_gemini_client,
    CategoryScores,
    AnalysisResult,
    extract_json_payload,
    is_transient_error,
    generate_content_with_retry,
    sanitize_output_markdown,
    build_analysis_prompt,
    execute_resume_analysis,
)
from services.pdf_service import extract_text_from_pdf
from services.scoring_service import (
    build_score_dashboard,
    calculate_reconciled_score,
)
from services.export_service import (
    generate_report_file,
    cleanup_old_reports,
)
from ui.layout import (
    create_ui,
    analyze_resume,
)

# Auto-load GEMINI_API_KEY from local .env if not yet set in environment
if not os.environ.get("GEMINI_API_KEY"):
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("GEMINI_API_KEY="):
                    os.environ["GEMINI_API_KEY"] = line_str.split("=", 1)[1].strip()

# Initialize Gemini Client if API key is present
client = None
if os.environ.get("GEMINI_API_KEY"):
    try:
        client = init_gemini_client()
    except Exception as e:
        logger.warning("Could not initialize Gemini Client on startup: %s", e)

# Assemble Gradio UI Application
app = create_ui(client=client)

def ensure_port_available(port: int = 7860):
    """If port is occupied by an orphaned python process, terminate it to avoid launch collision."""
    import socket, subprocess, time
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                logger.info("Port %s is currently occupied. Terminating previous process...", port)
                cmd = (
                    f'$p = (Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue).OwningProcess; '
                    'if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue }'
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True)
                time.sleep(1.5)
    except Exception as e:
        logger.debug("Port check note: %s", e)

if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        logger.info(
            "GEMINI_API_KEY not detected on startup. "
            "You can enter or configure your Gemini API Key directly in the web browser at http://localhost:7860."
        )
    ensure_port_available(7860)
    logger.info("Launching AI Resume Analyzer on http://localhost:7860...")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=CUSTOM_CSS,
    )
