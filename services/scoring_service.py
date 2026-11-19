"""
Scoring and Dashboard Rendering Service.
"""
import math
from typing import Optional, Dict, List
from config import (
    WEIGHT_KEYWORDS,
    WEIGHT_EXPERIENCE,
    WEIGHT_SKILLS,
    WEIGHT_FORMATTING,
)

def calculate_reconciled_score(cat_scores: Dict[str, int], model_overall: Optional[int] = None) -> int:
    """
    Calculate the authoritative weighted ATS score:
    - keywords: 40%
    - experience: 30%
    - skills: 20%
    - formatting: 10%
    Reconciles with the model's overall score if within a ±4 point tolerance.
    """
    keywords = max(0, min(100, int(cat_scores.get("keywords", 70))))
    experience = max(0, min(100, int(cat_scores.get("experience", 75))))
    skills = max(0, min(100, int(cat_scores.get("skills", 80))))
    formatting = max(0, min(100, int(cat_scores.get("formatting", 85))))

    calculated = round(
        keywords * WEIGHT_KEYWORDS +
        experience * WEIGHT_EXPERIENCE +
        skills * WEIGHT_SKILLS +
        formatting * WEIGHT_FORMATTING
    )
    if model_overall is None or abs(int(model_overall) - calculated) > 4:
        return calculated
    return max(0, min(100, int(model_overall)))

