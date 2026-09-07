const games=[
 {name:'Candy Crush',icon:'🍬',category:'Puzzle',source:'AA Gamerz',path:'01-Candy-Crush-Game'},
 {name:'Archery',icon:'🏹',category:'Action',source:'AA Gamerz',path:'02-Archery-Game'},
 {name:'Minesweeper',icon:'💣',category:'Puzzle',source:'AA Gamerz',path:'05-Minesweeper-Game'},
 {name:'Tower Blocks',icon:'🏗️',category:'Arcade',source:'AA Gamerz',path:'06-Tower-Blocks'},
 {name:'Tetris',icon:'🟦',category:'Puzzle',source:'AA Gamerz',path:'08-Tetris-Game'},
 {name:'Tilting Maze',icon:'🌀',category:'Puzzle',source:'AA Gamerz',path:'09-Tilting-Maze-Game'},
 {name:'Rock Paper Scissors',icon:'✊',category:'Party',source:'AA Gamerz',path:'11-Rock-Paper-Scissors'},
 {name:'Number Guessing',icon:'🔢',category:'Puzzle',source:'AA Gamerz',path:'12-Type-Number-Guessing-Game'},
 {name:'Connect Four',icon:'🔴',category:'Board',source:'AA Gamerz',path:'15-Connect-Four-Game'},
 {name:'Hangman',icon:'🔤',category:'Word',source:'AA Gamerz',path:'18-Hangman-Game'},
 {name:'Crossy Road',icon:'🐔',category:'Arcade',source:'AA Gamerz',path:'20-Crossy-Road-Game'},
 {name:'2048',icon:'🔢',category:'Puzzle',source:'AA Gamerz',path:'21-2048-Game'}
];
const base='https://aa-gamerz22.github.io/aa-gamerz-games/';
const grid=document.getElementById('gameGrid'), search=document.getElementById('search'), count=document.getElementById('count'), filters=document.getElementById('filters');
let active='All';
const categories=['All',...new Set(games.map(g=>g.category))];
filters.innerHTML=categories.map(c=>`<button class="chip ${c==='All'?'active':''}" data-category="${c}">${c}</button>`).join('');
filters.addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;active=b.dataset.category;document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('active',x===b));render()});
search.addEventListener('input',render);
function render(){const q=search.value.trim().toLowerCase();const visible=games.filter(g=>(active==='All'||g.category===active)&&(!q||`${g.name} ${g.category} ${g.source}`.toLowerCase().includes(q)));count.textContent=`${visible.length} game${visible.length===1?'':'s'} ready to play`;grid.innerHTML=visible.length?visible.map(g=>`<a class="game-card" href="${base}${g.path}/" target="_blank" rel="noopener"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category} • ${g.source}</p><span class="play">Play game →</span></a>`).join(''):`<div class="game-card" style="grid-column:1/-1;text-align:center"><h3>No games found</h3><p>Try another search or category.</p></div>`}
const themeButton=document.getElementById('themeButton');
const saved=localStorage.getItem('aither-theme');if(saved==='light')document.body.classList.add('light');
themeButton.onclick=()=>{document.body.classList.toggle('light');localStorage.setItem('aither-theme',document.body.classList.contains('light')?'light':'dark')};
render();
