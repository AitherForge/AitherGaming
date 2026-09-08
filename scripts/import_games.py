import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
AA = Path(sys.argv[1])
UGS = Path(sys.argv[2])
OUT = ROOT / "games"


def discover_game_roots(root: Path):
    """Find real game roots by locating index.html files and removing nested duplicates."""
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
    """Reject obvious external iframe wrappers before selecting/copying them."""
    entry = root / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        return False
    html = entry.read_text(encoding="utf-8", errors="ignore").lower()
    if "<iframe" in html and "src=" in html:
        # A real local game can contain an iframe for an internal asset, but a
        # top-level wrapper pointing at another site is not a bundled game.
        iframe_srcs = re.findall(r"<iframe[^>]+src=[\"']([^\"']+)", html)
        if any(src.startswith(("http://", "https://", "//")) for src in iframe_srcs):
            return False
    return True


aa = discover_game_roots(AA)
ugs = discover_game_roots(UGS)
print(f"AA Gamerz discovered roots: {len(aa)}")
print(f"UGS discovered roots: {len(ugs)}")

# Filter invalid/external wrappers before choosing the 100 games.
aa_valid = [root for root in aa if is_probable_local_game(root)]
ugs_valid = [root for root in ugs if is_probable_local_game(root)]
print(f"AA Gamerz local playable roots: {len(aa_valid)}")
print(f"UGS local playable roots: {len(ugs_valid)}")

# Source collections can change. Never require an arbitrary per-source quota.
# Prefer AA Gamerz when available, then fill the remaining slots from UGS.
selected = []
used_slugs = set()
used_names = set()

for source, roots in (("AA Gamerz", aa_valid), ("UGS", ugs_valid)):
    for source_root in roots:
        if len(selected) >= 100:
            break
        name = source_root.name.strip()
        slug = slugify(name)
        normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        if not slug or not normalized_name or slug in used_slugs or normalized_name in used_names:
            continue
        selected.append((name, slug, source, source_root))
        used_slugs.add(slug)
        used_names.add(normalized_name)

if len(selected) < 100:
    raise SystemExit(
        f"Need 100 local playable game roots in total, but discovered only {len(selected)} "
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
# integration. The importer must never regenerate it and erase authentication.
(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")

print(f"Imported {len(selected)} complete local game folders")
