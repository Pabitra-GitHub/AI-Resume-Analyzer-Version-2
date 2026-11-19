"""
Configuration, constants, theme CSS, and logging setup for AI Resume Analyzer.
"""
import os
import tempfile
import logging

# ── Logging Configuration ───────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("AIResumeAnalyzer")

# ── Model Identifiers ────────────────────────────
PRIMARY_MODEL = "gemini-3.5-flash"
FALLBACK_MODEL = "gemini-3.5-flash-lite"
FREE_TEXT_OUTPUT_MODELS = (
    ("Gemini 3.5 Flash (Balanced & Fast)", "gemini-3.5-flash"),
    ("Gemini 3.5 Flash Lite (Ultra-Fast 7s)", "gemini-3.5-flash-lite"),
    ("Gemini 3.7 Flash", "gemini-3.7-flash"),
    ("Gemini 3.8 Flash (High Accuracy)", "gemini-3.8-flash"),
    ("Gemini Flash Latest", "gemini-flash-latest"),
)
FREE_TEXT_OUTPUT_MODEL_IDS = frozenset(model_id for _, model_id in FREE_TEXT_OUTPUT_MODELS)

# ── Input & Processing Limits ────────────────────
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit
MAX_PDF_PAGES = 10                     # 10 page limit
MIN_EXTRACTED_CHARS = 50               # Minimum text threshold to detect scanned PDFs

MAX_RESUME_CHARS = 14000
MAX_JD_CHARS = 8000

# ── Mathematical Scoring Weights ─────────────────
WEIGHT_KEYWORDS = 0.40
WEIGHT_EXPERIENCE = 0.30
WEIGHT_SKILLS = 0.20
WEIGHT_FORMATTING = 0.10

# ── HTML Sanitization Allowlists ─────────────────
ALLOWED_HTML_TAGS = [
    "p", "span", "div", "h1", "h2", "h3", "h4", "h5", "h6",
    "strong", "em", "b", "i", "u", "ul", "ol", "li",
    "table", "thead", "tbody", "tr", "th", "td", "hr", "br",
    "code", "pre", "blockquote", "a", "details", "summary",
]

ALLOWED_CSS_CLASSES = {
    # Interview strategy accordion classes
    "interview-accordion", "accordion-body", "interview-tag",
    "tech", "behavioral", "gap", "leadership",
    "star-box", "star-line",
    # Bullet rewrites card classes
    "bullet-card", "bullet-before", "bullet-after", "bullet-rationale",
    # Badge and layout classes
    "status-pill", "ready", "running", "error", "pill-badge", "pill-heading",
    "truncation-warning-banner",
    "telemetry-pipeline-grid", "telemetry-pill-step", "telemetry-icon", "telemetry-text",
    "active", "processing", "pending", "check", "pulse",
}

# ── Report Export Configuration ──────────────────
REPORT_DIR = os.path.join(tempfile.gettempdir(), "ai_resume_analyzer_reports")
REPORT_MAX_AGE_SECONDS = 3600

# ── Custom CSS Theme ─────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* ===== ROOT & THEME VARIABLES (DYNAMIC THEME SYSTEM - PHASE 3 UNIFIED DESIGN SYSTEM) ===== */
:root, html, body {
    /* Phase 3 Unified Design System Surface Tokens */
    --bg-canvas: #070a12;
    --bg-card: rgba(17, 23, 41, 0.72);
    --bg-card-inner: rgba(11, 15, 28, 0.85);
    --border-subtle: rgba(255, 255, 255, 0.07);
    --border-focus: rgba(99, 102, 241, 0.55);
    --accent-primary: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted: #64748b;
    --brand-title-color: #ffffff;
    --brand-title-shadow: 0 0 20px rgba(129, 140, 248, 0.65), 0 0 35px rgba(99, 102, 241, 0.40);

    --bg-page: var(--bg-canvas);
    --bg-gradient: radial-gradient(ellipse at 35% 0%, #16143c 0%, #0a0c18 50%, #070a12 100%);
    
    /* Main container background: Deep dark slate / glassmorphic container */
    --bg-primary: var(--bg-card);
    --panel-bg: var(--bg-card);
    --panel-border: var(--border-subtle);
    --panel-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
    
    --inner-bg: var(--bg-card-inner);
    --inner-border: var(--border-subtle);
    --border-color: var(--border-subtle);
    
    --pill-heading-bg: rgba(255, 255, 255, 0.05);
    --pill-heading-border: rgba(255, 255, 255, 0.12);
    --pill-heading-color: var(--text-primary);
    --pill-heading-glow: 0 4px 14px rgba(99, 102, 241, 0.22);
    
    /* Inactive Tabs: Dark translucent pills with light gray text */
    --tab-inactive-bg: rgba(255, 255, 255, 0.06);
    --tab-inactive-border: rgba(255, 255, 255, 0.10);
    --tab-inactive-text: #cbd5e1;
    --tab-inactive-hover-bg: rgba(99, 102, 241, 0.22);
    --tab-inactive-hover-border: #818cf8;
    --tab-inactive-hover-text: #ffffff;
    
    /* Active Tabs: Vibrant purple/indigo gradient with crisp white text */
    --tab-active-bg: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    --tab-active-border: #a5b4fc;
    --tab-active-text: #ffffff;
    --tab-active-shadow: 0 4px 18px rgba(99, 102, 241, 0.5);
    
    --input-bg: var(--bg-card-inner);
    --input-border: var(--border-subtle);
    --input-text: #f8fafc;
    --input-placeholder: #64748b;
    
    --badge-bg: rgba(99, 102, 241, 0.18);
    --badge-border: rgba(129, 140, 248, 0.35);
    --badge-color: #ffffff;
    
    --bar-bg: rgba(255, 255, 255, 0.07);
    --verdict-bg: rgba(99, 102, 241, 0.08);
    --verdict-border: rgba(99, 102, 241, 0.20);
    --gauge-track: rgba(255, 255, 255, 0.07);

    --status-ready-bg: rgba(16, 185, 129, 0.15);
    --status-ready-border: rgba(16, 185, 129, 0.4);
    --status-ready-text: #34d399;
    --status-running-bg: rgba(99, 102, 241, 0.18);
    --status-running-border: rgba(129, 140, 248, 0.45);
    --status-running-text: #c7d2fe;
    --status-error-bg: rgba(239, 68, 68, 0.15);
    --status-error-border: rgba(239, 68, 68, 0.4);
    --status-error-text: #f87171;

    /* Gradio native variable overrides for Dark Mode */
    --background-fill-primary: var(--bg-card) !important;
    --background-fill-secondary: var(--bg-card-inner) !important;
    --block-background-fill: var(--bg-card) !important;
    --input-background-fill: var(--bg-card-inner) !important;
    --border-color-primary: var(--border-subtle) !important;
    --body-text-color: var(--text-primary) !important;
    --body-text-color-subdued: var(--text-secondary) !important;
    --block-label-text-color: #cbd5e1 !important;
    --block-title-text-color: var(--text-primary) !important;
}

:root.light-mode, html.light-mode, body.light-mode {
    --bg-canvas: #f8fafc;
    --bg-card: rgba(255, 255, 255, 0.85);
    --bg-card-inner: rgba(241, 245, 249, 0.85);
    --border-subtle: rgba(99, 102, 241, 0.16);
    --border-focus: rgba(99, 102, 241, 0.60);
    --accent-primary: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #0284c7 100%);
    --text-primary: #0f172a;
    --text-secondary: #475569;
    --text-muted: #64748b;
    --brand-title-color: #1e1b4b;
    --brand-title-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
    
    --bg-page: var(--bg-canvas);
    --bg-gradient: linear-gradient(135deg, #f8fafc 0%, #eef2f6 50%, #f1f5f9 100%);
    
    /* Main container background: Soft off-white / semi-transparent frosted glass */
    --bg-primary: var(--bg-card);
    --panel-bg: var(--bg-card);
    --panel-border: var(--border-subtle);
    --panel-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
    
    --inner-bg: var(--bg-card-inner);
    --inner-border: var(--border-subtle);
    --border-color: var(--border-subtle);
    
    --pill-heading-bg: #f1f5f9;
    --pill-heading-border: #cbd5e1;
    --pill-heading-color: #1e293b;
    --pill-heading-glow: 0 2px 10px rgba(99, 102, 241, 0.12);
    
    /* Inactive Tabs: Soft gray with clear dark text (#334155) */
    --tab-inactive-bg: #f1f5f9;
    --tab-inactive-border: #cbd5e1;
    --tab-inactive-text: #334155;
    --tab-inactive-hover-bg: #e0e7ff;
    --tab-inactive-hover-border: #6366f1;
    --tab-inactive-hover-text: #1e1b4b;
    
    /* Active Tabs: Vibrant purple/indigo gradient with crisp white text */
    --tab-active-bg: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    --tab-active-border: #3730a3;
    --tab-active-text: #ffffff;
    --tab-active-shadow: 0 4px 16px rgba(79, 70, 229, 0.35);
    
    --input-bg: #ffffff;
    --input-border: #cbd5e1;
    --input-text: #1e293b;
    --input-placeholder: #64748b;
    
    --badge-bg: rgba(99, 102, 241, 0.12);
    --badge-border: rgba(99, 102, 241, 0.30);
    --badge-color: #4338ca;
    
    --bar-bg: rgba(0, 0, 0, 0.08);
    --verdict-bg: rgba(99, 102, 241, 0.06);
    --verdict-border: rgba(99, 102, 241, 0.24);
    --gauge-track: rgba(0, 0, 0, 0.08);

    --status-ready-bg: rgba(16, 185, 129, 0.12);
    --status-ready-border: rgba(16, 185, 129, 0.5);
    --status-ready-text: #065f46;
    --status-running-bg: rgba(99, 102, 241, 0.1);
    --status-running-border: rgba(99, 102, 241, 0.4);
    --status-running-text: #3730a3;
    --status-error-bg: rgba(239, 68, 68, 0.12);
    --status-error-border: rgba(239, 68, 68, 0.5);
    --status-error-text: #991b1b;

    /* Gradio native variable overrides for Light Mode */
    --background-fill-primary: var(--bg-card) !important;
    --background-fill-secondary: var(--bg-card-inner) !important;
    --block-background-fill: var(--bg-card) !important;
    --input-background-fill: #ffffff !important;
    --border-color-primary: var(--border-subtle) !important;
    --body-text-color: var(--text-primary) !important;
    --body-text-color-subdued: var(--text-secondary) !important;
    --block-label-text-color: #1e293b !important;
    --block-title-text-color: #1e293b !important;
}

/* ===== FULL WIDTH FLUID LAYOUT ===== */
html, body {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
    overflow-x: hidden !important;
}

body, .gradio-container {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background: var(--bg-gradient) !important;
    min-height: 100vh;
    color: var(--text-primary) !important;
    transition: background 0.3s cubic-bezier(0.16, 1, 0.3, 1), color 0.3s ease !important;
}

.gradio-container, gradio-app {
    max-width: 100% !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 14px 28px !important;
    box-sizing: border-box !important;
}

.gradio-container > .main, .gradio-container > div {
    max-width: 100% !important;
    width: 100% !important;
}

/* ===== HARDWARE-ACCELERATED COMPOSITED ANIMATIONS ===== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes pulseGlow {
    0%, 100% {
        opacity: 1;
        transform: scale(1);
    }
    50% {
        opacity: 0.35;
        transform: scale(0.85);
    }
}

@keyframes sweepGauge {
    from {
        stroke-dashoffset: 440;
    }
    to {
        stroke-dashoffset: var(--target-offset, 0);
    }
}

@keyframes sweepBar {
    from {
        width: 0%;
    }
    to {
        width: var(--target-width, 100%);
    }
}

@keyframes softShimmer {
    0%, 100% {
        opacity: 0.9;
        transform: scale(1);
    }
    50% {
        opacity: 1;
        transform: scale(1.02);
    }
}

@keyframes radarSpin {
    from {
        transform: rotate(0deg);
    }
    to {
        transform: rotate(360deg);
    }
}

@keyframes shimmerScan {
    0% {
        background-position: -200% 0;
    }
    100% {
        background-position: 200% 0;
    }
}

/* ===== STRUCTURED GLASS CARDS ===== */
.glass-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 20px !important;
    padding: 20px 24px !important;
    margin-bottom: 16px !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: var(--panel-shadow) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease !important;
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    transform: translateZ(0);
}

.glass-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), 0 0 20px rgba(99, 102, 241, 0.15) !important;
}

