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

    # A source tree can contain nested demos/assets with their own index.html.
    # Keep the highest-level playable directory so the complete game stays together.
    unique = sorted(set(candidates), key=lambda p: (len(p.parts), str(p).lower()))
    roots = []
    for candidate in unique:
        if any(parent == candidate or candidate.is_relative_to(parent) for parent in roots):
            continue
        roots.append(candidate)
    return sorted(roots, key=lambda p: str(p).lower())


def slugify(name: str):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


aa = discover_game_roots(AA)
ugs = discover_game_roots(UGS)

if len(aa) < 10:
    raise SystemExit(f"Only found {len(aa)} playable AA Gamerz game roots; need at least 10")
if len(ugs) < 90:
    raise SystemExit(f"Only found {len(ugs)} playable UGS game roots; need at least 90")

selected = []
used_slugs = set()
used_names = set()

for source, roots, target in (("AA Gamerz", aa, 10), ("UGS", ugs, 90)):
    taken = 0
    for source_root in roots:
        name = source_root.name.strip()
        slug = slugify(name)
        normalized_name = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
        if not slug or not normalized_name or slug in used_slugs or normalized_name in used_names:
            continue
        if not (source_root / "index.html").is_file():
            continue
        selected.append((name, slug, source, source_root))
        used_slugs.add(slug)
        used_names.add(normalized_name)
        taken += 1
        if taken == target:
            break

if len(selected) != 100:
    raise SystemExit(f"Expected exactly 100 real games, discovered {len(selected)}")

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

    # Make sure each folder contains the actual source, not an external launcher/iframe.
    html = entry.read_text(encoding="utf-8", errors="ignore").lower()
    if "iframe" in html and "src=" in html and "games/" not in html:
        raise SystemExit(f"Refusing probable external wrapper instead of source: {name}")

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

(ROOT / "app.js").write_text(
    '''let games=[];\nconst grid=document.getElementById("gameGrid"),search=document.getElementById("search"),count=document.getElementById("count"),filters=document.getElementById("filters");\nlet active="All";\nasync function init(){games=await fetch("games.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error();return r.json()});filters.innerHTML='<button class="chip active" data-category="All">All</button>';filters.onclick=e=>{const b=e.target.closest(".chip");if(!b)return;active=b.dataset.category;document.querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===b));render()};search.oninput=render;render()}\nfunction render(){const q=search.value.trim().toLowerCase(),v=games.filter(g=>(active==="All"||g.category===active)&&(!q||g.name.toLowerCase().includes(q)));count.textContent=`${v.length} games ready to play`;grid.innerHTML=v.length?v.map(g=>`<a class="game-card" href="${g.path}/"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category}</p><span class="play">Play game →</span></a>`).join(""): '<div class="game-card" style="grid-column:1/-1;text-align:center"><h3>No games found</h3></div>'}\nconst themeButton=document.getElementById("themeButton"),saved=localStorage.getItem("aither-theme");if(saved==="light")document.body.classList.add("light");themeButton.onclick=()=>{document.body.classList.toggle("light");localStorage.setItem("aither-theme",document.body.classList.contains("light")?"light":"dark")};init().catch(()=>count.textContent="Game library failed to load");\n''',
    encoding="utf-8",
)

(ROOT / "CREDITS.md").write_text("\n".join(credits) + "\n", encoding="utf-8")

print(f"Imported {len(selected)} complete local game folders")
