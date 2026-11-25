from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent  # degenerate/
ROOT = PACKAGE_DIR.parent                      # top level

LOGS_DIR = ROOT / "logs"
PAPERS_DIR = ROOT / "papers"
FAILED_DIR = ROOT / "failed"
GRAMMAR_DIR = PACKAGE_DIR / "grammar"
SITE_DIR = ROOT / "site"
