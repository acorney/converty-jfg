"""Startup dependency checks."""
import shutil
import subprocess
from pathlib import Path


def find_tesseract() -> tuple[bool, str]:
    """Return (found, version_or_error)."""
    exe = shutil.which("tesseract")
    if not exe:
        # Common install path on Windows
        fallback = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if Path(fallback).exists():
            exe = fallback
    if not exe:
        return False, "Tesseract not found on PATH."
    try:
        result = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=5
        )
        first_line = (result.stdout or result.stderr or "").splitlines()[0]
        version = first_line.strip()
        return True, version
    except Exception as e:
        return False, str(e)


def find_poppler(vendor_path: str | None = None) -> tuple[bool, str]:
    """Return (found, path_or_error). Checks vendor/ first, then PATH."""
    if vendor_path:
        pdftoppm = Path(vendor_path) / "pdftoppm.exe"
        if pdftoppm.exists():
            return True, str(Path(vendor_path))
    exe = shutil.which("pdftoppm")
    if exe:
        return True, str(Path(exe).parent)
    return False, "Poppler not found."
