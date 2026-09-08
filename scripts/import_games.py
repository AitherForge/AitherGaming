import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
DRIVE = Path(sys.argv[1])
UGS = Path(sys.argv[2])
EAGLERCRAFT = Path(sys.argv[3])
AA = Path(sys.argv[4])
OUT = ROOT / "games"
AI_PREFIX = "ai-"
MAX_FILE_BYTES = 90 * 1024 * 1024


def discover_game_roots(root: Path):
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
    try:
        for file in root.rglob("*"):
            if file.is_file() and file.stat().st_size > MAX_FILE_BYTES:
                return False
    except OSError:
        return False
    return True


def collect(roots, source, used_slugs, used_names, limit=None):
    selected = []
    for source_root in roots:
        name = source_root.name.strip()
        slug = slugify(name)
        normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        if not slug or not normalized_name or slug in used_slugs or normalized_name in used_names:
            continue
        selected.append((name, slug, source, source_root))
        used_slugs.add(slug)
        used_names.add(normalized_name)
        if limit and len(selected) >= limit:
            break
    return selected


# Preserve Aither AI Originals across every external refresh.
ai_backup = ROOT / ".ai-games-backup"
if ai_backup.exists():
    shutil.rmtree(ai_backup)
if OUT.exists():
    for child in OUT.iterdir():
        if child.is_dir() and child.name.startswith(AI_PREFIX):
            ai_backup.mkdir(exist_ok=True)
            shutil.copytree(child, ai_backup / child.name)

# Drive contributes exactly 100 usable games; GitHub collections contribute every usable game.
drive_roots = [root for root in discover_game_roots(DRIVE) if is_probable_local_game(root)]
ugs_roots = [root for root in discover_game_roots(UGS) if is_probable_local_game(root)]
eagler_roots = [root for root in discover_game_roots(EAGLERCRAFT) if is_probable_local_game(root)]
aa_roots = [root for root in discover_game_roots(AA) if is_probable_local_game(root)]

print(f"UGS Google Drive usable games: {len(drive_roots)}")
print(f"UGS-Assets usable GitHub games: {len(ugs_roots)}")
print(f"Eaglercraft Extras usable GitHub games: {len(eagler_roots)}")
print(f"AA Gamerz usable GitHub games: {len(aa_roots)}")

used_slugs = set()
used_names = set()
selected = []

drive_selected = collect(drive_roots, "UGS Google Drive", used_slugs, used_names, limit=100)
if len(drive_selected) < 100:
    raise SystemExit(f"UGS Google Drive only provided {len(drive_selected)} usable games; 100 are required.")
selected.extend(drive_selected)
selected.extend(collect(ugs_roots, "UGS-Assets", used_slugs, used_names))
selected.extend(collect(eagler_roots, "Eaglercraft Extras", used_slugs, used_names))
selected.extend(collect(aa_roots, "AA Gamerz", used_slugs, used_names))

if not selected:
    raise SystemExit("No usable external game folders were found.")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

icons = ["🎮", "🕹️", "⭐", "🔥", "🚀", "🏆", "⚡", "🎯", "🧩", "👾"]
metadata = []
credits = [
    "# Aither Gaming Credits",
    "",
    "External games are imported as local files for the Aither Gaming library. Source attribution is retained here.",
    "",
]
source_counts = {}

for i, (name, slug, source, source_root) in enumerate(selected, 1):
    destination = OUT / slug
    shutil.copytree(source_root, destination, symlinks=True)
    entry = destination / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        raise SystemExit(f"Invalid local game entry point after copying: {name}")
    metadata.append({
        "name": name,
        "icon": icons[(i - 1) % len(icons)],
        "category": "UGS Google Drive" if source == "UGS Google Drive" else "GitHub Collections",
        "source": source,
        "path": f"games/{slug}",
    })
    source_counts[source] = source_counts.get(source, 0) + 1
    credits.append(f"- {name} — {source}")

# Restore Aither AI Originals.
ai_count = 0
if ai_backup.exists():
    for child in sorted(ai_backup.iterdir()):
        if child.is_dir() and child.name.startswith(AI_PREFIX) and (child / "index.html").is_file():
            shutil.copytree(child, OUT / child.name)
            metadata.append({
                "name": child.name[3:].replace("-", " ").title(),
                "icon": "🤖",
                "category": "AI Originals",
                "source": "Aither Gaming",
                "path": f"games/{child.name}",
            })
            ai_count += 1
            credits.append(f"- {child.name[3:].replace('-', ' ').title()} — Aither AI Original")
    shutil.rmtree(ai_backup)

credits.extend(["", "## Imported totals", ""])
for source, count in source_counts.items():
    credits.append(f"- {source}: {count} playable game folders")
credits.append(f"- Aither AI Originals: {ai_count}")

(ROOT / "games.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
print(f"Imported {len(selected)} external game folders + {ai_count} Aither AI Originals")
for source, count in source_counts.items():
    print(f"  {source}: {count}")
