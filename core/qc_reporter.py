# core/qc_reporter.py
"""
Quality Control reporting for Kearney AI Coding Assistant projects.

Provides:
- Automated QC checks at multiple checkpoints
- Brand compliance validation
- Chart quality assessment
- Data compliance checking
- QC report generation

Usage:
    from core.qc_reporter import (
        run_qc_checks,
        generate_qc_report,
        CheckResult,
    )

    # Run all checks
    results = run_qc_checks(Path("."))

    # Generate report
    report_path = generate_qc_report(Path("."), results)
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import yaml


class CheckStatus(Enum):
    """Status of a QC check."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"
    SKIPPED = "skipped"


@dataclass
class CheckResult:
    """Result of a single QC check."""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class QCReport:
    """Complete QC report."""
    project_name: str
    generated_at: str
    overall_status: CheckStatus
    brand_checks: List[CheckResult] = field(default_factory=list)
    chart_checks: List[CheckResult] = field(default_factory=list)
    data_checks: List[CheckResult] = field(default_factory=list)
    file_checks: List[CheckResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "project_name": self.project_name,
            "generated_at": self.generated_at,
            "overall_status": self.overall_status.value,
            "brand_checks": [
                {"name": c.name, "status": c.status.value, "message": c.message, "details": c.details}
                for c in self.brand_checks
            ],
            "chart_checks": [
                {"name": c.name, "status": c.status.value, "message": c.message, "file_path": c.file_path}
                for c in self.chart_checks
            ],
            "data_checks": [
                {"name": c.name, "status": c.status.value, "message": c.message}
                for c in self.data_checks
            ],
            "file_checks": [
                {"name": c.name, "status": c.status.value, "message": c.message, "file_path": c.file_path}
                for c in self.file_checks
            ],
            "recommendations": self.recommendations,
        }


# Kearney brand colors
KEARNEY_PURPLE = "#7823DC"
KEARNEY_PURPLE_VARIANTS = ["#7823DC", "#7823dc", "7823DC", "rgb(120,35,220)"]

# Forbidden colors (greens)
FORBIDDEN_COLORS = [
    "#00FF00", "#00ff00",  # Bright green
    "#2E7D32", "#2e7d32",  # Material green
    "#4CAF50", "#4caf50",  # Green 500
    "#008000", "#008000",  # Green
    "#00FF7F", "#00ff7f",  # Spring green
    "#228B22", "#228b22",  # Forest green
    "#32CD32", "#32cd32",  # Lime green
    "#90EE90", "#90ee90",  # Light green
]

# Emoji pattern
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"  # dingbats
    "\U000024C2-\U0001F251"  # enclosed characters
    "]+",
    flags=re.UNICODE
)

# PII patterns
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    "phone": re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
}


def check_forbidden_colors(content: str) -> Tuple[bool, List[str]]:
    """
    Check if content contains forbidden colors.

    Args:
        content: Text content to check

    Returns:
        Tuple of (has_forbidden, list of found colors)
    """
    found = []
    content_lower = content.lower()

    for color in FORBIDDEN_COLORS:
        if color.lower() in content_lower:
            found.append(color)

    return len(found) > 0, found


def check_emojis(content: str) -> Tuple[bool, List[str]]:
    """
    Check if content contains emojis.

    Args:
        content: Text content to check

    Returns:
        Tuple of (has_emojis, list of found emojis)
    """
    found = EMOJI_PATTERN.findall(content)
    return len(found) > 0, found


def check_gridlines_in_code(content: str) -> bool:
    """
    Check if Python code enables gridlines.

    Args:
        content: Python code content

    Returns:
        True if gridlines are enabled
    """
    gridline_patterns = [
        r"\.grid\s*\(\s*True",
        r"\.grid\s*\(\s*\)",
        r"ax\.grid\(",
        r"plt\.grid\(",
        r"gridlines\s*=\s*True",
    ]

    for pattern in gridline_patterns:
        if re.search(pattern, content):
            return True

    return False


def check_pii(content: str) -> Tuple[bool, Dict[str, int]]:
    """
    Check if content contains potential PII.

    Args:
        content: Text content to check

    Returns:
        Tuple of (has_pii, dict of type -> count)
    """
    found = {}

    for pii_type, pattern in PII_PATTERNS.items():
        matches = pattern.findall(content)
        if matches:
            found[pii_type] = len(matches)

    return len(found) > 0, found