def build_score_dashboard(score: int, cat_scores: dict, verdict_summary: str, quick_wins: list) -> str:
    """
    Build rich glassmorphic HTML score dashboard featuring:
    - SVG circular match gauge with glow and zero text overlap
    - Rating tier badge (Exceptional, Strong, Competitive, Needs Optimization)
    - Category benchmark progress bars
    - Executive verdict and actionable quick wins
    """
    score = max(0, min(100, int(score)))
    
    # Rating metadata
    if score == 0:
        rating_text = "PENDING AUDIT"
        badge_color = "var(--text-muted)"
        badge_bg = "var(--tab-inactive-bg)"
        border_color = "var(--tab-inactive-border)"
        glow = "transparent"
    elif score >= 88:
        rating_text = "EXCEPTIONAL MATCH"
        badge_color = "#10b981"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        border_color = "rgba(16, 185, 129, 0.35)"
        glow = "rgba(16, 185, 129, 0.4)"
    elif score >= 75:
        rating_text = "STRONG CONTENDER"
        badge_color = "#3b82f6"
        badge_bg = "rgba(59, 130, 246, 0.15)"
        border_color = "rgba(59, 130, 246, 0.35)"
        glow = "rgba(59, 130, 246, 0.4)"
    elif score >= 60:
        rating_text = "COMPETITIVE"
        badge_color = "#f59e0b"
        badge_bg = "rgba(245, 158, 11, 0.15)"
        border_color = "rgba(245, 158, 11, 0.35)"
        glow = "rgba(245, 158, 11, 0.4)"
    else:
        rating_text = "NEEDS OPTIMIZATION"
        badge_color = "#ef4444"
        badge_bg = "rgba(239, 68, 68, 0.15)"
        border_color = "rgba(239, 68, 68, 0.35)"
        glow = "rgba(239, 68, 68, 0.4)"

    radius = 70
    circumference = 2 * math.pi * radius
    dashoffset = circumference - (circumference * score / 100.0)

    cats = [
        ("Keywords & Hard Skills", cat_scores.get("keywords", int(score * 0.95)), "#6366f1"),
        ("Experience & Metrics", cat_scores.get("experience", int(score * 0.9)), "#8b5cf6"),
        ("Tech Stack & Domain Fit", cat_scores.get("skills", int(score * 1.02)), "#3b82f6"),
        ("Format & Readability", cat_scores.get("formatting", int(score * 0.98)), "#10b981"),
    ]

    cat_bars_html = ""
    delays = ["0.1s", "0.2s", "0.3s", "0.4s"]
    for idx, (name, val, color) in enumerate(cats):
        delay = delays[idx % len(delays)]
        val_clamped = max(0, min(100, int(val)))
        cat_bars_html += f"""
        <div class="benchmark-row">
            <div class="benchmark-label-row">
                <span class="benchmark-name">{name}</span>
                <span class="benchmark-score" style="color: {color};">{val_clamped}%</span>
            </div>
            <div class="benchmark-track">
                <div class="benchmark-fill" style="background: {color}; --target-width: {val_clamped}%; width: {val_clamped}%; animation-delay: {delay};"></div>
            </div>
        </div>
        """

    # Render all actionable recommendations and diagnostic wins
    if score == 0:
        display_wins = [
            "Match core keywords and required certifications verbatim with the job posting",
            "Eliminate ATS parser traps: tables, text boxes, multi-columns, and complex headers",
            "Quantify accomplishments with measurable metrics (e.g. %, $, team size, volume)",
            "Align job titles and seniority scope with target organization requirements",
            "Ensure standard headings: Professional Experience, Skills, Education, Projects",
            "Review generated tailored cover letter, STAR interview playbook & high-impact rewrites below"
        ]
    else:
        display_wins = quick_wins if quick_wins else [
            "Align hard skills and certifications with job description keywords",
            "Enhance bullet statements with strong action verbs and quantified impact metrics",
            "Standardize section titles for maximum Taleo and Workday parser accuracy",
            "Review personalized cover letter and STAR answers in the deliverables tabs below"
        ]

    quick_wins_html = ""
    for item in display_wins:
        quick_wins_html += f"""
        <div class="quick-win-item">
            <span class="quick-win-bullet">✓</span>
            <span class="quick-win-label">{item}</span>
        </div>
        """

    return f"""
    <div class="insights-container">
        <!-- Top Responsive Grid: Circular Gauge (Left) + Category Benchmarks (Right) -->
        <div class="insights-top-grid">
            <!-- Left Box: Circular Gauge & Rating Badge -->
            <div class="insights-gauge-box">
                <div class="gauge-svg-wrap">
                    <svg width="160" height="160" viewBox="0 0 180 180" class="gauge-svg">
                        <!-- Concentric Telemetry Guide Track -->
                        <circle cx="90" cy="90" r="78" fill="none" stroke="var(--border-subtle)" stroke-width="1.5" stroke-dasharray="3 4" opacity="0.7" />
                        <!-- Background Track -->
                        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="var(--gauge-track)" stroke-width="12" />
                        <!-- Progress Arc -->
                        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="{badge_color}" stroke-width="12"
                                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{dashoffset:.2f}" stroke-linecap="round"
                                transform="rotate(-90 90 90)"
                                class="gauge-arc"
                                style="filter: drop-shadow(0 0 10px {glow}); --target-offset: {dashoffset:.2f}; stroke-dashoffset: {dashoffset:.2f};" />
                        <!-- Centered Score Text (Locked Coordinates with Dynamic Animation) -->
                        <text x="90" y="84" text-anchor="middle" dominant-baseline="central" fill="var(--text-primary)"
                              font-size="44" font-weight="800" font-family="'Plus Jakarta Sans', sans-serif" letter-spacing="-0.02em" id="audit-score-counter">
                            {score}
                        </text>
                        <text x="90" y="116" text-anchor="middle" dominant-baseline="central" fill="var(--text-muted)"
                              font-size="11" font-weight="700" font-family="'Plus Jakarta Sans', sans-serif" letter-spacing="0.12em">
                            OUT OF 100
                        </text>
                    </svg>
                    <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg'></svg>" style="display:none;" onerror="(function(el){{var target={score};if(!el||target<=0)return;var startTime=null,duration=1200;function step(ts){{if(!startTime)startTime=ts;var progress=Math.min((ts-startTime)/duration,1);var ease=1-Math.pow(1-progress,3);el.textContent=Math.round(ease*target);if(progress<1){{window.requestAnimationFrame(step);}}else{{el.textContent=target;}}}}window.requestAnimationFrame(step);}})(document.getElementById('audit-score-counter'))" />
                </div>
                
                <div class="insights-rating-badge" style="background: {badge_bg}; border: 1px solid {border_color}; color: {badge_color}; box-shadow: 0 4px 12px {glow};">
                    {rating_text}
                </div>
            </div>

            <!-- Right Box: Category Benchmarks -->
            <div class="insights-benchmarks-box">
                <div class="benchmarks-header">
                    <span>📊</span>
                    <span>CATEGORY BENCHMARKS</span>
                </div>
                <div class="benchmarks-list">
                    {cat_bars_html}
                </div>
            </div>
        </div>

        <!-- Expanded Scrollable Box: Executive Verdict & Comprehensive Action Plan -->
        <div class="insights-verdict-box scrollable-verdict-box">
            <div class="verdict-title">
                <span>🎯</span>
                <span>Executive Verdict & Action Plan</span>
            </div>
            <p class="verdict-summary">
                {verdict_summary}
            </p>
            
            <div class="quick-wins-header">
                <span>⚡</span>
                <span>Actionable Recommendations & Quick Wins:</span>
            </div>
            <div class="quick-wins-grid">
                {quick_wins_html}
            </div>

            <div class="verdict-footer-meta">
                <div class="meta-item">
                    <span class="meta-icon">⚙️</span>
                    <span class="meta-label">ATS Rubric Weights: 40% Keywords • 30% Experience • 20% Skills • 10% Formatting</span>
                </div>
                <div class="meta-item">
                    <span class="meta-icon">📑</span>
                    <span class="meta-label">Scroll to view all recommendations • Detailed deliverables ready in tabs below</span>
                </div>
            </div>
        </div>
    </div>
    """