/* Balanced input step cards */
.input-step-card {
    padding: 16px 20px !important;
    margin-bottom: 14px !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease !important;
}

.input-step-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45) !important;
}

.input-step-card .section-header-block {
    margin-bottom: 8px !important;
}

.input-step-card .section-subtext {
    margin: 4px 0 10px 4px !important;
}

.resume-input-options {
    gap: 12px !important;
    align-items: stretch !important;
}

.resume-input-options > .form {
    min-width: 0 !important;
}

.compact-pdf-upload button.upload-button {
    min-height: 105px !important;
    padding: 14px 12px !important;
}

.input-step-card textarea {
    min-height: 105px !important;
}

.input-step-card .wrap,
.input-step-card .form {
    margin-bottom: 0 !important;
}

/* Header Bar */
.header-row {
    position: relative !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 24px 32px !important;
    margin-top: 1rem !important;
    margin-bottom: 2rem !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 20px !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: var(--panel-shadow) !important;
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    overflow: hidden !important;
}

.header-row::before {
    content: "" !important;
    position: absolute !important;
    top: -50% !important;
    left: -20% !important;
    width: 60% !important;
    height: 200% !important;
    background: radial-gradient(circle, rgba(124, 58, 237, 0.2) 0%, rgba(79, 70, 229, 0.08) 50%, transparent 70%) !important;
    pointer-events: none !important;
    filter: blur(35px) !important;
    z-index: 0 !important;
}

.header-brand-container {
    position: relative !important;
    z-index: 1 !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 12px !important;
    text-align: left !important;
}

.brand-title {
    font-size: 1.85rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    word-spacing: 0.35em !important;
    line-height: 1.25 !important;
    margin: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 12px !important;
    flex-wrap: wrap !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: var(--brand-title-color, #ffffff) !important;
}

:root.light-mode .brand-title,
html.light-mode .brand-title,
body.light-mode .brand-title,
.light-mode .brand-title {
    color: #1e1b4b !important;
}

/* ── RESUME INTELLIGENCE Brand Text: 100% Solid, High-Contrast Visibility in Both Modes ── */
.brand-text {
    display: inline-block !important;
    vertical-align: middle !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    word-spacing: 0.35em !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: none !important;
    background-image: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    filter: none !important;
    /* Default Dark Mode: Crisp White with Neon Violet Ambient Glow */
    color: var(--brand-title-color, #ffffff) !important;
    -webkit-text-fill-color: var(--brand-title-color, #ffffff) !important;
    text-shadow: var(--brand-title-shadow, 0 0 20px rgba(129, 140, 248, 0.65)) !important;
}

/* Explicit Dark Mode Overrides (Default / Non-Light) */
:root:not(.light-mode) .brand-text,
html:not(.light-mode) .brand-text,
body:not(.light-mode) .brand-text,
.dark .brand-text,
body.dark .brand-text,
html.dark .brand-text,
:root.dark .brand-text,
.gradio-container:not(.light-mode) .brand-text {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    text-shadow: 0 0 20px rgba(129, 140, 248, 0.65), 0 0 35px rgba(99, 102, 241, 0.40) !important;
    background: none !important;
    background-image: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    filter: none !important;
    opacity: 1 !important;
    visibility: visible !important;
}

.brand-ai-chip {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 12px !important;
    height: 28px !important;
    font-size: 0.88rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.12em !important;
    border-radius: 8px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 0 16px rgba(124, 58, 237, 0.45) !important;
    border: 1px solid rgba(167, 139, 250, 0.4) !important;
    box-sizing: border-box !important;
    vertical-align: middle !important;
    margin: 0 !important;
}

/* Explicit Light Mode Overrides: Deep Royal Navy Indigo (#1e1b4b) for Crystal-Clear Legibility */
:root.light-mode .brand-text,
html.light-mode .brand-text,
body.light-mode .brand-text,
.light-mode .brand-text,
.light-mode h1 .brand-text,
.light-mode .brand-title .brand-text,
.gradio-container.light-mode .brand-text,
body.light-mode h1.brand-title .brand-text,
html.light-mode h1.brand-title .brand-text {
    color: #1e1b4b !important;
    -webkit-text-fill-color: #1e1b4b !important;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.12) !important;
    background: none !important;
    background-image: none !important;
    -webkit-background-clip: initial !important;
    background-clip: initial !important;
    filter: none !important;
    opacity: 1 !important;
    visibility: visible !important;
}

:root.light-mode .header-row::before,
html.light-mode .header-row::before,
body.light-mode .header-row::before {
    background: radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, rgba(6, 182, 212, 0.08) 50%, transparent 70%) !important;
}

.pill-badge-powered {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    padding: 0 14px !important;
    height: 28px !important;
    border-radius: 9999px !important;
    background: var(--badge-bg) !important;
    border: 1px solid var(--badge-border) !important;
    color: var(--badge-color) !important;
    font-size: 0.78rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.03em !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    animation: softShimmer 4s infinite ease-in-out;
    width: fit-content !important;
    box-sizing: border-box !important;
    vertical-align: middle !important;
    margin: 0 !important;
}

.pulse-dot {
    width: 8px !important;
    height: 8px !important;
    border-radius: 50% !important;
    background: #10b981 !important;
    animation: pulseGlow 2s infinite !important;
}

.header-controls-col {
    display: flex !important;
    justify-content: flex-end !important;
    align-items: center !important;
}

.header-actions-group {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: flex-end !important;
    gap: 12px !important;
    width: 100% !important;
    flex-wrap: nowrap !important;
}

#api-key-toggle-btn {
    border-radius: 12px !important;
    padding: 0 20px !important;
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--pill-heading-border) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.03em !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    cursor: pointer !important;
    box-shadow: var(--pill-heading-glow) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    min-height: 44px !important;
    height: 44px !important;
    min-width: 220px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
    overflow: visible !important;
    box-sizing: border-box !important;
    flex-shrink: 0 !important;
}

