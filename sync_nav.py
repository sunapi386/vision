#!/usr/bin/env python3
"""Sync the canonical site nav into every hand-authored essay.

templates/nav.html is the single source of truth. build.py already injects it
into the generated pages (book.html, index.html); the standalone essays used to
carry a hard-copied nav that drifted (missing pages, stale links). This script
replaces the <nav class="site-nav">...</nav> block in each essay with the
canonical nav, filling the per-page language toggle.

Run it after editing templates/nav.html. It is idempotent.

    python3 sync_nav.py
"""

import re
from pathlib import Path

VISION_DIR = Path(__file__).parent
NAV = (VISION_DIR / "templates" / "nav.html").read_text().strip()

# EN essays whose Chinese toggle points at a specific translation. EN essays not
# listed here point the toggle at the Chinese landing page (/index-zh.html).
EN_TO_ZH = {
    "compute.html": "/compute-zh.html",
    "lessons.html": "/lessons-zh.html",
    "research.html": "/research-zh.html",
    "vault.html": "/vault-zh.html",
}

# Chinese essays: the toggle points BACK to the English twin and reads "EN".
ZH_TO_EN = {
    "compute-zh.html": "/compute.html",
    "lessons-zh.html": "/lessons.html",
    "research-zh.html": "/research.html",
    "vault-zh.html": "/vault.html",
}

# Generated pages (build.py owns their nav) and pages excluded on purpose.
EXCLUDE = {"index.html", "book.html", "index-zh.html", "book-zh.html"}

NAV_BLOCK_RE = re.compile(r'<nav class="site-nav".*?</nav>', re.DOTALL)
LANG_LINK_RE = re.compile(r'<a href="/index-zh\.html" class="nav-link[^"]*">中文</a>')


def canonical_nav_for(filename: str) -> str:
    nav = NAV
    for ph in ("{nav_active_book}", "{nav_active_essay}", "{nav_active_zh}", "{nav_extra}"):
        nav = nav.replace(ph, "")
    # Collapse the doubled spaces left by empty active-class placeholders.
    nav = nav.replace('class="nav-link "', 'class="nav-link"')
    if filename in ZH_TO_EN:
        link = f'<a href="{ZH_TO_EN[filename]}" class="nav-link">EN</a>'
    else:
        href = EN_TO_ZH.get(filename, "/index-zh.html")
        link = f'<a href="{href}" class="nav-link">中文</a>'
    nav = LANG_LINK_RE.sub(link, nav)
    return nav


def main() -> None:
    changed, skipped = [], []
    for path in sorted(VISION_DIR.glob("*.html")):
        if path.name in EXCLUDE:
            continue
        html = path.read_text()
        if not NAV_BLOCK_RE.search(html):
            skipped.append(f"{path.name} (no site-nav)")
            continue
        new_html = NAV_BLOCK_RE.sub(lambda _: canonical_nav_for(path.name), html, count=1)
        if new_html != html:
            path.write_text(new_html)
            changed.append(path.name)
    print(f"synced {len(changed)} file(s): {', '.join(changed) or 'none'}")
    if skipped:
        print(f"skipped: {', '.join(skipped)}")


if __name__ == "__main__":
    main()
