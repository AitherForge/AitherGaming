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
    # Skip simple iframe wrappers that only embed a remote game.
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


def collect_all(roots, source, used_slugs, used_names):
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

ugs_roots = [root for root in discover_game_roots(UGS) if is_probable_local_game(root)]
eagler_roots = [root for root in discover_game_roots(EAGLERCRAFT) if is_probable_local_game(root)]
aa_roots = [root for root in discover_game_roots(AA) if is_probable_local_game(root)]

print(f"UGS-Assets usable local games: {len(ugs_roots)}")
print(f"Eaglercraft Extras usable local games: {len(eagler_roots)}")
print(f"AA Gamerz usable local games: {len(aa_roots)}")

used_slugs = set()
used_names = set()
selected = []
selected.extend(collect_all(ugs_roots, "UGS-Assets", used_slugs, used_names))
selected.extend(collect_all(eagler_roots, "Eaglercraft Extras", used_slugs, used_names))
selected.extend(collect_all(aa_roots, "AA Gamerz", used_slugs, used_names))

if not selected:
    raise SystemExit("No usable GitHub game folders were found.")

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

icons = ["🎮", "🕹️", "⭐", "🔥", "🚀", "🏆", "⚡", "🎯", "🧩", "👾"]
metadata = []
credits = [
    "# Aither Gaming Credits",
    "",
    "Games are imported from public GitHub repositories as local files. Source attribution is retained here.",
    "",
]

source_counts = {}
for i, (name, slug, source, source_root) in enumerate(selected, 1):
    destination = OUT / slug
    shutil.copytree(source_root, destination, symlinks=True)
    entry = destination / "index.html"
    if not entry.is_file() or entry.stat().st_size == 0:
        raise SystemExit(f"Invalid local game entry point after copying: {name}")
    category = "UGS-Assets" if source == "UGS-Assets" else "GitHub"
    metadata.append({
        "name": name,
        "icon": icons[(i - 1) % len(icons)],
        "category": category,
        "source": source,
        "path": f"games/{slug}",
    })
    source_counts[source] = source_counts.get(source, 0) + 1
    credits.append(f"- {name} — {source}")

# Restore Aither AI Originals after the complete GitHub collection is rebuilt.
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

credits.extend([
    "",
    "## Imported totals",
    "",
])
for source, count in source_counts.items():
    credits.append(f"- {source}: {count} playable game folders")
credits.append(f"- Aither AI Originals: {ai_count}")

(ROOT / "games.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")
print(f"Imported {len(selected)} GitHub game folders + {ai_count} Aither AI Originals")
for source, count in source_counts.items():
    print(f"  {source}: {count}")
