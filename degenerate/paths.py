from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent  # degenerate/
ROOT = PACKAGE_DIR.parent                      # top level

OUTPUT_DIR = ROOT / "output"
LOGS_DIR = OUTPUT_DIR / "logs"
PAPERS_DIR = OUTPUT_DIR / "papers"
FAILED_DIR = OUTPUT_DIR / "failed"
GRAMMAR_DIR = PACKAGE_DIR / "grammar"
SITE_DIR = ROOT / "site"
