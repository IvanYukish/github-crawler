import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_PATH = os.path.join(BASE_DIR, "app/data")