#theme-toggle-btn {
    border-radius: 12px !important;
    padding: 0 16px !important;
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--pill-heading-border) !important;
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.02em !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    cursor: pointer !important;
    box-shadow: var(--pill-heading-glow) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    min-height: 44px !important;
    height: 44px !important;
    min-width: 120px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    white-space: nowrap !important;
    overflow: visible !important;
    box-sizing: border-box !important;
    flex-shrink: 0 !important;
}

#api-key-toggle-btn:hover, #theme-toggle-btn:hover {
    border-color: #818cf8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
}

#api-key-toggle-btn:active, #theme-toggle-btn:active {
    transform: translateY(0) scale(0.98) !important;
}

.api-key-inputs-row {
    display: flex !important;
    gap: 12px !important;
    align-items: flex-end !important;
    margin-bottom: 8px !important;
}

#api-key-field {
    min-width: 320px !important;
}

#api-key-field input {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.90rem !important;
    letter-spacing: 0.03em !important;
    padding: 10px 14px !important;
    box-sizing: border-box !important;
}

/* ===== API KEY SETTINGS MODAL / PANEL ===== */
.api-key-settings-card {
    margin: -10px 0 20px 0 !important;
    padding: 22px 26px !important;
    border-radius: 18px !important;
    background: var(--bg-card) !important;
    border: 1px solid rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.4), 0 0 24px rgba(99, 102, 241, 0.15) !important;
    position: relative !important;
    z-index: 10 !important;
    animation: slideUpFade 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.api-key-card-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    margin-bottom: 14px !important;
}

#close-key-btn {
    border-radius: 8px !important;
    background: transparent !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--text-muted) !important;
    padding: 6px 14px !important;
    font-size: 0.82rem !important;
    cursor: pointer !important;
    transition: all 0.2s ease !important;
}

#close-key-btn:hover {
    color: var(--text-primary) !important;
    border-color: var(--border-focus) !important;
    background: var(--tab-inactive-bg) !important;
}

.api-key-status-msg {
    margin-top: 10px !important;
    padding: 10px 14px !important;
    border-radius: 10px !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.api-key-status-msg.ready {
    background: rgba(16, 185, 129, 0.12) !important;
    border: 1px solid rgba(16, 185, 129, 0.35) !important;
    color: #34d399 !important;
}

.api-key-status-msg.warning {
    background: rgba(245, 158, 11, 0.12) !important;
    border: 1px solid rgba(245, 158, 11, 0.35) !important;
    color: #fbbf24 !important;
}

.api-key-status-msg.error {
    background: rgba(239, 68, 68, 0.12) !important;
    border: 1px solid rgba(239, 68, 68, 0.35) !important;
    color: #f87171 !important;
}

.api-key-footer-links {
    margin-top: 10px !important;
    font-size: 0.84rem !important;
    color: var(--text-muted) !important;
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.api-key-link {
    color: #818cf8 !important;
    text-decoration: underline !important;
    font-weight: 600 !important;
}

.api-key-link:hover {
    color: #c7d2fe !important;
}

/* ===== ATS AUDIT PROGRESS LINE & VFX TRACKER ===== */
.ats-progress-line-container {
    padding: 20px 24px !important;
    margin-bottom: 24px !important;
    border-radius: 16px !important;
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25) !important;
}

.ats-progress-line-container.in-progress {
    border-color: rgba(99, 102, 241, 0.45) !important;
}

.ats-progress-line-container.completed {
    border-color: rgba(16, 185, 129, 0.45) !important;
}

.progress-line-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 14px !important;
}

.progress-title-wrap {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}

.progress-pulse-dot {
    width: 9px !important;
    height: 9px !important;
    border-radius: 50% !important;
    background: #6366f1 !important;
    box-shadow: 0 0 10px #6366f1 !important;
    animation: pulseGlow 1.8s infinite ease-in-out !important;
}

.ats-progress-line-container.completed .progress-pulse-dot {
    background: #10b981 !important;
    box-shadow: 0 0 10px #10b981 !important;
}

.progress-title {
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    color: var(--text-primary) !important;
    text-transform: uppercase !important;
}

.progress-percent-badge {
    padding: 3px 10px !important;
    border-radius: 9999px !important;
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    background: rgba(99, 102, 241, 0.15) !important;
    border: 1px solid rgba(129, 140, 248, 0.35) !important;
    color: #c7d2fe !important;
}

.ats-progress-line-container.completed .progress-percent-badge {
    background: rgba(16, 185, 129, 0.15) !important;
    border-color: rgba(16, 185, 129, 0.35) !important;
    color: #34d399 !important;
}

.progress-bar-track {
    width: 100% !important;
    height: 8px !important;
    border-radius: 9999px !important;
    background: var(--gauge-track) !important;
    overflow: hidden !important;
    position: relative !important;
    margin-bottom: 18px !important;
    border: 1px solid var(--border-subtle) !important;
}

.progress-bar-fill {
    height: 100% !important;
    border-radius: 9999px !important;
    background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 50%, #06b6d4 100%) !important;
    position: relative !important;
    box-shadow: 0 0 12px rgba(99, 102, 241, 0.6) !important;
    transition: width 0.12s linear !important;
}

.ats-progress-line-container.completed .progress-bar-fill {
    background: linear-gradient(90deg, #10b981 0%, #34d399 50%, #06b6d4 100%) !important;
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.6) !important;
    transition: width 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.progress-laser-glow {
    position: absolute !important;
    top: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 40px !important;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.8), transparent) !important;
    animation: laserScan 2s infinite linear !important;
}

