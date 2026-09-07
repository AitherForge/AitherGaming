const games=[
 {name:'Candy Crush',icon:'🍬',category:'Puzzle',path:'01-Candy-Crush-Game'},
 {name:'Archery',icon:'🏹',category:'Action',path:'02-Archery-Game'},
 {name:'Minesweeper',icon:'💣',category:'Puzzle',path:'05-Minesweeper-Game'},
 {name:'Tower Blocks',icon:'🏗️',category:'Arcade',path:'06-Tower-Blocks'},
 {name:'Tetris',icon:'🟦',category:'Puzzle',path:'08-Tetris-Game'},
 {name:'Tilting Maze',icon:'🌀',category:'Puzzle',path:'09-Tilting-Maze-Game'},
 {name:'Rock Paper Scissors',icon:'✊',category:'Party',path:'11-Rock-Paper-Scissors'},
 {name:'Number Guessing',icon:'🔢',category:'Puzzle',path:'12-Type-Number-Guessing-Game'},
 {name:'Connect Four',icon:'🔴',category:'Board',path:'15-Connect-Four-Game'},
 {name:'Hangman',icon:'🔤',category:'Word',path:'18-Hangman-Game'},
 {name:'Crossy Road',icon:'🐔',category:'Arcade',path:'20-Crossy-Road-Game'},
 {name:'2048',icon:'🔢',category:'Puzzle',path:'21-2048-Game'},
 {name:'Snake',icon:'🐍',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Breakout',icon:'🧱',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Pong',icon:'🏓',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Space Invaders',icon:'👾',category:'Action',url:'https://chadmalek.com/'},
 {name:'Frogger',icon:'🐸',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Flappy Bird',icon:'🐦',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Asteroids',icon:'☄️',category:'Action',url:'https://chadmalek.com/'},
 {name:'Doodle Jump',icon:'🦘',category:'Arcade',url:'https://chadmalek.com/'},
 {name:'Chess',icon:'♟️',category:'Board',url:'https://chadmalek.com/'},
 {name:'Checkers',icon:'⚫',category:'Board',url:'https://chadmalek.com/'},
 {name:'Solitaire',icon:'🃏',category:'Card',url:'https://chadmalek.com/'},
 {name:'Sudoku',icon:'🔢',category:'Puzzle',url:'https://chadmalek.com/'},
 {name:'Memory Match',icon:'🧠',category:'Puzzle',url:'https://chadmalek.com/'},
 {name:'Simon',icon:'🔴',category:'Puzzle',url:'https://chadmalek.com/'},
 {name:'Sokoban',icon:'📦',category:'Puzzle',url:'https://chadmalek.com/'},
 {name:'Wordle',icon:'🟩',category:'Word',url:'https://chadmalek.com/'},
 {name:'Battleship',icon:'🚢',category:'Board',url:'https://chadmalek.com/'},
 {name:'Reaction Time',icon:'⚡',category:'Skill',url:'https://tools.jarvisbox.app/game/'},
 {name:'Aim Trainer',icon:'🎯',category:'Skill',url:'https://tools.jarvisbox.app/game/'},
 {name:'Typing Speed',icon:'⌨️',category:'Skill',url:'https://tools.jarvisbox.app/game/'},
 {name:'Whack-a-Mole',icon:'🔨',category:'Arcade',url:'https://tools.jarvisbox.app/game/'},
 {name:'Sliding Puzzle',icon:'🧩',category:'Puzzle',url:'https://unicodegames.com/'},
 {name:'Lights Out',icon:'💡',category:'Puzzle',url:'https://unicodegames.com/'},
 {name:'Reversi',icon:'⚪',category:'Board',url:'https://unicodegames.com/'},
 {name:'Yahtzee',icon:'🎲',category:'Board',url:'https://unicodegames.com/'},
 {name:'Mastermind',icon:'🧠',category:'Puzzle',url:'https://unicodegames.com/'},
 {name:'Word Search',icon:'🔎',category:'Word',url:'https://unicodegames.com/'},
 {name:'Mahjong',icon:'🀄',category:'Puzzle',url:'https://gamejadoo.com/'},
 {name:'Bubble Shooter',icon:'🫧',category:'Puzzle',url:'https://gamejadoo.com/'},
 {name:'Fruit Merge',icon:'🍉',category:'Puzzle',url:'https://gamejadoo.com/'},
 {name:'Mini Golf',icon:'⛳',category:'Sports',url:'https://gamejadoo.com/'},
 {name:'Drift Boss',icon:'🏎️',category:'Racing',url:'https://gamejadoo.com/'},
 {name:'Hill Climb',icon:'🚙',category:'Racing',url:'https://gamejadoo.com/'},
 {name:'Bike Stunt',icon:'🏍️',category:'Sports',url:'https://gamejadoo.com/'},
 {name:'Helicopter Rush',icon:'🚁',category:'Action',url:'https://gamejadoo.com/'},
 {name:'Stick Hero',icon:'🦸',category:'Arcade',url:'https://gamejadoo.com/'},
 {name:'Alien Invaders',icon:'👽',category:'Action',url:'https://gamejadoo.com/'},
 {name:'Darts',icon:'🎯',category:'Sports',url:'https://gamejadoo.com/'}
];
const base='https://aa-gamerz22.github.io/aa-gamerz-games/';
const grid=document.getElementById('gameGrid'),search=document.getElementById('search'),count=document.getElementById('count'),filters=document.getElementById('filters');
let active='All';
const categories=['All',...new Set(games.map(g=>g.category))];
filters.innerHTML=categories.map(c=>`<button class="chip ${c==='All'?'active':''}" data-category="${c}">${c}</button>`).join('');
filters.addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;active=b.dataset.category;document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('active',x===b));render()});
search.addEventListener('input',render);
function render(){const q=search.value.trim().toLowerCase();const visible=games.filter(g=>(active==='All'||g.category===active)&&(!q||`${g.name} ${g.category}`.toLowerCase().includes(q)));count.textContent=`${visible.length} games ready to play`;grid.innerHTML=visible.length?visible.map(g=>{const href=g.url||`${base}${g.path}/`;return `<a class="game-card" href="${href}" target="_blank" rel="noopener"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category}</p><span class="play">Play game →</span></a>`}).join(''):`<div class="game-card" style="grid-column:1/-1;text-align:center"><h3>No games found</h3><p>Try another search or category.</p></div>`}
const themeButton=document.getElementById('themeButton');const saved=localStorage.getItem('aither-theme');if(saved==='light')document.body.classList.add('light');themeButton.onclick=()=>{document.body.classList.toggle('light');localStorage.setItem('aither-theme',document.body.classList.contains('light')?'light':'dark')};render();