const AITHER_BACKEND = 'https://aitherbackendnew.onrender.com';
const grid=document.getElementById('gameGrid'),search=document.getElementById('search'),count=document.getElementById('count'),filters=document.getElementById('filters');
let games=[];
let active='All';

const accountButton=document.getElementById('accountButton');
const accountModal=document.getElementById('accountModal');
const accountLoggedOut=document.getElementById('accountLoggedOut');
const accountLoggedIn=document.getElementById('accountLoggedIn');
const accountForm=document.getElementById('accountForm');
const accountName=document.getElementById('accountName');
const accountEmail=document.getElementById('accountEmail');
const accountPassword=document.getElementById('accountPassword');
const accountSubmit=document.getElementById('accountSubmit');
const accountMessage=document.getElementById('accountMessage');
const accountWelcome=document.getElementById('accountWelcome');
const accountEmailDisplay=document.getElementById('accountEmailDisplay');
const accountVerifyStatus=document.getElementById('accountVerifyStatus');
const accountSignedMessage=document.getElementById('accountSignedMessage');
const resendVerification=document.getElementById('resendVerification');
const logoutButton=document.getElementById('logoutButton');
let accountMode='login';

function authHeaders(){
  const token=localStorage.getItem('aither_session_token');
  return token?{'Authorization':`Bearer ${token}`}:{};
}
async function authRequest(path,options={}){
  const headers={'Accept':'application/json',...(options.body?{'Content-Type':'application/json'}:{}),...authHeaders(),...(options.headers||{})};
  return fetch(`${AITHER_BACKEND}${path}`,{...options,headers,credentials:'include'});
}
function showAccount(){accountModal.hidden=false;document.body.style.overflow='hidden';}
function hideAccount(){accountModal.hidden=true;document.body.style.overflow='';}
function setAccountMode(mode){
  accountMode=mode;
  document.querySelectorAll('.account-tab').forEach(b=>b.classList.toggle('active',b.dataset.accountMode===mode));
  document.getElementById('nameField').hidden=mode!=='register';
  accountName.required=mode==='register';
  accountPassword.autocomplete=mode==='register'?'new-password':'current-password';
  accountSubmit.textContent=mode==='register'?'Create account':'Sign in';
  accountMessage.textContent='';
}
function openAccount(user){
  showAccount();
  if(user){
    accountLoggedOut.hidden=true;accountLoggedIn.hidden=false;
    accountWelcome.textContent=`Welcome, ${user.name || 'Aither user'}!`;
    accountEmailDisplay.textContent=user.email || '';
    accountVerifyStatus.textContent=user.email_verified?'Your email is verified and your Aither session is active.':'Your account is active. Please verify your email from the verification message.';
    resendVerification.style.display=user.email_verified?'none':'block';
  }else{
    accountLoggedOut.hidden=false;accountLoggedIn.hidden=true;setAccountMode('login');
  }
}
async function refreshAccount(){
  try{
    const response=await authRequest('/api/auth/session');
    if(!response.ok)throw new Error('session check failed');
    const data=await response.json();
    if(data.authenticated&&data.user){accountButton.textContent=data.user.name?`Hi, ${data.user.name}`:'Account';accountButton.dataset.authenticated='true';return data.user;}
  }catch(e){}
  accountButton.textContent='Account';accountButton.dataset.authenticated='false';
  return null;
}
accountButton.addEventListener('click',async()=>openAccount(await refreshAccount()));
document.querySelectorAll('[data-close-account]').forEach(el=>el.addEventListener('click',hideAccount));
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!accountModal.hidden)hideAccount()});
document.querySelectorAll('.account-tab').forEach(b=>b.addEventListener('click',()=>setAccountMode(b.dataset.accountMode)));