@keyframes laserScan {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.progress-milestones-grid {
    display: grid !important;
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 12px !important;
    margin-bottom: 14px !important;
}

.progress-milestone {
    padding: 10px 12px !important;
    border-radius: 12px !important;
    background: var(--tab-inactive-bg) !important;
    border: 1px solid var(--border-subtle) !important;
    transition: all 0.25s ease !important;
}

.progress-milestone.done {
    background: rgba(16, 185, 129, 0.08) !important;
    border-color: rgba(16, 185, 129, 0.3) !important;
}

.progress-milestone.active {
    background: rgba(99, 102, 241, 0.12) !important;
    border-color: rgba(129, 140, 248, 0.45) !important;
    box-shadow: 0 0 14px rgba(99, 102, 241, 0.25) !important;
}

.progress-milestone.pending {
    opacity: 0.6 !important;
}

.milestone-top {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 4px !important;
}

.milestone-num {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    color: var(--text-muted) !important;
    letter-spacing: 0.05em !important;
}

.milestone-badge {
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 2px 6px !important;
    border-radius: 6px !important;
}

.progress-milestone.done .milestone-badge {
    background: rgba(16, 185, 129, 0.2) !important;
    color: #34d399 !important;
}

.progress-milestone.active .milestone-badge {
    background: rgba(99, 102, 241, 0.25) !important;
    color: #c7d2fe !important;
    animation: pulseGlow 1.8s infinite !important;
}

.progress-milestone.pending .milestone-badge {
    background: var(--inner-border) !important;
    color: var(--text-muted) !important;
}

.milestone-label {
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    margin-bottom: 2px !important;
}

.milestone-desc {
    font-size: 0.72rem !important;
    color: var(--text-secondary) !important;
    line-height: 1.35 !important;
}

.progress-status-footer {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 0.8rem !important;
    color: var(--text-secondary) !important;
    padding-top: 10px !important;
    border-top: 1px dashed var(--border-subtle) !important;
}

.status-footer-text {
    font-weight: 500 !important;
}

/* ===== WORKSPACE GRID & BALANCED 2-COLUMN LAYOUT ===== */
.main-workspace-row {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    align-items: stretch !important;
    gap: 22px !important;
    margin-bottom: 16px !important;
    width: 100% !important;
}

.main-workspace-row > .gradio-column,
.main-workspace-row > div {
    min-width: 0 !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    flex-direction: column !important;
}

.workspace-col {
    display: flex !important;
    flex-direction: column !important;
    align-self: stretch !important;
    height: 100% !important;
}

.inputs-col {
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    height: 100% !important;
    gap: 14px !important;
}

.inputs-col .input-step-card {
    margin-bottom: 0 !important;
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
}

.insights-outer-col {
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
}

.actions-row {
    width: 100% !important;
    margin: 16px 0 24px !important;
    gap: 16px !important;
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    flex-wrap: nowrap !important;
}

.actions-row button {
    min-height: 48px !important;
    white-space: nowrap !important;
    word-break: keep-all !important;
    text-wrap: nowrap !important;
    flex-shrink: 0 !important;
}

.model-picker-radios {
    width: 100% !important;
    margin: 6px 0 10px !important;
    padding: 0 !important;
}

#model-picker .wrap {
    display: grid !important;
    grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
    gap: 8px !important;
    width: 100% !important;
    background: transparent !important;
}

#model-picker label {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-width: 0 !important;
    min-height: 40px !important;
    margin: 0 !important;
    padding: 7px 8px !important;
    border: 1px solid var(--tab-inactive-border) !important;
    border-radius: 10px !important;
    background: var(--tab-inactive-bg) !important;
    color: var(--text-secondary) !important;
    text-align: center !important;
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
    overflow-wrap: anywhere !important;
    cursor: pointer !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, background 0.18s ease, border-color 0.18s ease, color 0.18s ease !important;
}

#model-picker label:has(input:checked),
#model-picker label.selected {
    border-color: var(--tab-active-border) !important;
    background: var(--tab-active-bg) !important;
    color: var(--tab-active-text) !important;
    box-shadow: var(--tab-active-shadow) !important;
}

#model-picker label:hover {
    border-color: #818cf8 !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25) !important;
}

#model-picker label:active {
    transform: scale(0.98) !important;
}

#model-picker input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 1px !important;
    height: 1px !important;
    pointer-events: none !important;
}

.deliverables-card {
    margin-bottom: 24px !important;
}

/* ===== PROMINENT HEADERS & BULLETPROOF HIGH-CONTRAST PILL BADGES ===== */
.section-header-block {
    margin-bottom: 14px !important;
}

.pill-heading-lg {
    display: inline-flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 20px !important;
    border-radius: 9999px !important;
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--pill-heading-border) !important;
    color: var(--pill-heading-color) !important;
    font-size: 0.88rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: var(--pill-heading-glow) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.pill-heading-lg:hover {
    border-color: #818cf8 !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.35) !important;
}

.pill-badge {
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    padding: 4px 12px !important;
    border-radius: 9999px !important;
    background: var(--badge-bg) !important;
    color: var(--badge-color) !important;
    border: 1px solid var(--badge-border) !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.25) !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
}

.section-subtext {
    font-size: 0.86rem !important;
    color: var(--text-muted) !important;
    margin: 6px 0 14px 4px !important;
    line-height: 1.5 !important;
}

.pill-heading {
    display: inline-flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 7px 18px !important;
    border-radius: 9999px !important;
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--pill-heading-border) !important;
    color: var(--pill-heading-color) !important;
    font-size: 0.84rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: var(--pill-heading-glow) !important;
    margin-bottom: 12px !important;
    transition: all 0.25s ease !important;
}

.pill-heading:hover {
    border-color: #818cf8 !important;
    transform: translateY(-1px) !important;
}

/* ===== UPLOAD & EXPORT COMPONENTS (DYNAMIC THEME SYSTEM) ===== */
.gradio-file,
.gradio-file > div,
.gradio-file .wrap,
.gradio-file .file-preview,
.gradio-file .file-preview *,
.gradio-file .file,
.gradio-file .file *,
.gradio-file .file-item,
.gradio-file .file-item *,
.gradio-file .file-parts,
.gradio-file .file-parts *,
.gradio-file [data-testid="file-upload"],
.gradio-file [data-testid="file-upload"] *,
.gradio-file table,
.gradio-file tr,
.gradio-file td,
.gradio-file .drop-zone,
#report-download,
#report-download * {
    background: var(--panel-bg) !important;
    background-color: var(--panel-bg) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

button.upload-button {
    background: var(--pill-heading-bg) !important;
    border: 1.5px dashed var(--border-color) !important;
    border-radius: 14px !important;
    color: var(--text-secondary) !important;
    padding: 24px 16px !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease, border-color 0.25s ease, background 0.25s ease !important;
}

button.upload-button:hover {
    background: var(--tab-inactive-hover-bg) !important;
    border-color: rgba(99, 102, 241, 0.55) !important;
    color: var(--text-primary) !important;
    transform: scale(1.01) translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.30), inset 0 0 15px rgba(99, 102, 241, 0.12) !important;
}

button.upload-button:active,
.compact-pdf-upload:active button.upload-button {
    transform: scale(0.99) !important;
}

.gradio-file .file-name,
.gradio-file .file-size,
#report-download .file-name,
#report-download .file-size {
    color: var(--text-secondary) !important;
}

#report-download a,
#report-download button {
    background: var(--tab-inactive-bg) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    border-radius: 9999px !important;
    padding: 8px 20px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}

#report-download a:hover,
#report-download button:hover {
    background: var(--tab-inactive-hover-bg) !important;
    border-color: #818cf8 !important;
    color: var(--text-primary) !important;
    transform: translateY(-1px) !important;
}

#report-download a:active,
#report-download button:active {
    transform: scale(0.98) !important;
}

/* ===== TEXTBOX & TEXTAREA ===== */
.gradio-textbox,
.gradio-textbox > div,
.gradio-textbox .wrap,
.block.gradio-textbox,
label.block,
div[data-testid="textbox"] {
    background: var(--panel-bg) !important;
    border-color: var(--border-color) !important;
    color: var(--text-primary) !important;
}

textarea,
input[type="text"] {
    background: var(--bg-card-inner) !important;
    border: 1px solid var(--border-subtle) !important;
    color: var(--input-text) !important;
    border-radius: 12px !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s cubic-bezier(0.16, 1, 0.3, 1), background 0.25s ease !important;
}

textarea::placeholder,
input::placeholder {
    color: var(--input-placeholder) !important;
}

textarea:focus,
input[type="text"]:focus {
    border-color: var(--border-focus) !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25), 0 4px 16px rgba(99, 102, 241, 0.15) !important;
    outline: none !important;
}

