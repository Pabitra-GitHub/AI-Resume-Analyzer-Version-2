"""
Report Export and File Management Service.
"""
import os
import uuid
import time
from typing import List, Optional
from config import REPORT_DIR, REPORT_MAX_AGE_SECONDS, logger

def cleanup_old_reports(max_age_seconds: int = REPORT_MAX_AGE_SECONDS) -> None:
    """Remove export reports older than max_age_seconds to prevent disk bloat."""
    try:
        if not os.path.exists(REPORT_DIR):
            return
        cutoff = time.time() - max_age_seconds
        for fname in os.listdir(REPORT_DIR):
            if fname.startswith("AI_Resume_Audit_Report_") and fname.endswith(".txt"):
                fpath = os.path.join(REPORT_DIR, fname)
                try:
                    if os.path.isfile(fpath) and os.path.getmtime(fpath) < cutoff:
                        os.remove(fpath)
                except OSError:
                    pass
    except Exception as e:
        logger.warning("Error during report cleanup: %s", e)

def generate_report_file(
    model_used: str,
    depth: str,
    company_name: str,
    overall_score: int,
    verdict: str,
    quick_wins: List[str],
    ats_md: str,
    cover_letter_md: str,
    interview_md: str,
    bullet_md: str,
    truncation_warnings: Optional[List[str]] = None,
) -> str:
    """
    Generate an isolated, plain text audit report with a unique UUID filename.
    Returns the absolute path to the generated report file.
    """
    cleanup_old_reports()
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    telemetry_label = f"{model_used} (Primary Engine)" if model_used == "gemini-3.8-flash" else f"{model_used} (Fallback Engine)"
    truncation_block = ""
    if truncation_warnings:
        truncation_block = "\n[INPUT TRUNCATION NOTICE]\n" + "\n".join([f"- {w}" for w in truncation_warnings]) + "\n"

    report_content = f"""# AI RESUME AUDIT REPORT
Engine Telemetry: {telemetry_label}
Audit Depth: {depth}
Target Company: {company_name if company_name.strip() else 'General / Unspecified'}
Score: {overall_score}/100
{truncation_block}
## EXECUTIVE VERDICT
{verdict}

### Top Quick Wins:
""" + "\n".join([f"- {w}" for w in quick_wins]) + f"""

---

## 1. ATS ANALYSIS & KEYWORD AUDIT
{ats_md}

---

## 2. TAILORED COVER LETTER
{cover_letter_md}

---

## 3. INTERVIEW STRATEGY & STAR PLAYBOOK
{interview_md}

---

## 4. HIGH-IMPACT BULLET-BY-BULLET REWRITES
{bullet_md}
"""

    unique_report_id = uuid.uuid4().hex[:12]
    report_filename = f"AI_Resume_Audit_Report_{unique_report_id}.txt"
    report_path = os.path.join(REPORT_DIR, report_filename)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path