def check_file_brand_compliance(file_path: Path) -> List[CheckResult]:
    """
    Check a single file for brand compliance.

    Args:
        file_path: Path to file to check

    Returns:
        List of CheckResult
    """
    results = []

    try:
        content = file_path.read_text(errors="ignore")
    except Exception as e:
        return [CheckResult(
            name="File Read",
            status=CheckStatus.SKIPPED,
            message=f"Could not read file: {e}",
            file_path=str(file_path)
        )]

    # Check forbidden colors
    has_forbidden, found_colors = check_forbidden_colors(content)
    if has_forbidden:
        results.append(CheckResult(
            name="Forbidden Colors",
            status=CheckStatus.FAIL,
            message=f"Found forbidden colors: {', '.join(set(found_colors))}",
            file_path=str(file_path)
        ))
    else:
        results.append(CheckResult(
            name="Forbidden Colors",
            status=CheckStatus.PASS,
            message="No forbidden colors found",
            file_path=str(file_path)
        ))

    # Check emojis
    has_emojis, found_emojis = check_emojis(content)
    if has_emojis:
        results.append(CheckResult(
            name="Emojis",
            status=CheckStatus.FAIL,
            message=f"Found {len(found_emojis)} emoji(s)",
            file_path=str(file_path)
        ))
    else:
        results.append(CheckResult(
            name="Emojis",
            status=CheckStatus.PASS,
            message="No emojis found",
            file_path=str(file_path)
        ))

    # Check gridlines in Python files
    if file_path.suffix == ".py":
        has_gridlines = check_gridlines_in_code(content)
        if has_gridlines:
            results.append(CheckResult(
                name="Gridlines",
                status=CheckStatus.FAIL,
                message="Code enables gridlines (not allowed)",
                file_path=str(file_path)
            ))
        else:
            results.append(CheckResult(
                name="Gridlines",
                status=CheckStatus.PASS,
                message="No gridlines enabled",
                file_path=str(file_path)
            ))

    return results


def check_data_compliance(project_path: Path) -> List[CheckResult]:
    """
    Check data files for compliance issues.

    Args:
        project_path: Root path of the project

    Returns:
        List of CheckResult
    """
    results = []
    outputs_dir = Path(project_path) / "outputs"
    exports_dir = Path(project_path) / "exports"

    # Check for PII in output files
    pii_found_files = []
    for directory in [outputs_dir, exports_dir]:
        if not directory.exists():
            continue

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".csv", ".json", ".txt", ".md"]:
                try:
                    content = file_path.read_text(errors="ignore")
                    has_pii, pii_types = check_pii(content)
                    if has_pii:
                        pii_found_files.append((file_path, pii_types))
                except Exception:
                    pass

    if pii_found_files:
        details = "\n".join(
            f"  - {f}: {', '.join(t.keys())}" for f, t in pii_found_files
        )
        results.append(CheckResult(
            name="PII Detection",
            status=CheckStatus.WARNING,
            message=f"Potential PII found in {len(pii_found_files)} file(s)",
            details=details
        ))
    else:
        results.append(CheckResult(
            name="PII Detection",
            status=CheckStatus.PASS,
            message="No PII patterns detected in outputs"
        ))

    # Check for raw data in exports
    data_dir = Path(project_path) / "data" / "raw"
    if data_dir.exists() and exports_dir.exists():
        raw_files = {f.name for f in data_dir.iterdir() if f.is_file()}
        export_files = {f.name for f in exports_dir.rglob("*") if f.is_file()}

        exposed = raw_files & export_files
        if exposed:
            results.append(CheckResult(
                name="Raw Data Exposure",
                status=CheckStatus.FAIL,
                message=f"Raw data files in exports: {', '.join(exposed)}"
            ))
        else:
            results.append(CheckResult(
                name="Raw Data Exposure",
                status=CheckStatus.PASS,
                message="No raw data files in exports"
            ))

    return results


def check_outputs(project_path: Path) -> List[CheckResult]:
    """
    Check output files for brand compliance.

    Args:
        project_path: Root path of the project

    Returns:
        List of CheckResult
    """
    results = []
    outputs_dir = Path(project_path) / "outputs"

    if not outputs_dir.exists():
        return [CheckResult(
            name="Outputs Directory",
            status=CheckStatus.SKIPPED,
            message="outputs/ directory not found"
        )]

    # Check charts directory
    charts_dir = outputs_dir / "charts"
    if charts_dir.exists():
        chart_files = list(charts_dir.glob("*.png")) + list(charts_dir.glob("*.jpg"))
        for chart_file in chart_files:
            # For images, we can only check the filename for now
            # Full image analysis would require PIL/image processing
            results.append(CheckResult(
                name=f"Chart: {chart_file.name}",
                status=CheckStatus.PASS,
                message="Chart file exists",
                file_path=str(chart_file)
            ))

    # Check reports directory
    reports_dir = outputs_dir / "reports"
    if reports_dir.exists():
        for report_file in reports_dir.glob("*.md"):
            file_results = check_file_brand_compliance(report_file)
            results.extend(file_results)

    return results