/* ===== AUDIT DEPTH BALANCED PILL GROUP & STEP 3 CLEANUP ===== */
.step3-card {
    padding: 24px !important;
}

.step3-card .form,
.step3-card .block,
.step3-card [data-testid="textbox"],
.step3-card .wrap:not(.step3-depth-radio .wrap) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
}

.step3-depth-radio > span,
.step3-depth-radio .block-title,
.step3-depth-radio > label,
.step3-depth-radio span.svelte-10km448 {
    margin-top: 16px !important;
    margin-bottom: 8px !important;
    display: block !important;
    font-weight: 700 !important;
    font-size: 0.86rem !important;
    color: var(--text-secondary) !important;
}

.pill-radio-group,
.block.gradio-radio,
.gradio-radio {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    width: 100% !important;
}

.pill-radio-group .wrap,
.step3-depth-radio .wrap,
.pill-radio-group > div,
.block.gradio-radio .wrap {
    display: grid !important;
    grid-template-columns: repeat(3, 1fr) !important;
    gap: 10px !important;
    background: transparent !important;
    border: none !important;
    width: 100% !important;
}

.pill-radio-group label,
.step3-depth-radio label,
.block.gradio-radio label {
    width: 100% !important;
    min-width: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 10px 6px !important;
    border-radius: 9999px !important;
    background: var(--tab-inactive-bg) !important;
    border: 1px solid var(--tab-inactive-border) !important;
    color: var(--text-secondary) !important;
    font-size: 0.83rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.01em !important;
    white-space: nowrap !important;
    cursor: pointer !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, color 0.25s ease !important;
    margin: 0 !important;
    text-align: center !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    box-sizing: border-box !important;
}

.pill-radio-group input[type="radio"],
.step3-depth-radio input[type="radio"],
.block.gradio-radio input[type="radio"] {
    position: absolute !important;
    opacity: 0 !important;
    width: 0 !important;
    height: 0 !important;
    pointer-events: none !important;
}

.pill-radio-group label:has(input:checked),
.step3-depth-radio label:has(input:checked),
.block.gradio-radio label:has(input:checked),
.pill-radio-group label.selected,
.step3-depth-radio label.selected,
.block.gradio-radio label.selected {
    background: var(--tab-active-bg) !important;
    color: var(--tab-active-text) !important;
    border-color: var(--tab-active-border) !important;
    box-shadow: var(--tab-active-shadow) !important;
    transform: translateY(-2px) !important;
}

.pill-radio-group label:hover,
.step3-depth-radio label:hover,
.block.gradio-radio label:hover {
    border-color: #818cf8 !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25) !important;
}

.pill-radio-group label:active,
.step3-depth-radio label:active,
.block.gradio-radio label:active {
    transform: scale(0.98) !important;
}

/* Collapsible Model Selection Accordion */
.model-accordion {
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    border-radius: 14px !important;
    margin: 4px 0 12px 0 !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.model-accordion:hover {
    border-color: rgba(129, 140, 248, 0.45) !important;
}

.model-accordion > .label-wrap {
    padding: 10px 14px !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    color: var(--text-secondary) !important;
    cursor: pointer !important;
}

.model-accordion > .label-wrap:hover {
    color: var(--text-primary) !important;
}

/* ===== DELIVERABLES TABS & NAVIGATION (CLEAN PILLS, NO DUPLICATE MEASUREMENT LABELS) ===== */
/* Strictly neutralize Gradio 6 internal measurement containers and hidden dropdowns */
.visually-hidden,
[class*="visually-hidden"],
.tabs .visually-hidden,
.deliverable-tabs .visually-hidden,
.overflow-dropdown.hide,
.overflow-menu.hide {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    clip: rect(0, 0, 0, 0) !important;
    width: 0 !important;
    height: 0 !important;
    max-width: 0 !important;
    max-height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    position: absolute !important;
    pointer-events: none !important;
    user-select: none !important;
    -webkit-user-select: none !important;
}

.tabs,
.deliverable-tabs {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    width: 100% !important;
}

.tab-nav::before,
.tab-nav::after,
.tabs::before,
.tabs::after,
.tab-container::after {
    display: none !important;
    content: none !important;
    border: none !important;
    width: 0 !important;
    height: 0 !important;
}

.deliverable-tabs .tab-wrapper,
.deliverable-tabs .tab-container,
.deliverable-tabs .tab-nav,
div.tab-nav {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 10px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    overflow: visible !important;
    padding: 4px 0 16px 0 !important;
    margin: 0 0 10px 0 !important;
    align-items: center !important;
    width: 100% !important;
}

/* Standalone Pill Tab Buttons: High Contrast, Vibrant Active State */
.deliverable-tabs .tab-container > button[role="tab"],
.deliverable-tabs .tab-nav > button,
.deliverable-tabs button[role="tab"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    border-radius: 9999px !important;
    padding: 10px 20px !important;
    font-weight: 700 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.02em !important;
    background: var(--tab-inactive-bg) !important;
    border: 1.5px solid var(--tab-inactive-border) !important;
    color: var(--tab-inactive-text) !important;
    backdrop-filter: blur(14px) !important;
    -webkit-backdrop-filter: blur(14px) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    margin: 2px !important;
    height: auto !important;
    line-height: 1.4 !important;
    user-select: none !important;
}

.deliverable-tabs .tab-container > button[role="tab"]:hover,
.deliverable-tabs .tab-nav > button:hover,
.deliverable-tabs button[role="tab"]:hover {
    background: var(--tab-inactive-hover-bg) !important;
    border-color: var(--tab-inactive-hover-border) !important;
    color: var(--tab-inactive-hover-text) !important;
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.25) !important;
}

.deliverable-tabs .tab-container > button[role="tab"]:active,
.deliverable-tabs .tab-nav > button:active,
.deliverable-tabs button[role="tab"]:active {
    transform: scale(0.98) !important;
}

.deliverable-tabs .tab-container > button[role="tab"].selected,
.deliverable-tabs .tab-container > button[role="tab"][aria-selected="true"],
.deliverable-tabs .tab-nav > button.selected,
.deliverable-tabs .tab-nav > button[aria-selected="true"],
.deliverable-tabs button[role="tab"].selected,
.deliverable-tabs button[role="tab"][aria-selected="true"] {
    background: var(--tab-active-bg) !important;
    color: var(--tab-active-text) !important;
    border: 1.5px solid var(--tab-active-border) !important;
    box-shadow: var(--tab-active-shadow) !important;
    transform: translateY(-1px) !important;
    font-weight: 800 !important;
}

/* Deliverables Header Block Alignment */
.deliverables-header-block {
    margin-bottom: 20px !important;
    text-align: left !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    width: 100% !important;
}

.deliverables-header-block .pill-heading-lg {
    margin-bottom: 10px !important;
}

.deliverables-header-block .section-subtext {
    margin: 0 0 16px 2px !important;
    font-size: 0.90rem !important;
    color: var(--text-muted) !important;
    line-height: 1.6 !important;
}

