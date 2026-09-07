import os, re, shutil, sys, json, unicodedata
from pathlib import Path

ROOT=Path.cwd()
AA=Path(sys.argv[1]); UGS=Path(sys.argv[2])
text=(ROOT/'app.js').read_text(encoding='utf-8')
pattern=re.compile(r"\{name:'([^']+)',icon:'([^']*)',category:'([^']+)',(path|ugs):'((?:\\'|[^'])*)'\}")
games=[]
for m in pattern.finditer(text):
    source=m.group(4); value=m.group(5).replace("\\'", "'")
    games.append({'name':m.group(1),'icon':m.group(2),'category':m.group(3),'kind':'AA' if source=='path' else 'UGS','source':value})
if len(games)!=100:
    raise SystemExit(f'Expected 100 games in launcher manifest, found {len(games)}')

def norm(s):
    s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+','',s)

def find_dir(root, wanted):
    n=norm(wanted)
    direct=root/wanted
    if direct.is_dir(): return direct
    for p in root.iterdir():
        if p.is_dir() and norm(p.name)==n: return p
    matches=[]
    for p in root.rglob('*'):
        if p.is_dir() and norm(p.name)==n: matches.append(p)
    return matches[0] if matches else None

out=ROOT/'games'; out.mkdir(exist_ok=True)
for item in games:
    dest=out/re.sub(r'[^a-z0-9]+','-',item['name'].lower()).strip('-')
    if dest.exists(): shutil.rmtree(dest)
    src=(AA/item['source']) if item['kind']=='AA' else find_dir(UGS,item['source'])
    if not src or not src.is_dir():
        raise SystemExit(f"Could not locate source for {item['name']}: {item['source']}")
    shutil.copytree(src,dest)
    # If the source has its HTML entry one level deeper, promote that web root.
    if not (dest/'index.html').exists():
        indexes=list(dest.rglob('index.html'))
        if indexes:
            webroot=indexes[0].parent
            for child in list(webroot.iterdir()):
                target=dest/child.name
                if target.exists():
                    if target.is_dir(): shutil.copytree(child,target,dirs_exist_ok=True)
                else: shutil.copytree(child,target) if child.is_dir() else shutil.copy2(child,target)
    item['path']=f"games/{dest.name}"

(ROOT/'games.json').write_text(json.dumps([{'name':g['name'],'icon':g['icon'],'category':g['category'],'path':g['path']} for g in games],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

launcher='''const games=GAME_DATA;\nconst grid=document.getElementById("gameGrid"),search=document.getElementById("search"),count=document.getElementById("count"),filters=document.getElementById("filters");\nlet active="All";\nconst categories=["All",...new Set(games.map(g=>g.category))];\nfilters.innerHTML=categories.map(c=>`<button class="chip ${c==="All"?"active":""}" data-category="${c}">${c}</button>`).join("");\nfilters.addEventListener("click",e=>{const b=e.target.closest(".chip");if(!b)return;active=b.dataset.category;document.querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===b));render()});\nsearch.addEventListener("input",render);\nfunction render(){const q=search.value.trim().toLowerCase();const visible=games.filter(g=>(active==="All"||g.category===active)&&(!q||`${g.name} ${g.category}`.toLowerCase().includes(q)));count.textContent=`${visible.length} games ready to play`;grid.innerHTML=visible.length?visible.map(g=>`<a class="game-card" href="${g.path}/"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category}</p><span class="play">Play game →</span></a>`).join(""):"<div class=\"game-card\" style=\"grid-column:1/-1;text-align:center\"><h3>No games found</h3><p>Try another search or category.</p></div>"}\nconst themeButton=document.getElementById("themeButton"),saved=localStorage.getItem("aither-theme");if(saved==="light")document.body.classList.add("light");themeButton.onclick=()=>{document.body.classList.toggle("light");localStorage.setItem("aither-theme",document.body.classList.contains("light")?"light":"dark")};render();\n'''
# Keep game data separate so app.js contains no external game URLs.
(ROOT/'app.js').write_text(launcher.replace('GAME_DATA',json.dumps([{'name':g['name'],'icon':g['icon'],'category':g['category'],'path':g['path']} for g in games],ensure_ascii=False)),encoding='utf-8')

credits=['# Aither Gaming Credits','', 'Aither Gaming bundles the game source files into individual folders under `games/`.','', 'Credit is retained for the original projects as requested by their published terms.','']
for g in games: credits.append(f"- {g['name']}")
(ROOT/'CREDITS.md').write_text('\n'.join(credits)+'\n',encoding='utf-8')

# Remove external source/game launch sections from the launcher UI.
idx=ROOT/'index.html'; html=idx.read_text(encoding='utf-8')
html=re.sub(r'<nav>.*?</nav>', '<nav><a href="#games">Games</a></nav>', html, flags=re.S)
html=re.sub(r'<section id="minecraft".*?</section>', '', html, flags=re.S)
html=re.sub(r'<section id="sources".*?</section>', '<section class="feature-section"><div class="section-heading"><div><p class="eyebrow">AITHER GAMING</p><h2>100 local games</h2></div></div><p class="muted">Every game in the library is stored in its own folder inside <code>games/</code>.</p><a class="secondary" href="CREDITS.md">View credits</a></section>', html, flags=re.S)
idx.write_text(html,encoding='utf-8')

readme='''# Aither Gaming\n\nAither Gaming is a mobile-friendly browser game hub with **100 locally stored games**.\n\n## Local game structure\n\nEvery game is imported as its own directory under `games/`, with its original HTML, JavaScript, CSS, images, audio, and other game assets preserved. The launcher opens only local `games/<game>/` paths.\n\nThe import workflow pulls the selected game source files from the supplied collections and commits them into this repository. No external game URL is used by the launcher.\n\n## Credits\n\nOriginal project credit is retained in `CREDITS.md`.\n\n## GitHub Pages\n\nEnable **Settings → Pages → Deploy from a branch → main → / (root)**.\n'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
print(f'Imported {len(games)} games')