def run_qc_checks(project_path: Path) -> QCReport:
    """
    Run all QC checks on a project.

    Args:
        project_path: Root path of the project

    Returns:
        QCReport with all results
    """
    project_path = Path(project_path)

    # Get project name
    project_name = "Unknown"
    spec_path = project_path / "project_state" / "spec.yaml"
    if spec_path.exists():
        try:
            spec = yaml.safe_load(spec_path.read_text())
            project_name = spec.get("meta", {}).get("project_name", "Unknown")
        except Exception:
            pass

    report = QCReport(
        project_name=project_name,
        generated_at=datetime.now().isoformat(),
        overall_status=CheckStatus.PASS,
    )

    # Brand compliance checks
    outputs_dir = project_path / "outputs"
    if outputs_dir.exists():
        for subdir in ["charts", "reports"]:
            check_dir = outputs_dir / subdir
            if check_dir.exists():
                for file_path in check_dir.rglob("*"):
                    if file_path.is_file() and file_path.suffix in [".py", ".md", ".txt", ".json"]:
                        file_results = check_file_brand_compliance(file_path)
                        report.brand_checks.extend(file_results)

    # Chart checks
    report.chart_checks = check_outputs(project_path)

    # Data compliance checks
    report.data_checks = check_data_compliance(project_path)

    # Determine overall status
    all_checks = report.brand_checks + report.chart_checks + report.data_checks

    has_fail = any(c.status == CheckStatus.FAIL for c in all_checks)
    has_warning = any(c.status == CheckStatus.WARNING for c in all_checks)

    if has_fail:
        report.overall_status = CheckStatus.FAIL
    elif has_warning:
        report.overall_status = CheckStatus.WARNING
    else:
        report.overall_status = CheckStatus.PASS

    # Generate recommendations
    report.recommendations = generate_recommendations(report)

    return report