/* Tab Panel & Content Spacing with Smooth Keyframe Entrance */
@keyframes slideUpFade {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.deliverable-tabs .tabitem,
.tabitem,
.deliverable-tabs div[role="tabpanel"],
div[role="tabpanel"] {
    padding: 16px 4px 12px 4px !important;
    margin-top: 6px !important;
    margin-bottom: 12px !important;
    border: none !important;
    background: transparent !important;
    animation: slideUpFade 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    transform: translateZ(0);
}

/* ===== INTERACTIVE INTERVIEW ACCORDION & CARDS ===== */
.interview-accordion {
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    border-radius: 14px !important;
    margin: 16px 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
}

.interview-accordion:hover {
    border-color: rgba(129, 140, 248, 0.45) !important;
    box-shadow: 0 6px 22px rgba(99, 102, 241, 0.2) !important;
}

.interview-accordion[open] {
    border-color: #6366f1 !important;
    box-shadow: 0 8px 28px rgba(99, 102, 241, 0.3) !important;
}

.interview-accordion summary {
    padding: 16px 22px !important;
    font-weight: 700 !important;
    font-size: 0.98rem !important;
    color: var(--text-primary) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    user-select: none !important;
    background: rgba(255, 255, 255, 0.03) !important;
    transition: background 0.2s ease !important;
    list-style: none !important;
}

.interview-accordion summary::-webkit-details-marker {
    display: none !important;
}

.interview-accordion summary::after {
    content: "▾" !important;
    font-size: 1.3rem !important;
    color: #818cf8 !important;
    transition: transform 0.25s ease !important;
}

.interview-accordion[open] summary::after {
    transform: rotate(180deg) !important;
}

.interview-accordion summary:hover {
    background: rgba(99, 102, 241, 0.1) !important;
}

.interview-accordion .accordion-body {
    padding: 20px 24px 24px 24px !important;
    border-top: 1px solid var(--inner-border) !important;
    color: var(--text-secondary) !important;
    line-height: 1.7 !important;
    font-size: 0.94rem !important;
}

.interview-tag {
    display: inline-block !important;
    font-size: 0.72rem !important;
    font-weight: 800 !important;
    padding: 3px 10px !important;
    border-radius: 9999px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-right: 10px !important;
}
.interview-tag.tech { background: rgba(99, 102, 241, 0.2); color: #a5b4fc; border: 1px solid rgba(99, 102, 241, 0.4); }
.interview-tag.behavioral { background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.4); }
.interview-tag.gap { background: rgba(245, 158, 11, 0.2); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.4); }
.interview-tag.leadership { background: rgba(236, 72, 153, 0.2); color: #f472b6; border: 1px solid rgba(236, 72, 153, 0.4); }

.star-box {
    margin: 14px 0 !important;
    padding: 16px 20px !important;
    border-radius: 10px !important;
    background: rgba(0, 0, 0, 0.3) !important;
    border-left: 3.5px solid #6366f1 !important;
}
.star-line { margin: 8px 0 !important; font-size: 0.93rem !important; line-height: 1.6 !important; }
.star-line strong { color: var(--text-primary) !important; }

/* Light Mode Overrides for Accordion */
.light-mode .interview-accordion {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06) !important;
}
.light-mode .interview-accordion summary {
    background: #f8fafc !important;
    color: #0f172a !important;
}
.light-mode .interview-accordion .accordion-body {
    border-top: 1px solid #f1f5f9 !important;
    color: #334155 !important;
}
.light-mode .star-box {
    background: #f1f5f9 !important;
    border-left: 3.5px solid #4f46e5 !important;
}
.light-mode .star-line strong {
    color: #0f172a !important;
}

/* ===== HIGH-IMPACT BULLET REWRITE CARDS ===== */
.bullet-card {
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    border-radius: 14px !important;
    padding: 20px 24px !important;
    margin: 18px 0 !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.25s ease !important;
}
.bullet-card:hover {
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 6px 22px rgba(99, 102, 241, 0.18) !important;
}
.bullet-before {
    background: rgba(239, 68, 68, 0.08) !important;
    border-left: 3.5px solid #ef4444 !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    margin: 8px 0 14px 0 !important;
    font-size: 0.92rem !important;
    color: var(--text-secondary) !important;
    line-height: 1.6 !important;
}
.bullet-after {
    background: rgba(16, 185, 129, 0.08) !important;
    border-left: 3.5px solid #10b981 !important;
    padding: 12px 16px !important;
    border-radius: 8px !important;
    margin: 8px 0 14px 0 !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    line-height: 1.6 !important;
}
.bullet-rationale {
    font-size: 0.88rem !important;
    color: var(--text-muted) !important;
    margin-top: 10px !important;
    line-height: 1.6 !important;
}
.light-mode .bullet-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
}
.light-mode .bullet-before {
    background: #fef2f2 !important;
    color: #991b1b !important;
}
.light-mode .bullet-after {
    background: #f0fdf4 !important;
    color: #166534 !important;
}
.light-mode .bullet-rationale {
    color: #64748b !important;
}

/* Primary Action Button: RUN ATS AUDIT (Strict Single-Line, Hardware-Accelerated) */
.actions-row {
    width: 100% !important;
    margin: 18px 0 28px !important;
    gap: 16px !important;
    display: flex !important;
    flex-direction: row !important;
    flex-wrap: nowrap !important;
    align-items: center !important;
    justify-content: center !important;
}

.actions-row > * {
    flex: 0 0 auto !important;
    min-width: max-content !important;
}

.actions-row,
.actions-row *,
#analyze-btn,
#analyze-btn *,
#clear-btn,
#clear-btn * {
    white-space: nowrap !important;
    text-wrap: nowrap !important;
    word-break: keep-all !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
}

#analyze-btn {
    white-space: nowrap !important;
    text-wrap: nowrap !important;
    word-break: keep-all !important;
    display: inline-flex !important;
    flex-shrink: 0 !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    width: auto !important;
    min-width: max-content !important;
    height: 52px !important;
    max-height: 52px !important;
    line-height: 52px !important;
    padding: 0 36px !important;
    border-radius: 12px !important;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #9333ea 100%) !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    font-size: 0.95rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    border: none !important;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.45) !important;
    cursor: pointer !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    box-sizing: border-box !important;
    transform: translateZ(0);
}

#analyze-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4), 0 10px 28px rgba(124, 58, 237, 0.55) !important;
}

#analyze-btn:active {
    transform: translateY(0) scale(0.98) !important;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4) !important;
}

#clear-btn {
    white-space: nowrap !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    min-width: 140px !important;
    height: 52px !important;
    max-height: 52px !important;
    line-height: 52px !important;
    padding: 0 24px !important;
    border-radius: 12px !important;
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--pill-heading-border) !important;
    color: var(--text-secondary) !important;
    font-weight: 700 !important;
    font-size: 0.92rem !important;
    letter-spacing: 0.02em !important;
    cursor: pointer !important;
    box-sizing: border-box !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease, color 0.25s ease !important;
}

#clear-btn:hover {
    border-color: #818cf8 !important;
    color: var(--text-primary) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.25) !important;
}

#clear-btn:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ===== DYNAMIC THEME-AWARE TYPOGRAPHY & OUTPUTS (ZERO HARDCODED COLORS) ===== */
.prose, 
.prose *, 
.md-output, 
.md-output *, 
.gradio-html, 
.gradio-html * {
    color: var(--text-primary);
}

.prose p, 
.prose li, 
.prose span, 
.md-output p, 
.md-output li {
    color: var(--text-secondary) !important;
    font-size: 0.96rem !important;
    line-height: 1.75 !important;
    margin-top: 6px !important;
    margin-bottom: 12px !important;
}

.prose strong, 
.prose b, 
.md-output strong, 
.md-output b {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
}

.prose h1, .prose h2, .prose h3, .prose h4,
.md-output h1, .md-output h2, .md-output h3, .md-output h4 {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    margin-top: 1.5rem !important;
    margin-bottom: 0.75rem !important;
    border-bottom: 1px solid var(--border-color) !important;
    padding-bottom: 8px !important;
}

.prose hr, .md-output hr {
    border: none !important;
    height: 1px !important;
    background: var(--border-color) !important;
    margin: 22px 0 !important;
}

table {
    border-collapse: collapse !important;
    width: 100% !important;
    background: var(--panel-bg) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 12px !important;
    margin: 16px 0 !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
    overflow: hidden !important;
}

th {
    background: var(--pill-heading-bg) !important;
    color: var(--text-primary) !important;
    font-weight: 800 !important;
    border: 1px solid var(--border-color) !important;
    padding: 11px 16px !important;
    text-align: left !important;
}

td {
    color: var(--text-secondary) !important;
    border: 1px solid var(--inner-border) !important;
    padding: 10px 16px !important;
    background: var(--inner-bg) !important;
}

.prose ul, .prose ol, .md-output ul, .md-output ol {
    padding-left: 1.5rem !important;
    margin-top: 8px !important;
    margin-bottom: 16px !important;
}

.prose li, .md-output li {
    margin-bottom: 6px !important;
}

.prose code, .md-output code {
    background: var(--pill-heading-bg) !important;
    border: 1px solid var(--border-color) !important;
    color: var(--text-primary) !important;
    padding: 3px 8px !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important;
}

