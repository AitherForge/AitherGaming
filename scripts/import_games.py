import json
import re
import shutil
import sys
from pathlib import Path

ROOT=Path.cwd(); AA=Path(sys.argv[1]); UGS=Path(sys.argv[2]); OUT=ROOT/'games'

def discover(root):
    found=[]; seen=set()
    for index in root.rglob('index.html'):
        p=index.parent
        if '.git' in p.parts or p in seen: continue
        seen.add(p); found.append(p)
    return sorted(found,key=lambda p:str(p).lower())

aa=discover(AA); ugs=discover(UGS)
if len(aa)<10: raise SystemExit(f'Only found {len(aa)} playable AA Gamerz games')
if len(ugs)<90: raise SystemExit(f'Only found {len(ugs)} playable UGS games')
selected=[]; used=set()
for source,roots,target in [('AA Gamerz',aa,10),('UGS',ugs,90)]:
    for p in roots:
        name=p.name.strip(); slug=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
        if not slug or slug in used: continue
        used.add(slug); selected.append((name,slug,source,p))
        if sum(1 for x in selected if x[2]==source)>=target: break
if len(selected)!=100: raise SystemExit(f'Expected 100 games, discovered {len(selected)}')
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir(parents=True)
icons=['🎮','🕹️','⭐','🔥','🚀','🏆','⚡','🎯','🧩','👾']
metadata=[]
for i,(name,slug,source,src) in enumerate(selected,1):
    dest=OUT/slug; shutil.copytree(src,dest)
    if not (dest/'index.html').exists():
        raise SystemExit(f'No root index.html after copying {name}')
    metadata.append({'name':name,'icon':icons[(i-1)%len(icons)],'category':'Games','path':f'games/{slug}'})
(ROOT/'games.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(ROOT/'app.js').write_text(r'''let games=[];
const grid=document.getElementById("gameGrid"),search=document.getElementById("search"),count=document.getElementById("count"),filters=document.getElementById("filters");
let active="All";
async function init(){games=await fetch("games.json",{cache:"no-store"}).then(r=>{if(!r.ok)throw Error();return r.json()});filters.innerHTML='<button class="chip active" data-category="All">All</button>';filters.onclick=e=>{const b=e.target.closest(".chip");if(!b)return;active=b.dataset.category;document.querySelectorAll(".chip").forEach(x=>x.classList.toggle("active",x===b));render()};search.oninput=render;render()}
function render(){const q=search.value.trim().toLowerCase(),v=games.filter(g=>(active==="All"||g.category===active)&&(!q||g.name.toLowerCase().includes(q)));count.textContent=`${v.length} games ready to play`;grid.innerHTML=v.length?v.map(g=>`<a class="game-card" href="${g.path}/"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category}</p><span class="play">Play game →</span></a>`).join(""): '<div class="game-card" style="grid-column:1/-1;text-align:center"><h3>No games found</h3></div>'}
const themeButton=document.getElementById("themeButton"),saved=localStorage.getItem("aither-theme");if(saved==="light")document.body.classList.add("light");themeButton.onclick=()=>{document.body.classList.toggle("light");localStorage.setItem("aither-theme",document.body.classList.contains("light")?"light":"dark")};init().catch(()=>count.textContent="Game library failed to load");
''',encoding='utf-8')
credits=['# Aither Gaming Credits','','The bundled games retain original attribution.','']+[f'- {n} — {s}' for n,sl,s,p in selected]
(ROOT/'CREDITS.md').write_text('\n'.join(credits)+'\n',encoding='utf-8')
print(f'Imported {len(selected)} complete local game folders')
