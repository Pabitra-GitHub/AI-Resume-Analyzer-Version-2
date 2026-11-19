import os
import json
import time
import math
import concurrent.futures
import httpx
from pydantic import ValidationError
import gradio as gr
from google.genai import errors as genai_errors

from config import (
    logger,
    CUSTOM_CSS,
    MAX_RESUME_CHARS,
    MAX_JD_CHARS,
    PRIMARY_MODEL,
    FREE_TEXT_OUTPUT_MODELS,
)
from services.pdf_service import extract_text_from_pdf
from services.scoring_service import (
    build_score_dashboard,
    build_loading_dashboard,
    build_ats_progress_line,
    build_skeleton_markdown,
    calculate_reconciled_score,
)
from services.gemini_service import (
    init_gemini_client,
    get_masked_api_key,
    validate_gemini_api_key,
    save_api_key_to_env,
    execute_resume_analysis,
    sanitize_output_markdown,
)
from services.export_service import generate_report_file

def analyze_resume(pdf_file, pasted_resume, jd_text, company_name, depth, client=None, model_id=PRIMARY_MODEL, progress=None):
    """
    Main controller generator for resume analysis:
    - Checks API key presence gracefully
    - Validates inputs & PDF extraction
    - Emits continuous 1% to 100% live progress updates without discrete jumps
    - Runs Gemini Flash analysis asynchronously in a background thread while interpolating progress
    - Renders live ATS progress tracker line & loading radar dashboard percent-by-percent
    - Performs input truncation check with visible UI banners
    - Yields ONE authoritative reconciled final score upon completion
    - Catches typed exceptions with server-side logging and safe UI messages
    """
    # 0. API Key Pre-check
    clean_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not clean_key and client is None:
        err_html = """<div class="status-pill error">⚠️ Error: Gemini API Key is required. Please click '🔑 Configure API Key' in the header to enter your key.</div>"""
        missing_dash = build_score_dashboard(
            0,
            {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0},
            "Gemini API Key missing. Please click '🔑 Configure API Key' in the top header to enter and activate your key.",
            ["Click 'Configure API Key' in the header", "Paste your free Gemini key from Google AI Studio", "Click Save & Connect"]
        )
        yield (
            err_html,
            missing_dash,
            "",
            "### ⚠️ Gemini API Key Required\nPlease click the **🔑 Configure API Key** button in the header bar above, paste your Gemini API key from Google AI Studio, and click **Save & Connect**.",
            "", "", "", None
        )
        return

    model_labels = dict(FREE_TEXT_OUTPUT_MODELS)
    selected_model_label = model_labels.get(model_id, model_id)

    # Reusable Skeleton Placeholders
    ats_loading_md = build_skeleton_markdown("Extracting ATS Keywords & Compliance Rules", "Evaluating candidate keywords against required and preferred job qualifications...")
    cover_letter_skeleton = build_skeleton_markdown("Synthesizing Executive Cover Letter", "Generating strategic narrative alignment for target role and organization...")
    interview_skeleton = build_skeleton_markdown("Formulating Interview Playbook & STAR Strategy", "Anticipating behavioral/technical challenges and drafting structured answer frameworks...")
    bullet_skeleton = build_skeleton_markdown("Crafting High-Impact Quantified Bullet Rewrites", "Transforming passive responsibilities into metrics-driven achievement statements...")

    def render_loading_frame(p: int, custom_msg: str = ""):
        p_clamped = max(1, min(100, int(p)))
        stat_html = f"""<div class="status-pill running"><span class="pulse-dot"></span> Auditing with {selected_model_label}... ({p_clamped}%)</div>"""
        dash_html = build_loading_dashboard(
            model_name=selected_model_label,
            depth=depth,
            percent=p_clamped,
        )
        bar_html = build_ats_progress_line(
            percent=p_clamped,
            is_completed=(p_clamped >= 100),
            custom_status=custom_msg or None
        )
        return (
            stat_html,
            dash_html,
            bar_html,
            ats_loading_md,
            cover_letter_skeleton,
            interview_skeleton,
            bullet_skeleton,
            None,
        )

    # Initial frame at 1%
    yield render_loading_frame(1, "Audit Initiated • Verifying input parameters...")
    if progress:
        progress(0.01, desc=f"Auditing with {selected_model_label} (1%)")

    # 1. Validation & PDF Extraction
    resume_text = ""
    if pdf_file is not None:
        for p in range(2, 6):
            yield render_loading_frame(p, "Parsing PDF text structure & encoding...")
            if progress:
                progress(p / 100.0, desc=f"Auditing with {selected_model_label} ({p}%)")
            time.sleep(0.015)

        resume_text = extract_text_from_pdf(pdf_file)
        if resume_text.startswith("Error reading PDF:"):
            err_html = f"""<div class="status-pill error">⚠️ {resume_text}</div>"""
            yield err_html, "", "", "", "", "", "", None
            return
    else:
        for p in range(2, 6):
            yield render_loading_frame(p, "Parsing resume plain text & encoding...")
            if progress:
                progress(p / 100.0, desc=f"Auditing with {selected_model_label} ({p}%)")
            time.sleep(0.015)

    if not resume_text.strip() and pasted_resume.strip():
        resume_text = pasted_resume.strip()

    if not resume_text.strip():
        err_html = """<div class="status-pill error">⚠️ Error: Please upload a PDF resume or paste resume plain text.</div>"""
        yield err_html, "", "", "", "", "", "", None
        return

    if not jd_text.strip():
        err_html = """<div class="status-pill error">⚠️ Error: Target Job Description is required for accurate ATS scoring.</div>"""
        yield err_html, "", "", "", "", "", "", None
        return

    # Truncation check & warning generation
    for p in range(6, 11):
        yield render_loading_frame(p, "Verifying character boundaries & input tokens...")
        if progress:
            progress(p / 100.0, desc=f"Auditing with {selected_model_label} ({p}%)")
        time.sleep(0.015)

    orig_resume_len = len(resume_text)
    orig_jd_len = len(jd_text)

    truncated_resume = resume_text[:MAX_RESUME_CHARS]
    truncated_jd = jd_text[:MAX_JD_CHARS]

    truncation_warnings = []
    if orig_resume_len > MAX_RESUME_CHARS:
        truncation_warnings.append(
            f"Resume text was truncated from {orig_resume_len:,} to {MAX_RESUME_CHARS:,} characters ({orig_resume_len - MAX_RESUME_CHARS:,} omitted)."
        )
    if orig_jd_len > MAX_JD_CHARS:
        truncation_warnings.append(
            f"Job description was truncated from {orig_jd_len:,} to {MAX_JD_CHARS:,} characters ({orig_jd_len - MAX_JD_CHARS:,} omitted)."
        )

    truncation_banner_html = ""
    truncation_banner_md = ""
    if truncation_warnings:
        items_html = "".join([f"<li style='margin-bottom: 2px;'>{w}</li>" for w in truncation_warnings])
        truncation_banner_html = f"""
        <div class="truncation-warning-banner" style="margin-top: 10px; padding: 10px 14px; border-radius: 10px; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); color: #fbbf24; font-size: 0.85rem; line-height: 1.45;">
            <div style="font-weight: 700; margin-bottom: 4px; display: flex; align-items: center; gap: 6px;">
                <span>⚠️</span> <span>Notice: Input Truncated for Analysis</span>
            </div>
            <ul style="margin: 0; padding-left: 20px;">
                {items_html}
            </ul>
        </div>
        """
        items_md = "\n".join([f"- ⚠️ **{w}**" for w in truncation_warnings])
        truncation_banner_md = f"""<div style="padding: 12px 16px; margin-bottom: 16px; border-radius: 8px; background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.35); color: #fbbf24; font-size: 0.88rem; line-height: 1.5;">\n<strong>⚠️ Notice: Input Exceeded Capacity & Was Truncated:</strong>\n\n{items_md}\n</div>\n\n"""

    try:
        if client is None:
            client = init_gemini_client()

        # Execute Gemini analysis in background worker thread while driving smooth percent-by-percent progress
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            analysis_future = executor.submit(
                execute_resume_analysis,
                gemini_client=client,
                truncated_resume=truncated_resume,
                truncated_jd=truncated_jd,
                company_name=company_name,
                depth=depth,
                model_id=model_id,
            )

            api_start_time = time.time()
            current_p = 10

            # Granular percent-by-percent interpolation while awaiting the API response
            while not analysis_future.done():
                elapsed = time.time() - api_start_time
                # Asymptotic curve designed for Gemini Flash latency profile (~4-15s)
                # Reaches ~50% at 3s, ~75% at 6s, ~88% at 10s, ~95% at 15s, asymptotes smoothly to 99%
                target_p = min(99, int(10 + 89 * (1.0 - math.exp(-elapsed / 4.8))))

                if target_p > current_p:
                    current_p += 1
                    yield render_loading_frame(current_p)
                    if progress:
                        progress(current_p / 100.0, desc=f"Auditing with {selected_model_label} ({current_p}%)")
                    time.sleep(0.045)
                else:
                    time.sleep(0.035)

            # Check if background API execution raised any typed exception
            api_exc = analysis_future.exception()
            if api_exc is not None:
                raise api_exc

            validated_result, model_used = analysis_future.result()

        # Rapid smooth interpolation from current percent to 100%
        while current_p < 100:
            current_p += 1
            yield render_loading_frame(current_p, "Calibrating final rubric score & preparing deliverables...")
            if progress:
                progress(current_p / 100.0, desc=f"Finalizing deliverables ({current_p}%)")
            time.sleep(0.012)

        # Render 100% complete milestone state
        yield render_loading_frame(100, "All 4 ATS Audit Stages Completed Successfully • Authoritative Final Match Calibrated")
        if progress:
            progress(1.0, desc="Analysis Complete & Ready")
        time.sleep(0.12)

        cat_scores = {
            "keywords": validated_result.category_scores.keywords,
            "experience": validated_result.category_scores.experience,
            "skills": validated_result.category_scores.skills,
            "formatting": validated_result.category_scores.formatting,
        }

        overall_score = calculate_reconciled_score(cat_scores, validated_result.overall_score)
        verdict = validated_result.verdict_summary
        quick_wins = validated_result.quick_wins

        ats_completed_bar = build_ats_progress_line(percent=100, is_completed=True)
        ats_completed_md = f"{truncation_banner_md}{sanitize_output_markdown(validated_result.ats_analysis_markdown)}"
        cover_letter_md = sanitize_output_markdown(validated_result.cover_letter_markdown)
        interview_md = sanitize_output_markdown(validated_result.interview_strategy_markdown)
        bullet_md = sanitize_output_markdown(validated_result.bullet_rewrites_markdown)

        # Generate isolated report file
        report_path = generate_report_file(
            model_used=model_used,
            depth=depth,
            company_name=company_name,
            overall_score=overall_score,
            verdict=verdict,
            quick_wins=quick_wins,
            ats_md=ats_completed_md,
            cover_letter_md=cover_letter_md,
            interview_md=interview_md,
            bullet_md=bullet_md,
            truncation_warnings=truncation_warnings,
        )

        # Single Authoritative Final Score Dashboard
        final_dashboard = build_score_dashboard(overall_score, cat_scores, verdict, quick_wins)
        if model_used == model_id:
            model_badge = f"⚡ Selected: {model_labels.get(model_used, model_used)}"
            status_style = ""
        else:
            model_badge = f"🔄 Fallback: {model_labels.get(model_used, model_used)}"
            status_style = "border-color: #f59e0b; color: #fbbf24;"

        ready_status = f"""<div class="status-pill ready" style="{status_style}">✓ Analysis Complete & Ready ({model_badge})</div>{truncation_banner_html}"""

        yield ready_status, final_dashboard, ats_completed_bar, ats_completed_md, cover_letter_md, interview_md, bullet_md, report_path

    except ValidationError as e:
        logger.error("Validation error in resume analysis schema: %s", e, exc_info=True)
        user_err = "The AI model returned an incomplete or unexpected response structure. Please retry your audit."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Schema validation error: {user_err}", ["Retry the analysis", "Ensure inputs have clear context"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except json.JSONDecodeError as e:
        logger.error("JSON decode error in resume analysis: %s", e, exc_info=True)
        user_err = "The AI model returned malformed output that could not be parsed as JSON. Please retry your audit."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"JSON parsing error: {user_err}", ["Retry the audit"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except genai_errors.ClientError as e:
        code = getattr(e, "code", None)
        logger.error("Gemini API ClientError (code=%s): %s", code, e, exc_info=True)
        if code in (401, 403) or "API_KEY" in str(e).upper():
            user_err = "Authentication failed. Please verify that your GEMINI_API_KEY environment variable is configured and valid."
        elif code == 429 or "RESOURCE_EXHAUSTED" in str(e).upper():
            user_err = "API rate limit or quota exceeded. Please wait a brief moment before retrying."
        elif code == 400:
            user_err = "The analysis request was rejected as invalid. Please check your resume and job description content."
        else:
            user_err = "The AI service encountered a client request error. Please verify your inputs and try again."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Client error: {user_err}", ["Check API key and input formatting"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except genai_errors.ServerError as e:
        logger.error("Gemini API ServerError: %s", e, exc_info=True)
        user_err = "The AI service is temporarily experiencing high load or server errors. Please retry in a few moments."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Server error: {user_err}", ["Retry in a few moments"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except genai_errors.APIError as e:
        logger.error("Gemini API general APIError: %s", e, exc_info=True)
        user_err = "An error occurred while communicating with the AI service. Please try again."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Service error: {user_err}", ["Check network and retry"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except (httpx.TransportError, httpx.TimeoutException, ConnectionError, TimeoutError, OSError) as e:
        logger.error("Network / Connection error in analyze_resume: %s", e, exc_info=True)
        user_err = "Network connection to the AI service timed out or was interrupted. Please check your internet connection."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Connection error: {user_err}", ["Check internet connection"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except (KeyError, TypeError, ValueError) as e:
        logger.error("Data processing error in analyze_resume: %s", e, exc_info=True)
        user_err = "An error occurred while processing the audit deliverables. Please try again."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Processing error: {user_err}", ["Retry the analysis"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

    except Exception as e:
        logger.error("Unhandled exception in analyze_resume: %s", e, exc_info=True)
        user_err = "An unexpected error occurred while analyzing the resume. Please check server logs and try again."
        err_status = f"""<div class="status-pill error">⚠️ Error: {user_err}</div>"""
        fallback_dashboard = build_score_dashboard(0, {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0}, f"Unexpected error: {user_err}", ["Check server logs and retry"])
        yield err_status, fallback_dashboard, "", f"### Audit Failed\n{user_err}", "", "", "", None

def create_ui(client=None) -> gr.Blocks:
    """Build and return the complete Gradio Blocks application."""
    with gr.Blocks(title="AI Resume Analyzer | Gemini") as app:
        
        # ── HEADER ROW with BRAND, API KEY BUTTON & THEME TOGGLE ──
        with gr.Row(elem_classes=["header-row"]):
            with gr.Column(scale=7, min_width=280):
                gr.HTML("""
                <div class="header-brand-container">
                    <h1 class="brand-title">
                        <span class="brand-text">RESUME &nbsp;INTELLIGENCE</span>
                        <span class="brand-ai-chip">AI</span>
                        <span class="pill-badge-powered">
                            <span class="pulse-dot"></span>
                            <span>⚡ AI Resume Analyzer</span>
                        </span>
                    </h1>
                </div>
                """)
            with gr.Column(scale=5, min_width=360, elem_classes=["header-controls-col"]):
                with gr.Row(elem_classes=["header-actions-group"]):
                    initial_masked = get_masked_api_key()
                    initial_btn_text = f"🔑 Key: {initial_masked}" if initial_masked else "🔑 Configure API Key"
                    api_key_toggle_btn = gr.Button(
                        initial_btn_text,
                        variant="secondary",
                        elem_id="api-key-toggle-btn",
                        scale=0,
                        min_width=220
                    )
                    theme_btn = gr.Button(
                        "☀️ Light Mode",
                        variant="secondary",
                        elem_id="theme-toggle-btn",
                        scale=0,
                        min_width=120
                    )
                    theme_btn.click(
                        fn=None,
                        js="""() => {
                            const html = document.documentElement;
                            const body = document.body;
                            const isLight = body.classList.toggle('light-mode');
                            if (isLight) {
                                html.classList.add('light-mode');
                                body.classList.remove('dark');
                                html.classList.remove('dark');
                            } else {
                                html.classList.remove('light-mode');
                                body.classList.add('dark');
                                html.classList.add('dark');
                            }
                            document.querySelectorAll('.gradio-container, gradio-app').forEach(el => {
                                if (isLight) {
                                    el.classList.add('light-mode');
                                    el.classList.remove('dark');
                                } else {
                                    el.classList.remove('light-mode');
                                    el.classList.add('dark');
                                }
                            });
                            const btn = document.getElementById('theme-toggle-btn');
                            if (btn) {
                                btn.innerText = isLight ? '🌙 Dark Mode' : '☀️ Light Mode';
                            }
                            return [];
                        }"""
                    )

        # ── EXPANDABLE API KEY CONFIGURATION MODAL / CARD ──
        with gr.Column(visible=False, elem_id="api-key-card", elem_classes=["glass-card", "api-key-settings-card"]) as api_key_panel:
            with gr.Row(elem_classes=["api-key-card-header"]):
                gr.HTML("""
                <div class="api-key-title-group">
                    <div class="pill-heading-lg" style="margin-bottom: 2px;">
                        <span>🔑</span>
                        <span>GOOGLE GEMINI API KEY CONFIGURATION</span>
                        <span class="pill-badge">RUNTIME RECONFIGURABLE</span>
                    </div>
                    <div class="section-subtext">
                        Add, test, or update your Google Gemini API Key at runtime. Changes take effect immediately without restarting the application.
                    </div>
                </div>
                """)
                close_key_btn = gr.Button("✕ Close", elem_id="close-key-btn", scale=0, min_width=75)
            
            with gr.Row(elem_classes=["api-key-inputs-row"]):
                api_key_input = gr.Textbox(
                    label="Google Gemini API Key",
                    placeholder="Paste your AIzaSy... API key here",
                    type="password",
                    value=os.environ.get("GEMINI_API_KEY", ""),
                    scale=6,
                    elem_id="api-key-field"
                )
                persist_key_check = gr.Checkbox(
                    label="Save to .env file",
                    value=True,
                    scale=2,
                    elem_id="persist-key-checkbox"
                )
                save_key_btn = gr.Button(
                    "💾 Save & Connect",
                    variant="primary",
                    scale=2,
                    elem_id="save-key-btn"
                )
                test_key_btn = gr.Button(
                    "🧪 Test Key",
                    variant="secondary",
                    scale=2,
                    elem_id="test-key-btn"
                )
            
            initial_status = f"""<div class="api-key-status-msg ready">🟢 Active Key: {initial_masked} (Connected & Ready)</div>""" if initial_masked else """<div class="api-key-status-msg warning">⚠️ No API Key Configured. Please paste your Gemini API key above and click Save & Connect.</div>"""
            api_key_status_output = gr.HTML(initial_status, elem_id="api-key-status-display")
            
            gr.HTML("""
            <div class="api-key-footer-links">
                <span>Need a free API key?</span>
                <a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" class="api-key-link">
                    ⚡ Get a Free Gemini API Key from Google AI Studio ↗
                </a>
            </div>
            """)

        # ── MAIN 2-COLUMN SECTION: INPUTS (LEFT) & RESUME INTELLIGENCE INSIGHTS (RIGHT) ──
        with gr.Row(elem_classes=["main-workspace-row"], equal_height=True):
            # LEFT COLUMN: Structured Input Glass Cards (Scale 6)
            with gr.Column(scale=6, min_width=340, elem_classes=["workspace-col", "inputs-col"]):
                
                # Step 1: Candidate Resume Card
                with gr.Column(elem_classes=["glass-card", "input-step-card"]):
                    gr.HTML("""
                    <div class="section-header-block">
                        <div class="pill-heading-lg">
                            <span>📄</span>
                            <span>STEP 1: CANDIDATE RESUME</span>
                            <span class="pill-badge">PDF OR TEXT</span>
                        </div>
                        <div class="section-subtext">Upload your PDF resume or paste raw text below for parsing.</div>
                    </div>
                    """)
                    with gr.Row(elem_classes=["resume-input-options"]):
                        with gr.Column(scale=1, min_width=0):
                            pdf_input = gr.File(
                                label="Upload PDF Resume",
                                file_types=[".pdf"],
                                file_count="single",
                                elem_id="pdf-upload",
                                elem_classes=["compact-pdf-upload"]
                            )
                        with gr.Column(scale=1, min_width=0):
                            pasted_resume_input = gr.Textbox(
                                label="Or Paste Resume Plain Text",
                                lines=3,
                                max_lines=8,
                                placeholder="Paste resume text here if no PDF is uploaded...",
                                elem_id="resume-text-input"
                            )

                # Step 2: Target Job Description Card
                with gr.Column(elem_classes=["glass-card", "input-step-card"]):
                    gr.HTML("""
                    <div class="section-header-block">
                        <div class="pill-heading-lg">
                            <span>💼</span>
                            <span>STEP 2: TARGET JOB DESCRIPTION</span>
                            <span class="pill-badge">REQUIRED</span>
                        </div>
                        <div class="section-subtext">Paste the full role description, responsibilities, and required qualifications.</div>
                    </div>
                    """)
                    jd_input = gr.Textbox(
                        label="Job Description & Requirements",
                        lines=4,
                        max_lines=10,
                        placeholder="Paste target job description, responsibilities, and required qualifications here...",
                        elem_id="jd-input",
                        show_label=False
                    )

                # Step 3: Target Company & Calibration Depth
                with gr.Column(elem_classes=["glass-card", "input-step-card", "step3-card"]):
                    gr.HTML("""
                    <div class="section-header-block">
                        <div class="pill-heading-lg">
                            <span>⚙️</span>
                            <span>STEP 3: CALIBRATION & SCOPE</span>
                            <span class="pill-badge">CONFIG</span>
                        </div>
                        <div class="section-subtext">Configure target organization and rubric calibration depth.</div>
                    </div>
                    """)
                    
                    company_input = gr.Textbox(
                        label="Target Company (Optional)",
                        placeholder="Target Company (e.g. Google, Stripe, Microsoft, Startup...)",
                        lines=1
                    )

                    depth_input = gr.Radio(
                        label="Select Calibration Depth",
                        choices=["Standard ATS Scan", "Deep Architectural Review", "Executive Alignment"],
                        value="Deep Architectural Review",
                        elem_classes=["pill-radio-group", "step3-depth-radio"]
                    )

            # RIGHT COLUMN: Dedicated Unified Resume Intelligence Insights (Scale 6)
            with gr.Column(scale=6, min_width=340, elem_classes=["workspace-col", "insights-outer-col"]):
                with gr.Column(elem_classes=["glass-card", "insights-card"]):
                    gr.HTML("""
                    <div class="section-header-block">
                        <div class="pill-heading-lg insights-pill-heading">
                            <span>🧠</span>
                            <span class="insights-title-text">RESUME &nbsp;INTELLIGENCE &nbsp;INSIGHTS</span>
                            <span class="pill-badge">AI EVALUATION</span>
                        </div>
                        <div class="section-subtext">Select model engine, view real-time ATS match rating, category benchmarks, and executive verdict.</div>
                    </div>
                    """)

                    initial_model_dict = dict(FREE_TEXT_OUTPUT_MODELS)
                    initial_model_title = f"⚙️ Engine & Model Selection ({initial_model_dict.get(PRIMARY_MODEL, PRIMARY_MODEL)})"
                    with gr.Accordion(initial_model_title, open=False, elem_classes=["model-accordion"]) as model_accordion:
                        model_input = gr.Radio(
                            choices=FREE_TEXT_OUTPUT_MODELS,
                            value=PRIMARY_MODEL,
                            label="Select Gemini Model Engine",
                            elem_id="model-picker",
                            elem_classes=["model-picker-radios"]
                        )

                    status_output = gr.HTML(
                        """<div class="status-pill ready">⚡ Ready for Audit</div>"""
                    )

                    initial_dashboard_html = build_score_dashboard(
                        0,
                        {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0},
                        "Upload a resume and job description, then click 'RUN ATS AUDIT' to compute ATS match and benchmark analytics.",
                        ["Parse keyword density and hard skills", "Detect ATS formatting bottlenecks", "Generate tailored application assets"]
                    )
                    score_output = gr.HTML(initial_dashboard_html)

        with gr.Row(elem_classes=["actions-row"]):
            analyze_btn = gr.Button(
                "⚡ RUN ATS AUDIT",
                variant="primary",
                elem_id="analyze-btn",
                scale=0,
                min_width=250
            )
            clear_btn = gr.Button(
                "🔄 Reset All",
                variant="secondary",
                elem_id="clear-btn",
                scale=0,
                min_width=140
            )

        # ── BOTTOM SECTION: DETAILED DELIVERABLES TABS (STRUCTURED GLASS CARD) ──
        with gr.Row(elem_classes=["deliverables-row"]):
            with gr.Column(scale=12):
                with gr.Column(elem_classes=["glass-card", "deliverables-card"]):
                    gr.HTML("""
                    <div class="deliverables-header-block">
                        <div class="pill-heading-lg">
                            <span>📑</span>
                            <span>DETAILED ANALYSIS & DELIVERABLES</span>
                            <span class="pill-badge">COMPREHENSIVE AUDIT</span>
                        </div>
                        <div class="section-subtext">
                            Explore your ATS keyword gaps, tailored cover letter, interactive interview strategy, and high-impact bullet rewrites below.
                        </div>
                    </div>
                    """)
                    
                    with gr.Tabs(elem_classes=["deliverable-tabs"]):
                        with gr.Tab("🔍 ATS & Keyword Audit"):
                            ats_progress_output = gr.HTML("", elem_id="ats-progress-tracker-wrap")
                            ats_output = gr.Markdown(
                                "*Run an audit to view missing keywords, match rates, and critical ATS blockers.*",
                                elem_classes=["md-output"],
                                sanitize_html=False
                            )

                        with gr.Tab("✉️ Tailored Cover Letter"):
                            cover_letter_output = gr.Markdown(
                                "*Run an audit to generate an executive-grade tailored cover letter.*",
                                elem_classes=["md-output"],
                                sanitize_html=False
                            )

                        with gr.Tab("🎤 Interview Strategy"):
                            interview_output = gr.Markdown(
                                "*Run an audit to generate top interview questions and custom STAR guidelines.*",
                                elem_classes=["md-output"],
                                sanitize_html=False
                            )

                        with gr.Tab("🛠️ High-Impact Bullet Rewrites"):
                            bullet_output = gr.Markdown(
                                "*Run an audit to view transformed high-impact bullet rewrites with strong action verbs and quantified achievements.*",
                                elem_classes=["md-output"],
                                sanitize_html=False
                            )

                        with gr.Tab("💾 Export Audit Report"):
                            gr.HTML("""
                            <div class="export-helper-card" style="padding: 18px 22px; margin-top: 8px; margin-bottom: 20px; border-radius: 14px; background: var(--inner-bg); border: 1px solid var(--inner-border);">
                                <div style="font-size: 0.94rem; font-weight: 800; color: var(--text-primary); margin-bottom: 6px;">📥 1-Click Comprehensive Audit Export</div>
                                <div style="font-size: 0.86rem; color: var(--text-secondary); line-height: 1.6;">Download the complete ATS audit report, tailored cover letter, interview playbook, and bullet rewrites in clean plain text.</div>
                            </div>
                            """)
                            report_file_output = gr.File(
                                label="Download Comprehensive Report (.txt)",
                                elem_id="report-download"
                            )

        # ── API KEY PANEL EVENT WIRING ──
        api_key_toggle_btn.click(
            fn=lambda: gr.update(visible=True),
            inputs=[],
            outputs=[api_key_panel]
        )
        
        close_key_btn.click(
            fn=lambda: gr.update(visible=False),
            inputs=[],
            outputs=[api_key_panel]
        )

        def handle_save_key(key_val, persist):
            clean_k = (key_val or "").strip()
            if not clean_k:
                return (
                    """<div class="api-key-status-msg error">❌ API Key cannot be empty. Please enter your Gemini API key.</div>""",
                    "🔑 Configure API Key",
                    """<div class="status-pill error">⚠️ Error: Gemini API Key is missing</div>"""
                )
            
            is_valid, msg = validate_gemini_api_key(clean_k)
            if not is_valid:
                return (
                    f"""<div class="api-key-status-msg error">❌ {msg}</div>""",
                    "🔑 Invalid Key",
                    f"""<div class="status-pill error">⚠️ {msg}</div>"""
                )
            
            os.environ["GEMINI_API_KEY"] = clean_k
            saved_env = False
            if persist:
                saved_env = save_api_key_to_env(clean_k)
            
            masked = get_masked_api_key()
            persist_note = " (Saved to .env file)" if saved_env else " (Active for current session)"
            success_msg = f"""<div class="api-key-status-msg ready">✅ Key validated & connected successfully! Active: {masked}{persist_note}</div>"""
            btn_label = f"🟢 Key: {masked}"
            status_pill = f"""<div class="status-pill ready">⚡ Gemini Key Connected ({masked}) - Ready for Audit</div>"""
            return success_msg, btn_label, status_pill

        save_key_btn.click(
            fn=handle_save_key,
            inputs=[api_key_input, persist_key_check],
            outputs=[api_key_status_output, api_key_toggle_btn, status_output]
        )

        def handle_test_key(key_val):
            clean_k = (key_val or "").strip()
            if not clean_k:
                return """<div class="api-key-status-msg error">❌ Please enter an API key to test.</div>"""
            is_valid, msg = validate_gemini_api_key(clean_k)
            if is_valid:
                return f"""<div class="api-key-status-msg ready">✅ Connection Successful: {msg}</div>"""
            else:
                return f"""<div class="api-key-status-msg error">❌ Connection Failed: {msg}</div>"""

        test_key_btn.click(
            fn=handle_test_key,
            inputs=[api_key_input],
            outputs=[api_key_status_output]
        )

        def on_model_change(selected_model):
            model_dict = dict(FREE_TEXT_OUTPUT_MODELS)
            lbl = model_dict.get(selected_model, selected_model)
            return (
                gr.Accordion(label=f"⚙️ Engine & Model Selection ({lbl})"),
                f"""<div class="status-pill ready">⚡ Model Engine Selected: <strong>{lbl}</strong> (Ready for Audit)</div>"""
            )

        model_input.change(
            fn=on_model_change,
            inputs=[model_input],
            outputs=[model_accordion, status_output]
        )

        # ── EVENT WIRING ──
        def _analyze_handler(pdf, pasted, jd, company, depth_val, selected_model, progress=gr.Progress(track_tqdm=False)):
            # Dynamically grab the latest client or initialize from os.environ
            active_client = None
            if os.environ.get("GEMINI_API_KEY"):
                try:
                    active_client = init_gemini_client()
                except Exception as e:
                    logger.error("Could not init client: %s", e)

            yield from analyze_resume(
                pdf, pasted, jd, company, depth_val,
                client=active_client,
                model_id=selected_model,
                progress=progress
            )

        analyze_btn.click(
            fn=_analyze_handler,
            inputs=[pdf_input, pasted_resume_input, jd_input, company_input, depth_input, model_input],
            outputs=[status_output, score_output, ats_progress_output, ats_output, cover_letter_output, interview_output, bullet_output, report_file_output],
            show_progress="hidden"
        )

        def clear_all():
            initial_dash = build_score_dashboard(
                0, 
                {"keywords": 0, "experience": 0, "skills": 0, "formatting": 0},
                "Upload a resume and job description, then click 'RUN ATS AUDIT' to compute ATS match and benchmark analytics.",
                ["Parse keyword density and hard skills", "Detect ATS formatting bottlenecks", "Generate tailored application assets"]
            )
            return (
                None, "", "", "", "Deep Architectural Review", PRIMARY_MODEL,
                """<div class="status-pill ready">⚡ Ready for Audit</div>""",
                initial_dash,
                "",
                "*Run an audit to view missing keywords, match rates, and critical ATS blockers.*",
                "*Run an audit to generate an executive-grade tailored cover letter.*",
                "*Run an audit to generate top interview questions and custom STAR guidelines.*",
                "*Run an audit to view transformed high-impact bullet rewrites with strong action verbs and quantified achievements.*",
                None
            )

        clear_btn.click(
            fn=clear_all,
            inputs=[],
            outputs=[
                pdf_input, pasted_resume_input, jd_input, company_input, depth_input,
                model_input,
                status_output, score_output, ats_progress_output, ats_output, cover_letter_output, interview_output, bullet_output, report_file_output
            ]
        )

    return app