/* ===== STATUS PILL STYLING ===== */
div[data-testid="html"]:has(.status-pill),
.gradio-html:has(.status-pill) {
    margin: 0 !important;
    padding: 0 !important;
}

.status-pill {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    padding: 7px 18px !important;
    border-radius: 9999px !important;
    font-size: 0.85rem !important;
    font-weight: 700 !important;
    line-height: 1.4 !important;
    min-height: 38px !important;
    box-sizing: border-box !important;
    margin: 4px 0 16px 0 !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    transform: translateZ(0);
}

.status-pill.ready {
    background: var(--status-ready-bg) !important;
    border: 1px solid var(--status-ready-border) !important;
    color: var(--status-ready-text) !important;
}

.status-pill.running {
    background: var(--status-running-bg) !important;
    border: 1px solid var(--status-running-border) !important;
    color: var(--status-running-text) !important;
}

.status-pill.error {
    background: var(--status-error-bg) !important;
    border: 1px solid var(--status-error-border) !important;
    color: var(--status-error-text) !important;
}

/* ===== RESUME INTELLIGENCE INSIGHTS DEDICATED SECTION ===== */
.insights-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 20px !important;
    padding: 20px 22px !important;
    margin-bottom: 0 !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    box-shadow: var(--panel-shadow) !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    max-height: 100% !important;
    box-sizing: border-box !important;
    overflow: hidden !important;
    animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease !important;
    transform: translateZ(0);
}

.insights-card:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.55), 0 0 20px rgba(99, 102, 241, 0.15) !important;
}

.insights-pill-heading {
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 4px 18px rgba(99, 102, 241, 0.25) !important;
}

.insights-pill-heading .insights-title-text,
.insights-title-text {
    letter-spacing: 0.12em !important;
    word-spacing: 0.38em !important;
    font-weight: 800 !important;
}

.insights-inner-scroll {
    overflow-y: auto !important;
    overflow-x: hidden !important;
    flex: 1 1 auto !important;
    max-height: 540px !important;
    padding-right: 6px !important;
    scrollbar-width: thin !important;
    scrollbar-color: rgba(124, 58, 237, 0.45) transparent !important;
}

.insights-inner-scroll::-webkit-scrollbar {
    width: 6px !important;
}

.insights-inner-scroll::-webkit-scrollbar-track {
    background: transparent !important;
}

.insights-inner-scroll::-webkit-scrollbar-thumb {
    background: rgba(124, 58, 237, 0.4) !important;
    border-radius: 9999px !important;
}

.insights-inner-scroll::-webkit-scrollbar-thumb:hover {
    background: rgba(124, 58, 237, 0.75) !important;
}

div[data-testid="html"]:has(.insights-container),
.gradio-html:has(.insights-container) {
    flex: 1 1 auto !important;
    display: flex !important;
    flex-direction: column !important;
    height: 100% !important;
    min-height: 0 !important;
}

.insights-container {
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    width: 100% !important;
    flex: 1 1 auto !important;
    height: 100% !important;
    min-height: 0 !important;
}

.insights-top-grid {
    display: grid !important;
    grid-template-columns: 200px 1fr !important;
    gap: 14px !important;
    align-items: stretch !important;
    width: 100% !important;
    flex-shrink: 0 !important;
}

.insights-gauge-box {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;
    background: var(--bg-card-inner) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 16px !important;
    padding: 14px 12px !important;
    box-sizing: border-box !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
}

.gauge-svg-wrap {
    position: relative !important;
    width: 145px !important;
    height: 145px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

.gauge-svg {
    display: block !important;
    width: 145px !important;
    height: 145px !important;
}

.gauge-arc {
    animation: sweepGauge 1.2s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    transform-origin: 90px 90px;
}

.insights-rating-badge {
    margin-top: 8px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 5px 14px !important;
    border-radius: 9999px !important;
    font-size: 0.74rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    text-align: center !important;
    white-space: nowrap !important;
}

.insights-benchmarks-box {
    display: flex !important;
    flex-direction: column !important;
    justify-content: space-between !important;
    height: 100% !important;
    background: var(--bg-card-inner) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 16px !important;
    padding: 14px 18px !important;
    box-sizing: border-box !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04) !important;
}

.benchmarks-header {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 0.78rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--text-muted) !important;
    margin-bottom: 10px !important;
}

.benchmarks-list {
    display: flex !important;
    flex-direction: column !important;
    gap: 9px !important;
    flex: 1 1 auto !important;
    justify-content: space-around !important;
}

.benchmark-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 3px !important;
}

.benchmark-label-row {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    font-size: 0.80rem !important;
    font-weight: 700 !important;
}

.benchmark-name {
    color: var(--text-secondary) !important;
}

.benchmark-score {
    font-weight: 800 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.80rem !important;
}

.benchmark-track {
    background: var(--bar-bg) !important;
    height: 7px !important;
    border-radius: 9999px !important;
    overflow: hidden !important;
    border: 1px solid var(--border-subtle) !important;
}

.benchmark-fill {
    height: 100% !important;
    border-radius: 9999px !important;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation: sweepBar 0.9s cubic-bezier(0.16, 1, 0.3, 1) both !important;
    transform: translateZ(0);
}

/* Loading radar arc, shimmer scan, and live telemetry pipeline */
.gauge-loading-arc {
    transform-origin: 90px 90px;
    animation: radarSpin 1.8s linear infinite !important;
    filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.8));
}

.shimmer-scan {
    background: linear-gradient(90deg, rgba(99, 102, 241, 0.08) 0%, rgba(129, 140, 248, 0.30) 50%, rgba(99, 102, 241, 0.08) 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmerScan 1.8s infinite linear !important;
}

.loading-rating-badge {
    animation: softShimmer 2s infinite ease-in-out !important;
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.45) !important;
}

.telemetry-pipeline-grid {
    display: flex !important;
    flex-direction: column !important;
    gap: 7px !important;
    margin-top: 8px !important;
}

.telemetry-pill-step {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 7px 12px !important;
    border-radius: 10px !important;
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    font-size: 0.82rem !important;
    color: var(--text-secondary) !important;
}

.telemetry-pill-step.active .telemetry-icon.check {
    color: #10b981;
    font-weight: 800;
}

.telemetry-pill-step.processing {
    border-color: rgba(99, 102, 241, 0.45);
    background: rgba(99, 102, 241, 0.12);
    color: var(--text-primary);
    font-weight: 700;
}

.telemetry-pill-step.processing .telemetry-icon.pulse {
    display: inline-block;
    color: #818cf8;
    animation: radarSpin 1.4s linear infinite;
    font-weight: 800;
}

.telemetry-pill-step.pending {
    opacity: 0.55;
}

.insights-verdict-box,
.scrollable-verdict-box {
    background: var(--verdict-bg) !important;
    border: 1px solid var(--verdict-border) !important;
    border-radius: 16px !important;
    padding: 16px 18px !important;
    box-sizing: border-box !important;
    display: flex !important;
    flex-direction: column !important;
    flex: 1 1 auto !important;
    min-height: 250px !important;
    max-height: 380px !important;
    overflow-y: auto !important;
    overflow-x: hidden !important;
    scrollbar-width: thin !important;
    scrollbar-color: rgba(99, 102, 241, 0.45) rgba(255, 255, 255, 0.03) !important;
    scroll-behavior: smooth !important;
}

.insights-verdict-box::-webkit-scrollbar,
.scrollable-verdict-box::-webkit-scrollbar {
    width: 6px !important;
}

.insights-verdict-box::-webkit-scrollbar-track,
.scrollable-verdict-box::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 9999px !important;
}

.insights-verdict-box::-webkit-scrollbar-thumb,
.scrollable-verdict-box::-webkit-scrollbar-thumb {
    background: rgba(99, 102, 241, 0.45) !important;
    border-radius: 9999px !important;
}

.insights-verdict-box::-webkit-scrollbar-thumb:hover,
.scrollable-verdict-box::-webkit-scrollbar-thumb:hover {
    background: rgba(99, 102, 241, 0.8) !important;
}

.verdict-footer-meta {
    margin-top: 14px !important;
    padding-top: 10px !important;
    border-top: 1px dashed var(--border-subtle) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    flex-shrink: 0 !important;
}

