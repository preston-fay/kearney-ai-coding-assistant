# core/streamlit_utils.py
"""
Utilities for Streamlit app deployment and management.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple
import socket


def is_port_in_use(port: int) -> bool:
    """Check if a port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def find_available_port(start_port: int = 8501, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port."""
    for i in range(max_attempts):
        port = start_port + i
        if not is_port_in_use(port):
            return port
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")


def kill_streamlit_on_port(port: int) -> bool:
    """Kill any process using the specified port. Returns True if killed."""
    try:
        if sys.platform == "win32":
            # Windows
            result = subprocess.run(
                f"netstat -ano | findstr :{port}",
                shell=True, capture_output=True, text=True
            )
            # Parse PID and kill - simplified, may need refinement
            return False  # Windows implementation TODO
        else:
            # Unix/Mac
            result = subprocess.run(
                f"lsof -ti:{port} | xargs kill -9 2>/dev/null",
                shell=True, capture_output=True
            )
            return result.returncode == 0
    except Exception:
        return False


def install_requirements(requirements_path: Path, quiet: bool = True) -> bool:
    """
    Install dependencies from requirements.txt.

    Returns True if successful.
    """
    if not requirements_path.exists():
        return False

    cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)]
    if quiet:
        cmd.append("-q")

    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


def verify_imports(modules: List[str]) -> Tuple[bool, List[str]]:
    """
    Verify that required modules can be imported.

    Returns (success, list_of_missing_modules)
    """
    missing = []
    for module in modules:
        try:
            __import__(module.split('.')[0])  # Handle submodules
        except ImportError:
            missing.append(module)

    return len(missing) == 0, missing


def launch_streamlit(
    app_path: Path,
    port: int = 8501,
    auto_kill: bool = True,
    install_deps: bool = True,
    headless: bool = True
) -> Tuple[bool, str]:
    """
    Launch a Streamlit app with pre-flight checks.

    Args:
        app_path: Path to the Streamlit app.py
        port: Port to run on
        auto_kill: Kill existing process on port first
        install_deps: Install requirements.txt if present
        headless: Run in headless mode

    Returns:
        (success, message)
    """
    app_path = Path(app_path)

    if not app_path.exists():
        return False, f"App not found: {app_path}"

    # Install dependencies if requirements.txt exists
    if install_deps:
        req_path = app_path.parent / "requirements.txt"
        if req_path.exists():
            print("Installing dependencies...")
            if not install_requirements(req_path):
                return False, "Failed to install dependencies"

    # Verify core imports
    success, missing = verify_imports(["streamlit", "pandas", "plotly"])
    if not success:
        return False, f"Missing required modules: {missing}"

    # Handle port conflict
    if is_port_in_use(port):
        if auto_kill:
            print(f"Port {port} in use, killing existing process...")
            kill_streamlit_on_port(port)
            time.sleep(2)
        else:
            port = find_available_port(port)
            print(f"Port in use, switching to {port}")

    # Build command
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(app_path),
        f"--server.port={port}"
    ]
    if headless:
        cmd.append("--server.headless=true")

    # Launch
    print(f"Launching Streamlit on port {port}...")
    subprocess.Popen(cmd)

    # Wait and verify
    time.sleep(3)
    if is_port_in_use(port):
        return True, f"Dashboard running at http://localhost:{port}"
    else:
        return False, "Failed to start Streamlit"


# Standard Streamlit tier dependencies
STREAMLIT_CORE_DEPS = [
    "streamlit>=1.28.0",
    "pandas>=2.0.0",
    "plotly>=5.18.0",
    "numpy>=1.24.0",
]

STREAMLIT_VIZ_DEPS = [
    "seaborn>=0.13.0",
    "matplotlib>=3.7.0",
]

STREAMLIT_ALL_DEPS = STREAMLIT_CORE_DEPS + STREAMLIT_VIZ_DEPS


def generate_requirements(
    include_viz: bool = True,
    extra_deps: Optional[List[str]] = None
) -> str:
    """Generate requirements.txt content for Streamlit apps."""
    deps = STREAMLIT_CORE_DEPS.copy()
    if include_viz:
        deps.extend(STREAMLIT_VIZ_DEPS)
    if extra_deps:
        deps.extend(extra_deps)
    return "\n".join(deps)
