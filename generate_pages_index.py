"""
Build the static site published to repo.bossanova808.net via GitHub Pages.

Publishes ONLY the repository.bossanova808 zip(s) - not the individual addon
zips - so this site is purely a way to get the repository addon installed via
Kodi's file manager. Every other addon (skins, scripts, etc.) is meant to be
browsed and installed the normal way, through "Install from repository" once
the repository addon itself is in place, not side-loaded directly from here.

Generates a plain Apache/nginx-autoindex-style index.html so Kodi's file
manager ("Add source" -> browse) can list and select the zip, the same way it
would against a real autoindex-enabled web server. Only used for the initial
"Install from zip" bootstrap step - the repository addon's own datadir/
checksum/info URLs stay pointed at raw.githubusercontent.com for ongoing
auto-updates, unaffected by this site.
"""

import html
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

SOURCE_DIR = Path("repository-downloads") / "repository.bossanova808"
SITE_DIR = Path("_site")
CUSTOM_DOMAIN = "repo.bossanova808.net"

INDEX_TEMPLATE = """<!DOCTYPE html>
<html>
<head><title>Index of /{rel_path}</title></head>
<body>
<h1>Index of /{rel_path}</h1>
<ul>
{entries}
</ul>
</body>
</html>
"""


def build_entries(directory: Path, is_root: bool) -> str:
    lines = []
    if not is_root:
        lines.append('<li><a href="../">../</a></li>')

    dirs = sorted(p for p in directory.iterdir() if p.is_dir())
    files = sorted(p for p in directory.iterdir() if p.is_file() and p.name != "index.html")

    for p in dirs:
        href, name = quote(p.name), html.escape(p.name)
        lines.append(f'<li><a href="{href}/">{name}/</a></li>')
    for p in files:
        href, name = quote(p.name), html.escape(p.name)
        lines.append(f'<li><a href="{href}">{name}</a></li>')

    return "\n".join(lines)


def write_indexes(root: Path) -> None:
    for directory in [root, *sorted(p for p in root.rglob("*") if p.is_dir())]:
        rel = directory.relative_to(root)
        rel_path = "" if rel == Path(".") else f"{rel}/"
        entries = build_entries(directory, is_root=(rel == Path(".")))
        (directory / "index.html").write_text(
            INDEX_TEMPLATE.format(rel_path=html.escape(rel_path), entries=entries),
            encoding="utf-8",
        )


def main() -> int:
    if not SOURCE_DIR.is_dir():
        print(f"Source directory not found: {SOURCE_DIR}", file=sys.stderr)
        return 1

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True)

    # only the zip(s) - not the loose resources/ folder (icon etc.), which
    # isn't needed for "Install from zip" and would just be extra clutter
    for zip_path in SOURCE_DIR.glob("*.zip"):
        shutil.copy2(zip_path, SITE_DIR / zip_path.name)

    write_indexes(SITE_DIR)

    (SITE_DIR / "CNAME").write_text(CUSTOM_DOMAIN + "\n", encoding="utf-8")

    print(f"Site built at {SITE_DIR}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