.meta-item {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    font-size: 0.76rem !important;
    color: var(--text-muted) !important;
    line-height: 1.4 !important;
}

.meta-icon {
    font-size: 0.82rem !important;
    flex-shrink: 0 !important;
}

.meta-label {
    font-weight: 500 !important;
}

.verdict-title {
    font-size: 0.82rem !important;
    font-weight: 800 !important;
    color: #818cf8 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

:root.light-mode .verdict-title {
    color: #4f46e5 !important;
}

.verdict-summary {
    font-size: 0.86rem !important;
    color: var(--text-secondary) !important;
    line-height: 1.5 !important;
    margin: 0 0 10px 0 !important;
}

.quick-wins-header {
    font-size: 0.76rem !important;
    font-weight: 800 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 6px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.quick-wins-grid {
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
}

.quick-win-item {
    display: flex !important;
    align-items: flex-start !important;
    gap: 10px !important;
    background: var(--bg-card-inner) !important;
    border: 1px solid var(--border-subtle) !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 10px !important;
    padding: 8px 12px !important;
    box-sizing: border-box !important;
    transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), background 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
    cursor: default !important;
}

.quick-win-item:hover {
    transform: translateX(4px) !important;
    background: rgba(99, 102, 241, 0.10) !important;
    border-left-color: #818cf8 !important;
    border-color: rgba(99, 102, 241, 0.35) !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25) !important;
}

:root.light-mode .quick-win-item:hover {
    background: rgba(99, 102, 241, 0.08) !important;
    border-left-color: #4f46e5 !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.12) !important;
}

.quick-win-bullet {
    color: #10b981 !important;
    font-weight: 800 !important;
    font-size: 0.88rem !important;
    flex-shrink: 0 !important;
    margin-top: 1px !important;
}

.quick-win-label {
    color: var(--text-secondary) !important;
    font-size: 0.83rem !important;
    line-height: 1.4 !important;
}

/* ATS System Compliance & Heuristic Telemetry Card */
.insights-telemetry-box {
    background: var(--bg-card-inner) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    padding: 12px 14px !important;
    box-sizing: border-box !important;
    transition: all 0.25s ease !important;
}

.insights-telemetry-box.completed {
    border-color: rgba(16, 185, 129, 0.3) !important;
    background: rgba(16, 185, 129, 0.04) !important;
}

.telemetry-box-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    margin-bottom: 8px !important;
}

.telemetry-title-wrap {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.telemetry-pulse-dot {
    width: 7px !important;
    height: 7px !important;
    border-radius: 50% !important;
    background: #6366f1 !important;
    box-shadow: 0 0 8px #6366f1 !important;
    animation: pulseGlow 1.8s infinite ease-in-out !important;
}

.telemetry-pulse-dot.green {
    background: #10b981 !important;
    box-shadow: 0 0 8px #10b981 !important;
}

.telemetry-box-title {
    font-size: 0.74rem !important;
    font-weight: 800 !important;
    color: #818cf8 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
}

.insights-telemetry-box.completed .telemetry-box-title {
    color: #34d399 !important;
}

.telemetry-engine-badge {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    padding: 2px 7px !important;
    border-radius: 6px !important;
    background: rgba(99, 102, 241, 0.18) !important;
    border: 1px solid rgba(129, 140, 248, 0.35) !important;
    color: #c7d2fe !important;
    letter-spacing: 0.04em !important;
}

.telemetry-engine-badge.green {
    background: rgba(16, 185, 129, 0.18) !important;
    border-color: rgba(16, 185, 129, 0.35) !important;
    color: #34d399 !important;
}

.telemetry-grid-metrics {
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 6px 10px !important;
    margin-bottom: 8px !important;
}

.telemetry-metric-item {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
    padding: 6px 8px !important;
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    border-radius: 8px !important;
}

.metric-top {
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
}

.metric-weight-pill {
    font-size: 0.66rem !important;
    font-weight: 800 !important;
    padding: 1px 5px !important;
    border-radius: 4px !important;
    background: rgba(99, 102, 241, 0.2) !important;
    color: #a5b4fc !important;
}

.metric-weight-pill.green {
    background: rgba(16, 185, 129, 0.2) !important;
    color: #34d399 !important;
}

.metric-name {
    font-size: 0.76rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}

.metric-desc {
    font-size: 0.68rem !important;
    color: var(--text-muted) !important;
    line-height: 1.3 !important;
}

.telemetry-system-tags {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 5px !important;
    padding-top: 6px !important;
    border-top: 1px dashed var(--border-subtle) !important;
}

.sys-tag {
    font-size: 0.66rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
    background: var(--tab-inactive-bg) !important;
    padding: 2px 7px !important;
    border-radius: 5px !important;
    border: 1px solid var(--border-subtle) !important;
}

.sys-tag.green {
    color: #34d399 !important;
    background: rgba(16, 185, 129, 0.08) !important;
    border-color: rgba(16, 185, 129, 0.25) !important;
}

#ats-progress-tracker-wrap {
    margin-bottom: 16px !important;
    display: block !important;
    width: 100% !important;
}

/* Skeleton Shimmer Loaders for Deliverable Tabs */
.skeleton-placeholder {
    padding: 24px 28px !important;
    border-radius: 14px !important;
    background: var(--inner-bg) !important;
    border: 1px solid var(--inner-border) !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
    margin: 8px 0 !important;
    animation: softShimmer 2.5s infinite ease-in-out !important;
}

.skeleton-header-row {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    margin-bottom: 4px !important;
}

.skeleton-icon-spin {
    font-size: 1.15rem !important;
    color: #818cf8 !important;
    animation: radarSpin 1.6s linear infinite !important;
    display: inline-block !important;
}

.skeleton-title {
    color: var(--text-primary) !important;
    font-size: 0.96rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
}

.skeleton-subtitle {
    font-size: 0.85rem !important;
    color: var(--text-muted) !important;
    margin-bottom: 6px !important;
    line-height: 1.5 !important;
}

.skeleton-line {
    height: 13px !important;
    border-radius: 6px !important;
    background: linear-gradient(90deg, rgba(255, 255, 255, 0.04) 0%, rgba(99, 102, 241, 0.16) 50%, rgba(255, 255, 255, 0.04) 100%) !important;
    background-size: 200% 100% !important;
    animation: shimmerScan 2s infinite linear !important;
}

.light-mode .skeleton-line {
    background: linear-gradient(90deg, rgba(0, 0, 0, 0.04) 0%, rgba(99, 102, 241, 0.14) 50%, rgba(0, 0, 0, 0.04) 100%) !important;
    background-size: 200% 100% !important;
}

/* Responsive breakpoints */
@media (max-width: 900px) {
    .insights-top-grid {
        grid-template-columns: 1fr;
    }
    .insights-gauge-box {
        padding: 18px;
    }
    .main-workspace-row {
        flex-direction: column !important;
        align-items: stretch !important;
    }
    .workspace-col {
        width: 100% !important;
    }
}

@media (max-width: 640px) {
    .gradio-container, gradio-app {
        padding: 10px 14px !important;
    }
    .header-row {
        padding: 14px 18px !important;
        flex-direction: column !important;
        gap: 14px !important;
        align-items: flex-start !important;
    }
    .header-row .gradio-column:last-child,
    .header-row > div:last-child {
        width: 100% !important;
        justify-content: flex-start !important;
    }
    .brand-title {
        font-size: 1.55rem !important;
    }
    .glass-card, .insights-card, .deliverables-card {
        padding: 16px 18px !important;
    }
    .resume-input-options {
        flex-direction: column !important;
    }
    .actions-row {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 12px !important;
    }
    .actions-row button {
        flex: 0 0 auto !important;
        white-space: nowrap !important;
        text-wrap: nowrap !important;
        word-break: keep-all !important;
    }
    #analyze-btn {
        width: auto !important;
        min-width: max-content !important;
        padding: 0 28px !important;
    }
    #clear-btn {
        width: auto !important;
        min-width: max-content !important;
        padding: 0 18px !important;
    }
    #model-picker .wrap {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
    }
    .compact-pdf-upload button.upload-button {
        min-height: 76px !important;
    }
}
"""
