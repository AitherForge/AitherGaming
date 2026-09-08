import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
AA = Path(sys.argv[1])
UGS = Path(sys.argv[2])
OUT = ROOT / "games"

# Keep individual files comfortably below GitHub's 100 MiB hard limit.
MAX_FILE_BYTES = 90 * 1024 * 1024


def discover_game_roots(root: Path):
    """Find top-level playable game roots without selecting nested asset copies."""
    candidates = []
    for index in root.rglob("index.html"):
        parent = index.parent.resolve()
        if ".git" in parent.parts:
            continue
        candidates.append(parent)

    unique = sorted(set(candidates), key=lambda p: (len(p.parts), str(p).lower()))
    roots = []
    for candidate in unique:
        if any(parent == candidate or candidate.is_relative_to(parent) for parent in roots):
            continue
        roots.append(candidate)
    return sorted(roots, key=lambda p: str(p).lower())


def slugify(name: str):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def is_probable_local_game(root: Path):
    """Accept real local games and reject obvious external iframe wrappers."""
    entry = root / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        return False

    try:
        html = entry.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False

    if "<iframe" in html and "src=" in html:
        iframe_srcs = re.findall(r"<iframe[^>]+src=[\"']([^\"']+)", html)
        if any(src.startswith(("http://", "https://", "//")) for src in iframe_srcs):
            return False

    # Avoid selecting repositories whose playable entry depends on a giant
    # binary that GitHub will reject during the eventual push.
    try:
        for file in root.rglob("*"):
            if file.is_file() and file.stat().st_size > MAX_FILE_BYTES:
                return False
    except OSError:
        return False

    return True


aa = discover_game_roots(AA)
ugs = discover_game_roots(UGS)
print(f"AA Gamerz discovered roots: {len(aa)}")
print(f"UGS discovered roots: {len(ugs)}")

aa_valid = [root for root in aa if is_probable_local_game(root)]
ugs_valid = [root for root in ugs if is_probable_local_game(root)]
print(f"AA Gamerz local playable roots: {len(aa_valid)}")
print(f"UGS local playable roots: {len(ugs_valid)}")

selected = []
used_slugs = set()
used_names = set()

# Prefer AA Gamerz when it contains usable local games, then fill from UGS.
for source, roots in (("AA Gamerz", aa_valid), ("UGS", ugs_valid)):
    for source_root in roots:
        if len(selected) >= 100:
            break

        name = source_root.name.strip()
        slug = slugify(name)
        normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        if not slug or not normalized_name:
            continue
        if slug in used_slugs or normalized_name in used_names:
            continue
        if not (source_root / "index.html").is_file():
            continue

        selected.append((name, slug, source, source_root))
        used_slugs.add(slug)
        used_names.add(normalized_name)

if len(selected) < 100:
    raise SystemExit(
        f"Need 100 local playable games, but found only {len(selected)} "
        f"({len(aa_valid)} from AA Gamerz and {len(ugs_valid)} from UGS)"
    )

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

icons = ["🎮", "🕹️", "⭐", "🔥", "🚀", "🏆", "⚡", "🎯", "🧩", "👾"]
metadata = []
credits = [
    "# Aither Gaming Credits",
    "",
    "The games below are bundled as local source files. Original attribution is retained by source collection.",
    "",
]

for i, (name, slug, source, source_root) in enumerate(selected, 1):
    destination = OUT / slug
    shutil.copytree(source_root, destination, symlinks=True)

    entry = destination / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        raise SystemExit(f"Invalid local game entry point after copying: {name}")

    metadata.append({
        "name": name,
        "icon": icons[(i - 1) % len(icons)],
        "category": "Games",
        "path": f"games/{slug}",
    })
    credits.append(f"- {name} — {source}")

(ROOT / "games.json").write_text(
    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

# app.js is maintained separately because it contains the Aither Account
# integration. Never regenerate or stage it from this importer.
(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")

print(f"Imported {len(selected)} complete local game folders")
