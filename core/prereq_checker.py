# core/prereq_checker.py
"""
Prerequisite checker for Kearney AI Coding Assistant.
Run before project scaffolding to ensure environment is ready.

Usage:
    from core.prereq_checker import run_all_checks, print_results

    all_passed, results = run_all_checks(template_path)
    print_results(results)
"""

import sys
import shutil
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass
class CheckResult:
    """Result of a single prerequisite check."""
    name: str
    passed: bool
    message: str
    fix_instructions: Optional[str] = None


def check_python_version() -> CheckResult:
    """Check Python version is 3.10+."""
    version = sys.version_info
    # Use tuple indexing for compatibility with mocks
    major, minor = version[0], version[1]
    micro = version[2] if len(version) > 2 else 0
    passed = major == 3 and minor >= 10

    if passed:
        return CheckResult(
            name="Python Version",
            passed=True,
            message=f"Python {major}.{minor}.{micro}"
        )
    else:
        return CheckResult(
            name="Python Version",
            passed=False,
            message=f"Python {major}.{minor} found, need 3.10+",
            fix_instructions=(
                "Install Python 3.10+ from Kearney Software Center:\n"
                "  1. Open Software Center\n"
                "  2. Search for 'Python'\n"
                "  3. Install Python 3.11 or later\n"
                "  4. Restart your terminal"
            )
        )


def check_git_installed() -> CheckResult:
    """Check Git is installed."""
    git_path = shutil.which("git")

    if git_path:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            version = result.stdout.strip()
            return CheckResult(
                name="Git",
                passed=True,
                message=version
            )
        except (subprocess.TimeoutExpired, Exception):
            pass

    return CheckResult(
        name="Git",
        passed=False,
        message="Git not found",
        fix_instructions=(
            "Install Git from Kearney Software Center:\n"
            "  1. Open Software Center\n"
            "  2. Search for 'Git'\n"
            "  3. Install Git for Windows\n"
            "  4. Restart your terminal"
        )
    )


def check_claude_desktop() -> CheckResult:
    """Check Claude Desktop is installed."""
    # Check common installation paths
    possible_paths = [
        Path.home() / "AppData/Local/Programs/Claude/Claude.exe",  # Windows
        Path("/Applications/Claude.app"),  # macOS
        Path.home() / ".local/share/Claude/claude",  # Linux
    ]

    found = any(p.exists() for p in possible_paths)

    if found:
        return CheckResult(
            name="Claude Desktop",
            passed=True,
            message="Claude Desktop installed"
        )
    else:
        return CheckResult(
            name="Claude Desktop",
            passed=False,
            message="Claude Desktop not found",
            fix_instructions=(
                "Install Claude Desktop:\n"
                "  1. Request access from D&A Leadership\n"
                "  2. Once approved, download from claude.ai/download\n"
                "  3. Install and sign in with your Kearney credentials"
            )
        )


def check_required_packages() -> CheckResult:
    """Check required Python packages are available."""
    required = {
        "pandas": "pandas",
        "matplotlib": "matplotlib",
        "pptx": "python-pptx",
        "yaml": "pyyaml",
        "PIL": "pillow",
    }
    missing = []

    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if not missing:
        return CheckResult(
            name="Python Packages",
            passed=True,
            message="All required packages installed"
        )
    else:
        return CheckResult(
            name="Python Packages",
            passed=False,
            message=f"Missing packages: {', '.join(missing)}",
            fix_instructions=(
                "Run the bootstrap script to install packages:\n"
                f"  pip install {' '.join(missing)}\n"
                "Or use the bootstrap scripts:\n"
                "  Windows: Double-click bootstrap/setup_windows.bat\n"
                "  macOS:   Run ./bootstrap/setup_mac.sh"
            )
        )


def check_template_version(template_path: Path) -> CheckResult:
    """Check template is present and get version."""
    template_path = Path(template_path)
    version_file = template_path / "VERSION"

    if not template_path.exists():
        return CheckResult(
            name="Template",
            passed=False,
            message=f"Template not found at {template_path}",
            fix_instructions=(
                "Clone the template repository:\n"
                "  git clone https://github.kearney.com/digital-analytics/kearney-ai-coding-assistant.git ~/kaca-template"
            )
        )

    if version_file.exists():
        version = version_file.read_text().strip()
        return CheckResult(
            name="Template",
            passed=True,
            message=f"Template v{version}"
        )
    else:
        return CheckResult(
            name="Template",
            passed=True,
            message="Template found (version unknown)"
        )


def run_all_checks(template_path: Path) -> Tuple[bool, List[CheckResult]]:
    """
    Run all prerequisite checks.

    Args:
        template_path: Path to the KACA template directory.

    Returns:
        Tuple of (all_passed, list of CheckResult).
    """
    checks = [
        check_python_version(),
        check_git_installed(),
        check_claude_desktop(),
        check_required_packages(),
        check_template_version(template_path),
    ]

    all_passed = all(c.passed for c in checks)
    return all_passed, checks


def print_results(results: List[CheckResult]) -> None:
    """Print check results in a readable format."""
    print("\n" + "=" * 60)
    print("  KEARNEY AI CODING ASSISTANT - PREREQUISITE CHECK")
    print("=" * 60 + "\n")

    for result in results:
        status = "[PASS]" if result.passed else "[FAIL]"
        print(f"  {status} {result.name}: {result.message}")

    print("\n" + "-" * 60)

    failed = [r for r in results if not r.passed]
    if failed:
        print("\n  ACTION REQUIRED:\n")
        for result in failed:
            print(f"  {result.name}:")
            if result.fix_instructions:
                for line in result.fix_instructions.split("\n"):
                    print(f"    {line}")
            print()
    else:
        print("\n  All checks passed! Ready to create projects.\n")


def main():
    """CLI entry point for prereq_checker."""
    template_path = Path(__file__).parent.parent
    all_passed, results = run_all_checks(template_path)
    print_results(results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
