import re
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path.cwd()
POSTS_DIR = REPO_ROOT / "_posts"

def slugify(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = s.strip("-")
    return (s[:60] if s else "post")

def build_post_path(title: str) -> Path:
    today = datetime.now().strftime('%Y-%m-%d')
    slug = slugify(title)
    return POSTS_DIR / f'{today}-{slug}.md'