accountForm.addEventListener('submit',async e=>{
  e.preventDefault();
  accountMessage.textContent='';accountSubmit.disabled=true;accountSubmit.textContent=accountMode==='register'?'Creating…':'Signing in…';
  try{
    const payload=accountMode==='register'?{name:accountName.value.trim(),email:accountEmail.value.trim(),password:accountPassword.value}:{email:accountEmail.value.trim(),password:accountPassword.value};
    const response=await authRequest(`/api/auth/${accountMode==='register'?'register':'login'}`,{method:'POST',body:JSON.stringify(payload)});
    const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.detail||'Unable to complete account request.');
    if(data.session_token)localStorage.setItem('aither_session_token',data.session_token);
    accountPassword.value='';
    accountMessage.style.color='#8ff0ce';
    accountMessage.textContent=accountMode==='register'?'Account created! Check your email to verify it.':'Signed in successfully.';
    await refreshAccount();
    setTimeout(async()=>openAccount(data.user||await refreshAccount()),350);
  }catch(error){accountMessage.style.color='#ffb8c3';accountMessage.textContent=error.message||'Something went wrong.';}
  finally{accountSubmit.disabled=false;accountSubmit.textContent=accountMode==='register'?'Create account':'Sign in';}
});

logoutButton.addEventListener('click',async()=>{
  logoutButton.disabled=true;
  try{await authRequest('/api/auth/logout',{method:'POST'});}catch(e){}
  localStorage.removeItem('aither_session_token');
  accountButton.textContent='Account';
  accountLoggedOut.hidden=false;accountLoggedIn.hidden=true;
  accountSignedMessage.style.color='#8ff0ce';accountSignedMessage.textContent='You are signed out.';
  setAccountMode('login');
  logoutButton.disabled=false;
});
resendVerification.addEventListener('click',async()=>{
  resendVerification.disabled=true;accountSignedMessage.style.color='#aeb6cc';accountSignedMessage.textContent='Sending verification email…';
  try{
    const response=await authRequest('/api/auth/verify/resend',{method:'POST'});const data=await response.json().catch(()=>({}));
    if(!response.ok)throw new Error(data.detail||'Could not send verification email.');
    accountSignedMessage.style.color='#8ff0ce';accountSignedMessage.textContent=data.already_verified?'Your email is already verified.':'Verification email sent.';
  }catch(error){accountSignedMessage.style.color='#ffb8c3';accountSignedMessage.textContent=error.message;}
  resendVerification.disabled=false;
});

async function init(){
  games=await fetch('games.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('games.json failed');return r.json()});
  const categories=['All',...new Set(games.map(g=>g.category))];
  filters.innerHTML=categories.map(c=>`<button class="chip ${c==='All'?'active':''}" data-category="${c}">${c}</button>`).join('');
  filters.addEventListener('click',e=>{const b=e.target.closest('.chip');if(!b)return;active=b.dataset.category;document.querySelectorAll('.chip').forEach(x=>x.classList.toggle('active',x===b));render()});
  search.addEventListener('input',render);render();await refreshAccount();
}
function render(){const q=search.value.trim().toLowerCase(),visible=games.filter(g=>(active==='All'||g.category===active)&&(!q||`${g.name} ${g.category}`.toLowerCase().includes(q)));count.textContent=`${visible.length} games ready to play`;grid.innerHTML=visible.length?visible.map(g=>`<a class="game-card" href="${g.path}/"><div class="game-icon">${g.icon}</div><h3>${g.name}</h3><p>${g.category}</p><span class="play">Play game →</span></a>`).join(''):`<div class="game-card" style="grid-column:1/-1;text-align:center"><h3>No games found</h3><p>Try another search.</p></div>`}

const themeButton=document.getElementById('themeButton'),saved=localStorage.getItem('aither-theme');
if(saved==='light')document.body.classList.add('light');
themeButton.onclick=()=>{document.body.classList.toggle('light');localStorage.setItem('aither-theme',document.body.classList.contains('light')?'light':'dark')};
init().catch(()=>count.textContent='Game library failed to load');