def build_loading_dashboard(model_name: str, depth: str, initial_seconds: int = 12, percent: int = 1) -> str:
    """
    Build rich animated loading dashboard with continuous live progress feedback:
    - High-tech circular radar scanner with glowing rotating arc and live SVG progress arc
    - Centered live progress percentage counter
    - 'COMPUTING ATS MATCH... {percent}%' rating pill
    - Live calibrated category benchmark telemetry bars
    - Live 4-milestone pipeline telemetry steps dynamically updating by phase
    """
    percent = max(1, min(100, int(percent)))
    radius = 70
    circumference = 2 * math.pi * radius
    dashoffset = circumference - (circumference * percent / 100.0)

    # Dynamic telemetry steps based on current percent
    p1_class = "active" if percent >= 25 else "processing"
    p1_icon = "check" if percent >= 25 else "pulse"
    p1_symbol = "✓" if percent >= 25 else "⚡"

    p2_class = "active" if percent >= 50 else ("processing" if percent >= 25 else "pending")
    p2_icon = "check" if percent >= 50 else ("pulse" if percent >= 25 else "")
    p2_symbol = "✓" if percent >= 50 else ("⚡" if percent >= 25 else "⏳")

    p3_class = "active" if percent >= 75 else ("processing" if percent >= 50 else "pending")
    p3_icon = "check" if percent >= 75 else ("pulse" if percent >= 50 else "")
    p3_symbol = "✓" if percent >= 75 else ("⚡" if percent >= 50 else "⏳")

    p4_class = "active" if percent >= 100 else ("processing" if percent >= 75 else "pending")
    p4_icon = "check" if percent >= 100 else ("pulse" if percent >= 75 else "")
    p4_symbol = "✓" if percent >= 100 else ("⚡" if percent >= 75 else "⏳")

    # Dynamic benchmark bar widths calibrated by progress
    kw_width = max(15, min(100, int(percent * 1.12)))
    exp_width = max(15, min(100, int(percent * 0.94)))
    tech_width = max(15, min(100, int(percent * 1.04)))
    fmt_width = max(15, min(100, int(percent * 0.98)))

    kw_status = "Complete" if percent >= 50 else "Scanning..."
    exp_status = "Complete" if percent >= 75 else "Evaluating..."
    tech_status = "Complete" if percent >= 75 else "Benchmarking..."
    fmt_status = "Complete" if percent >= 90 else "Validating..."

    return f"""
    <div class="insights-container loading-state">
        <!-- Top Responsive Grid: Circular Gauge (Left) + Category Benchmarks (Right) -->
        <div class="insights-top-grid">
            <!-- Left Box: Circular Gauge with Live Progress Arc, Centered Percent & Radar Overlay -->
            <div class="insights-gauge-box">
                <div class="gauge-svg-wrap">
                    <svg width="160" height="160" viewBox="0 0 180 180" class="gauge-svg">
                        <!-- Concentric Telemetry Guide Track -->
                        <circle cx="90" cy="90" r="78" fill="none" stroke="var(--border-subtle)" stroke-width="1.5" stroke-dasharray="3 4" opacity="0.7" />
                        <!-- Background Track -->
                        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="var(--gauge-track)" stroke-width="12" />
                        <!-- Live Continuous Progress Arc -->
                        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="#6366f1" stroke-width="12"
                                stroke-dasharray="{circumference:.2f}" stroke-dashoffset="{dashoffset:.2f}" stroke-linecap="round"
                                transform="rotate(-90 90 90)"
                                style="filter: drop-shadow(0 0 10px rgba(99, 102, 241, 0.6)); transition: stroke-dashoffset 0.15s linear;" />
                        <!-- Rotating Radar Scanner Arc Overlay -->
                        <circle cx="90" cy="90" r="{radius}" fill="none" stroke="#818cf8" stroke-width="12"
                                stroke-dasharray="90 350" stroke-linecap="round"
                                class="gauge-loading-arc" opacity="0.45" />
                        <!-- Centered Live Percentage Counter -->
                        <text x="90" y="70" text-anchor="middle" dominant-baseline="central" fill="var(--text-primary)"
                              font-size="34" font-weight="800" font-family="'Plus Jakarta Sans', sans-serif" letter-spacing="-0.02em">
                            {percent}%
                        </text>
                        <text x="90" y="96" text-anchor="middle" dominant-baseline="central" fill="var(--text-primary)"
                              font-size="11" font-weight="800" font-family="'Plus Jakarta Sans', sans-serif" letter-spacing="0.14em">
                            AUDITING
                        </text>
                        <text x="90" y="112" text-anchor="middle" dominant-baseline="central" fill="#818cf8"
                              font-size="9" font-weight="800" font-family="'Plus Jakarta Sans', sans-serif" letter-spacing="0.12em">
                            IN PROGRESS
                        </text>
                    </svg>
                </div>
                
                <div class="insights-rating-badge loading-rating-badge" style="background: rgba(99, 102, 241, 0.15); border: 1px solid rgba(129, 140, 248, 0.4); color: #c7d2fe; box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);">
                    ⏳ COMPUTING ATS MATCH... {percent}%
                </div>
            </div>

            <!-- Right Box: Shimmering Category Benchmarks -->
            <div class="insights-benchmarks-box">
                <div class="benchmarks-header">
                    <span>📊</span>
                    <span>CALIBRATING BENCHMARKS ({percent}%)...</span>
                </div>
                <div class="benchmarks-list">
                    <div class="benchmark-row">
                        <div class="benchmark-label-row">
                            <span class="benchmark-name">Keywords & Hard Skills</span>
                            <span class="benchmark-score" style="color: #818cf8;">{kw_status}</span>
                        </div>
                        <div class="benchmark-track">
                            <div class="benchmark-fill shimmer-scan" style="background: linear-gradient(90deg, #6366f1, #818cf8, #6366f1); width: {kw_width}%; transition: width 0.15s linear;"></div>
                        </div>
                    </div>
                    <div class="benchmark-row">
                        <div class="benchmark-label-row">
                            <span class="benchmark-name">Experience & Metrics</span>
                            <span class="benchmark-score" style="color: #a78bfa;">{exp_status}</span>
                        </div>
                        <div class="benchmark-track">
                            <div class="benchmark-fill shimmer-scan" style="background: linear-gradient(90deg, #8b5cf6, #c084fc, #8b5cf6); width: {exp_width}%; transition: width 0.15s linear;"></div>
                        </div>
                    </div>
                    <div class="benchmark-row">
                        <div class="benchmark-label-row">
                            <span class="benchmark-name">Tech Stack & Domain Fit</span>
                            <span class="benchmark-score" style="color: #60a5fa;">{tech_status}</span>
                        </div>
                        <div class="benchmark-track">
                            <div class="benchmark-fill shimmer-scan" style="background: linear-gradient(90deg, #3b82f6, #60a5fa, #3b82f6); width: {tech_width}%; transition: width 0.15s linear;"></div>
                        </div>
                    </div>
                    <div class="benchmark-row">
                        <div class="benchmark-label-row">
                            <span class="benchmark-name">Format & Readability</span>
                            <span class="benchmark-score" style="color: #34d399;">{fmt_status}</span>
                        </div>
                        <div class="benchmark-track">
                            <div class="benchmark-fill shimmer-scan" style="background: linear-gradient(90deg, #10b981, #34d399, #10b981); width: {fmt_width}%; transition: width 0.15s linear;"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Bottom Box: Live Telemetry Pipeline -->
        <div class="insights-verdict-box scrollable-verdict-box">
            <div class="verdict-title">
                <span>⚡</span>
                <span>LIVE AUDIT TELEMETRY & PIPELINE MONITOR ({percent}%)</span>
            </div>
            <p class="verdict-summary">
                Analyzing candidate profile with <strong>{model_name}</strong> for <strong>{depth}</strong>. Reconciling resume text against target qualifications, detecting keyword gaps, and calculating definitive ATS score...
            </p>
            
            <div class="telemetry-pipeline-grid">
                <div class="telemetry-pill-step {p1_class}">
                    <span class="telemetry-icon {p1_icon}">{p1_symbol}</span>
                    <span class="telemetry-text">01. Input Extraction & Text Sanitization</span>
                </div>
                <div class="telemetry-pill-step {p2_class}">
                    <span class="telemetry-icon {p2_icon}">{p2_symbol}</span>
                    <span class="telemetry-text">02. Semantic Keyword Gap & Skills Matching</span>
                </div>
                <div class="telemetry-pill-step {p3_class}">
                    <span class="telemetry-icon {p3_icon}">{p3_symbol}</span>
                    <span class="telemetry-text">03. Weighted Formula ATS Calibration (40/30/20/10)</span>
                </div>
                <div class="telemetry-pill-step {p4_class}">
                    <span class="telemetry-icon {p4_icon}">{p4_symbol}</span>
                    <span class="telemetry-text">04. Asset Synthesis (Cover Letter, STAR, Rewrites)</span>
                </div>
            </div>
        </div>
    </div>
    """

