import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path.cwd()
UGS = Path(sys.argv[1])
EAGLERCRAFT = Path(sys.argv[2])
AA = Path(sys.argv[3])
OUT = ROOT / "games"
AI_PREFIX = "ai-"
MAX_FILE_BYTES = 90 * 1024 * 1024
UGS_TARGET = 170
GITHUB_TARGET = 30


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


def add_candidates(selected, roots, source, target, used_slugs, used_names):
    for source_root in roots:
        if len(selected) >= target:
            break
        name = source_root.name.strip()
        slug = slugify(name)
        normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        if not slug or not normalized_name or slug in used_slugs or normalized_name in used_names:
            continue
        selected.append((name, slug, source, source_root))
        used_slugs.add(slug)
        used_names.add(normalized_name)


# Preserve Aither AI Originals across every external refresh.
ai_backup = ROOT / ".ai-games-backup"
if ai_backup.exists():
    shutil.rmtree(ai_backup)
if OUT.exists():
    for child in OUT.iterdir():
        if child.is_dir() and child.name.startswith(AI_PREFIX):
            ai_backup.mkdir(exist_ok=True)
            shutil.copytree(child, ai_backup / child.name)

ugs_roots = [root for root in discover_game_roots(UGS) if is_probable_local_game(root)]
eagler_roots = [root for root in discover_game_roots(EAGLERCRAFT) if is_probable_local_game(root)]
aa_roots = [root for root in discover_game_roots(AA) if is_probable_local_game(root)]

print(f"UGS usable local games: {len(ugs_roots)}")
print(f"Eaglercraft Extras usable local games: {len(eagler_roots)}")
print(f"AA Gamerz usable local games: {len(aa_roots)}")

used_slugs = set()
used_names = set()
ugs_selected = []
github_selected = []

add_candidates(ugs_selected, ugs_roots, "UGS Google Drive", UGS_TARGET, used_slugs, used_names)

# The 30 GitHub games are selected from both supplied repositories, preferring
# Eaglercraft Extras first and then AA Gamerz, while removing duplicates.
add_candidates(github_selected, eagler_roots, "Eaglercraft Extras", GITHUB_TARGET, used_slugs, used_names)
if len(github_selected) < GITHUB_TARGET:
    add_candidates(github_selected, aa_roots, "AA Gamerz", GITHUB_TARGET, used_slugs, used_names)

if len(ugs_selected) < UGS_TARGET:
    raise SystemExit(f"Need {UGS_TARGET} UGS games, but found only {len(ugs_selected)}")
if len(github_selected) < GITHUB_TARGET:
    raise SystemExit(f"Need {GITHUB_TARGET} GitHub games, but found only {len(github_selected)} across Eaglercraft Extras and AA Gamerz")

selected = ugs_selected + github_selected

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

icons = ["🎮", "🕹️", "⭐", "🔥", "🚀", "🏆", "⚡", "🎯", "🧩", "👾"]
metadata = []
credits = [
    "# Aither Gaming Credits",
    "",
    "The imported games are bundled as local source files. Original attribution is retained by the source collections.",
    "",
]

for i, (name, slug, source, source_root) in enumerate(selected, 1):
    destination = OUT / slug
    shutil.copytree(source_root, destination, symlinks=True)
    entry = destination / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        raise SystemExit(f"Invalid local game entry point after copying: {name}")
    category = "UGS" if source == "UGS Google Drive" else "GitHub"
    metadata.append({
        "name": name,
        "icon": icons[(i - 1) % len(icons)],
        "category": category,
        "path": f"games/{slug}",
    })
    credits.append(f"- {name} — {source}")

# Restore Aither AI Originals after the 200-game external collection is rebuilt.
ai_count = 0
if ai_backup.exists():
    for child in sorted(ai_backup.iterdir()):
        if child.is_dir() and child.name.startswith(AI_PREFIX) and (child / "index.html").is_file():
            shutil.copytree(child, OUT / child.name)
            metadata.append({
                "name": child.name[3:].replace("-", " ").title(),
                "icon": "🤖",
                "category": "AI Originals",
                "path": f"games/{child.name}",
            })
            ai_count += 1
            credits.append(f"- {child.name[3:].replace('-', ' ').title()} — Aither AI Original")
    shutil.rmtree(ai_backup)

(ROOT / "games.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
print(f"Imported {len(ugs_selected)} UGS games + {len(github_selected)} GitHub games + {ai_count} Aither AI Originals")