def generate_recommendations(report: QCReport) -> List[str]:
    """
    Generate recommendations based on QC results.

    Args:
        report: QCReport to analyze

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Check for forbidden color issues
    color_fails = [c for c in report.brand_checks if c.name == "Forbidden Colors" and c.status == CheckStatus.FAIL]
    if color_fails:
        recommendations.append(
            "Replace forbidden green colors with Kearney Purple (#7823DC) or neutral grays"
        )

    # Check for emoji issues
    emoji_fails = [c for c in report.brand_checks if c.name == "Emojis" and c.status == CheckStatus.FAIL]
    if emoji_fails:
        recommendations.append(
            "Remove all emojis from outputs - Kearney style requires professional, emoji-free content"
        )

    # Check for gridline issues
    gridline_fails = [c for c in report.brand_checks if c.name == "Gridlines" and c.status == CheckStatus.FAIL]
    if gridline_fails:
        recommendations.append(
            "Disable gridlines in all charts - use ax.grid(False) or remove grid() calls"
        )

    # Check for PII issues
    pii_warnings = [c for c in report.data_checks if c.name == "PII Detection" and c.status == CheckStatus.WARNING]
    if pii_warnings:
        recommendations.append(
            "Review flagged files for PII - anonymize or remove sensitive data before export"
        )

    # Check for raw data exposure
    data_fails = [c for c in report.data_checks if c.name == "Raw Data Exposure" and c.status == CheckStatus.FAIL]
    if data_fails:
        recommendations.append(
            "Remove raw data files from exports/ - only processed, anonymized data should be exported"
        )

    return recommendations


def generate_qc_report(project_path: Path, report: Optional[QCReport] = None) -> Path:
    """
    Generate and save a QC report.

    Args:
        project_path: Root path of the project
        report: Optional pre-generated report (will run checks if not provided)

    Returns:
        Path to the generated report file
    """
    if report is None:
        report = run_qc_checks(project_path)

    # Ensure reports directory exists
    reports_dir = Path(project_path) / "outputs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Generate markdown report
    md_content = _report_to_markdown(report)
    md_path = reports_dir / "qc_report.md"
    md_path.write_text(md_content)

    # Also save JSON for programmatic access
    json_path = reports_dir / "qc_report.json"
    json_path.write_text(json.dumps(report.to_dict(), indent=2))

    return md_path


def _report_to_markdown(report: QCReport) -> str:
    """Convert QCReport to markdown format."""
    status_icons = {
        CheckStatus.PASS: "PASS",
        CheckStatus.WARNING: "WARNING",
        CheckStatus.FAIL: "FAIL",
        CheckStatus.SKIPPED: "SKIPPED",
    }

    lines = [
        "# Quality Control Report",
        "",
        f"**Generated**: {report.generated_at}",
        f"**Project**: {report.project_name}",
        f"**Status**: {status_icons[report.overall_status]}",
        "",
    ]

    # Brand Compliance section
    if report.brand_checks:
        lines.extend([
            "## Brand Compliance",
            "",
            "| Check | Status | Details |",
            "|-------|--------|---------|",
        ])
        for check in report.brand_checks:
            status = status_icons[check.status]
            details = check.message
            if check.file_path:
                details += f" ({Path(check.file_path).name})"
            lines.append(f"| {check.name} | {status} | {details} |")
        lines.append("")

    # Chart Quality section
    if report.chart_checks:
        lines.extend([
            "## Chart Quality",
            "",
            "| File | Status | Issues |",
            "|------|--------|--------|",
        ])
        for check in report.chart_checks:
            status = status_icons[check.status]
            file_name = Path(check.file_path).name if check.file_path else check.name
            issues = check.message if check.status != CheckStatus.PASS else "-"
            lines.append(f"| {file_name} | {status} | {issues} |")
        lines.append("")

    # Data Compliance section
    if report.data_checks:
        lines.extend([
            "## Data Compliance",
            "",
            "| Check | Status | Details |",
            "|-------|--------|---------|",
        ])
        for check in report.data_checks:
            status = status_icons[check.status]
            lines.append(f"| {check.name} | {status} | {check.message} |")
        lines.append("")

    # Recommendations section
    if report.recommendations:
        lines.extend([
            "## Recommendations",
            "",
        ])
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "*This report was generated automatically by Kearney AI Coding Assistant QC.*",
        "*User is responsible for final review before client delivery.*",
    ])

    return "\n".join(lines)


def print_qc_summary(report: QCReport) -> None:
    """
    Print a summary of QC results to console.

    Args:
        report: QCReport to summarize
    """
    status_icons = {
        CheckStatus.PASS: "[PASS]",
        CheckStatus.WARNING: "[WARN]",
        CheckStatus.FAIL: "[FAIL]",
        CheckStatus.SKIPPED: "[SKIP]",
    }

    print("\n" + "=" * 60)
    print("  QUALITY CONTROL SUMMARY")
    print("=" * 60)
    print(f"\n  Project: {report.project_name}")
    print(f"  Overall Status: {status_icons[report.overall_status]}")
    print()

    all_checks = report.brand_checks + report.chart_checks + report.data_checks

    passes = sum(1 for c in all_checks if c.status == CheckStatus.PASS)
    warnings = sum(1 for c in all_checks if c.status == CheckStatus.WARNING)
    fails = sum(1 for c in all_checks if c.status == CheckStatus.FAIL)

    print(f"  Checks: {passes} passed, {warnings} warnings, {fails} failed")

    if fails > 0 or warnings > 0:
        print("\n  Issues:")
        for check in all_checks:
            if check.status in [CheckStatus.FAIL, CheckStatus.WARNING]:
                print(f"    {status_icons[check.status]} {check.name}: {check.message}")

    if report.recommendations:
        print("\n  Recommendations:")
        for rec in report.recommendations:
            print(f"    - {rec}")

    print("\n" + "-" * 60 + "\n")


def get_human_approval_warning(deliverables: List[str]) -> str:
    """
    Generate human approval warning message.

    Args:
        deliverables: List of deliverable file names

    Returns:
        Warning message string
    """
    deliverable_list = "\n".join(f"  - {d}" for d in deliverables)

    return f"""
============================================================
                 HUMAN REVIEW REQUIRED
============================================================

These deliverables will be generated:

{deliverable_list}

  YOU are responsible for reviewing these outputs
  before sending to the client.

Automated checks passed, but human judgment required for:
  - Content accuracy
  - Appropriate messaging
  - Client-specific sensitivities

============================================================
"""


def get_post_export_checklist() -> str:
    """
    Get the post-export review checklist.

    Returns:
        Checklist message string
    """
    return """
Exports created in: exports/

BEFORE SENDING TO CLIENT:
[ ] Review all content for accuracy
[ ] Check messaging aligns with client expectations
[ ] Verify no sensitive data exposed
[ ] Confirm brand compliance

Your signature: _____________ Date: _____________
"""