def build_ats_progress_line(percent: int = 50, is_completed: bool = False, custom_status: Optional[str] = None) -> str:
    """
    Build interactive horizontal progress bar line for 'ATS & Keyword Audit':
    Shows:
    - Continuous granular percentage track (1% to 100%) with glowing cyber pulse
    - 4 milestone stage chips dynamically transitioning (Pending, Scanning, Done)
    - Live contextual status feedback banner
    """
    if is_completed or percent >= 100:
        percent = 100
        status_text = custom_status or "All 4 ATS Audit Stages Completed Successfully • Authoritative Final Match Calibrated"
        status_class = "completed"
        step1_class, step2_class, step3_class, step4_class = "done", "done", "done", "done"
        step1_badge, step2_badge, step3_badge, step4_badge = "✓ Complete", "✓ Complete", "✓ Complete", "✓ Complete"
    else:
        percent = max(1, min(99, int(percent)))
        status_class = "in-progress"

        # Step 1: Input Extraction (0 - 25%)
        if percent < 25:
            step1_class = "active"
            step1_badge = "⚡ Parsing..."
        else:
            step1_class = "done"
            step1_badge = "✓ Extracted"

        # Step 2: Keyword Gap Audit (25 - 50%)
        if percent < 25:
            step2_class = "pending"
            step2_badge = "⏳ Queued"
        elif percent < 50:
            step2_class = "active"
            step2_badge = "⚡ Scanning..."
        else:
            step2_class = "done"
            step2_badge = "✓ Complete"

        # Step 3: Weighted Calibration (50 - 75%)
        if percent < 50:
            step3_class = "pending"
            step3_badge = "⏳ Queued"
        elif percent < 75:
            step3_class = "active"
            step3_badge = "⚡ Calibrating..."
        else:
            step3_class = "done"
            step3_badge = "✓ Complete"

        # Step 4: Asset Synthesis (75 - 100%)
        if percent < 75:
            step4_class = "pending"
            step4_badge = "⏳ Queued"
        else:
            step4_class = "active"
            step4_badge = "⚡ Synthesizing..."

        if custom_status:
            status_text = custom_status
        elif percent < 25:
            status_text = "Audit In Progress • Parsing input text & verifying character boundaries..."
        elif percent < 50:
            status_text = "Audit In Progress • Analyzing Keyword Density, Hard Skills & ATS Bottlenecks..."
        elif percent < 75:
            status_text = "Audit In Progress • Calibrating rubric weights (40% Keywords • 30% Exp • 20% Skills • 10% Format)..."
        else:
            status_text = "Audit In Progress • Synthesizing Tailored Cover Letter, STAR Playbook & Bullet Rewrites..."

    # CRITICAL: Every line starts at column 0 to prevent markdown code block wrap (<pre><code>)
    return (
f'<div class="ats-progress-line-container {status_class}">\n'
f'<div class="progress-line-header">\n'
f'<div class="progress-title-wrap">\n'
f'<span class="progress-pulse-dot"></span>\n'
f'<span class="progress-title">ATS AUDIT PIPELINE & PROGRESS TRACKER</span>\n'
f'</div>\n'
f'<div class="progress-percent-badge">{percent}% COMPLETE</div>\n'
f'</div>\n'
f'<div class="progress-bar-track">\n'
f'<div class="progress-bar-fill" style="width: {percent}%;">\n'
f'<div class="progress-laser-glow"></div>\n'
f'</div>\n'
f'</div>\n'
f'<div class="progress-milestones-grid">\n'
f'<div class="progress-milestone {step1_class}">\n'
f'<div class="milestone-top">\n'
f'<span class="milestone-num">01</span>\n'
f'<span class="milestone-badge">{step1_badge}</span>\n'
f'</div>\n'
f'<div class="milestone-label">Input Extraction</div>\n'
f'<div class="milestone-desc">PDF text parsed & character bounds verified</div>\n'
f'</div>\n'
f'<div class="progress-milestone {step2_class}">\n'
f'<div class="milestone-top">\n'
f'<span class="milestone-num">02</span>\n'
f'<span class="milestone-badge">{step2_badge}</span>\n'
f'</div>\n'
f'<div class="milestone-label">Keyword Gap Audit</div>\n'
f'<div class="milestone-desc">Matching hard skills, certifications & terminology</div>\n'
f'</div>\n'
f'<div class="progress-milestone {step3_class}">\n'
f'<div class="milestone-top">\n'
f'<span class="milestone-num">03</span>\n'
f'<span class="milestone-badge">{step3_badge}</span>\n'
f'</div>\n'
f'<div class="milestone-label">Weighted Calibration</div>\n'
f'<div class="milestone-desc">Reconciling experience, skills & ATS formulas</div>\n'
f'</div>\n'
f'<div class="progress-milestone {step4_class}">\n'
f'<div class="milestone-top">\n'
f'<span class="milestone-num">04</span>\n'
f'<span class="milestone-badge">{step4_badge}</span>\n'
f'</div>\n'
f'<div class="milestone-label">Asset Synthesis</div>\n'
f'<div class="milestone-desc">Synthesizing cover letter, STAR interview & rewrites</div>\n'
f'</div>\n'
f'</div>\n'
f'<div class="progress-status-footer">\n'
f'<span class="status-footer-icon">ℹ️</span>\n'
f'<span class="status-footer-text">{status_text}</span>\n'
f'</div>\n'
f'</div>'
    )

def build_skeleton_markdown(title: str, subtitle: str) -> str:
    """
    Generate rich HTML skeleton placeholder for tab deliverables during model execution.
    Features spinning icon, clear phase message, and animated shimmering horizontal bars.
    """
    return f"""
<div class="skeleton-placeholder">
    <div class="skeleton-header-row">
        <span class="skeleton-icon-spin">⟳</span>
        <span class="skeleton-title">{title}</span>
    </div>
    <div class="skeleton-subtitle">{subtitle}</div>
    <div class="skeleton-line" style="width: 95%;"></div>
    <div class="skeleton-line" style="width: 82%;"></div>
    <div class="skeleton-line" style="width: 88%;"></div>
    <div class="skeleton-line" style="width: 64%;"></div>
</div>
"""

