const $=s=>document.querySelector(s),messages=$('#messages'),state=$('#state'),answer=$('#answer'),mic=$('#micBtn');
let socket;

function add(role,text,sources=[]){
  const d=document.createElement('div');d.className='msg '+role;d.textContent=text;
  if(sources?.length){const s=document.createElement('span');s.className='source';s.textContent=sources.map(x=>'['+x.id+'] '+x.title).join('  ·  ');d.appendChild(s)}
  messages.appendChild(d);messages.scrollTop=messages.scrollHeight;
}
function speak(text){if(!('speechSynthesis'in window))return;window.speechSynthesis.cancel();const u=new SpeechSynthesisUtterance(text.replace(/\[\d+\]/g,''));u.rate=.98;u.pitch=1.02;window.speechSynthesis.speak(u)}
function beep(){try{const C=window.AudioContext||window.webkitAudioContext;if(!C)return;const c=new C(),o=c.createOscillator(),g=c.createGain();o.frequency.value=660;g.gain.value=.035;o.connect(g);g.connect(c.destination);o.start();o.stop(c.currentTime+.08)}catch{}}
function notify(title,body){if('Notification'in window&&Notification.permission==='granted')new Notification(title,{body})}

async function ask(t){
  if(!t)return;add('user',t);answer.textContent=t;state.textContent='THINKING';
  try{
    const r=await (await fetch('/api/chat',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({text:t})})).json();
    add('assistant',r.text||JSON.stringify(r),r.sources||[]);
    answer.textContent=r.text||'Done.';state.textContent=(r.agent||r.intent||'READY').toUpperCase();
    $('#agentState').textContent=r.agent||r.research_agent||'verified response';
    $('#liveText').textContent=(r.research_agent?'Research: '+r.research_agent:'Task completed');
    if(r.confirmation_id) showConfirmation(r.confirmation_id,r.text||'Confirmation required before this action.');
    speak(r.text||'Done.');
  }catch(e){state.textContent='ERROR';answer.textContent='Request failed';add('system','Request failed: '+e);$('#liveText').textContent='Request failed'}
  refresh();refreshReminder();
}

$('#chat').onsubmit=e=>{e.preventDefault();const t=$('#input').value.trim();$('#input').value='';ask(t)};
document.querySelectorAll('[data-cmd]').forEach(b=>b.onclick=()=>ask(b.dataset.cmd));
$('#clear').onclick=()=>messages.innerHTML='';
mic.onclick=()=>{
  const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!SR){add('system','Speech recognition is unavailable in this browser. Use text input or install the optional Python voice backend.');return}
  const r=new SR();r.lang='en-US';r.interimResults=false;
  r.onstart=()=>{state.textContent='LISTENING';mic.classList.add('listening')};
  r.onresult=e=>{const t=e.results[0][0].transcript;$('#input').value=t;ask(t)};
  r.onerror=e=>add('system','Microphone error: '+e.error);
  r.onend=()=>{state.textContent='IDLE';mic.classList.remove('listening')};r.start();
};

function showConfirmation(id,message){
  const wrap=document.createElement('div');
  wrap.className='confirmation';
  const text=document.createElement('div');
  text.className='confirmation-text';
  text.textContent=message;
  const approve=document.createElement('button');
  approve.textContent='APPROVE';
  const cancel=document.createElement('button');
  cancel.textContent='CANCEL';
  approve.onclick=()=>resolveConfirmation(id,true,wrap,approve,cancel);
  cancel.onclick=()=>resolveConfirmation(id,false,wrap,approve,cancel);
  wrap.appendChild(text);wrap.appendChild(approve);wrap.appendChild(cancel);
  messages.appendChild(wrap);messages.scrollTop=messages.scrollHeight;
}
async function resolveConfirmation(id,approved,wrap,approve,cancel){
  approve.disabled=true;cancel.disabled=true;state.textContent=approved?'EXECUTING':'CANCELLED';
  try{
    const r=await (await fetch('/api/confirmations/'+encodeURIComponent(id),{
      method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({approved})
    })).json();
    wrap.remove();
    const resultText=r.result?.stdout||r.result?.stderr||r.result?.text;
    if(resultText)add('assistant',resultText);
    else if(r.text)add('assistant',r.text);
    else if(r.error)add('system','Confirmation error: '+r.error);
    $('#liveText').textContent=approved?'Approved and executed':'Action cancelled';
    speak(r.result?.text||r.text|| (approved?'Approved.':'Cancelled.'));
  }catch(e){
    approve.disabled=false;cancel.disabled=false;
    add('system','Confirmation request failed: '+e);
    $('#liveText').textContent='Confirmation failed';
  }
  refresh();
}
function connectEvents(){
  try{
    socket=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/api/events');
    socket.onmessage=e=>{
      const x=JSON.parse(e.data);
      if(x.event==='agent.state'){$('#agentState').textContent=(x.agent||x.intent||x.state||'working').toString();state.textContent=x.state||'WORKING'}
      if(x.event==='agent.error'){state.textContent='ERROR';$('#liveText').textContent='Agent error';add('system','Agent error: '+x.error)}
      if(x.event==='computer.action'){state.textContent=(x.state||'WORKING').toUpperCase();$('#liveText').textContent='Desktop: '+x.action+' · '+x.state}
      if(x.event==='computer.workflow'){state.textContent=(x.state||'WORKING').toUpperCase();$('#liveText').textContent='Workflow: '+x.state+' '+(x.application||'')}
      if(x.event==='computer.screenshot'){$('#liveText').textContent='Screenshot: '+x.path}
      if(x.event==='scheduler.add'){const t=x.task||{};$('#liveText').textContent='Reminder scheduled';$('#nextReminder').textContent='Next: '+(t.command||'Reminder')}
      if(x.event==='scheduler.due'){beep();const t=x.task||{};const msg=t.command||'Reminder';add('system','REMINDER: '+msg);$('#liveText').textContent='Reminder due';notify('JARVIS reminder',msg);speak('Reminder: '+msg);refreshReminder()}
    };
    socket.onclose=()=>setTimeout(connectEvents,3000);
  }catch{setTimeout(connectEvents,3000)}
}

async function refresh(){
  try{
    const s=await (await fetch('/api/status')).json();
    $('#ram').textContent=s.system?.ram_percent!=null?s.system.ram_percent+'%':'—';
    $('#ramState').textContent=s.system?.ram_available?Math.round(s.system.ram_available/1048576)+' MB free':'system';
    $('#model').textContent=s.model?.general||'—';
    $('#modelState').textContent=s.model?.backend||'backend';
    $('#agents').textContent=s.agents?.count??'—';
    $('#mcp').textContent=(s.mcp?.count??0)+' configured';
    $('#mcpState').textContent=s.mcp?.sdk_available?'SDK ready':'install [mcp]';
    $('#net').textContent=s.web?.available?'● ONLINE':'● OFFLINE';
  }catch{$('#net').textContent='● OFFLINE'}
}
async function refreshReminder(){
  try{
    const xs=await (await fetch('/api/schedule')).json();
    const next=xs.find(x=>x.status==='SCHEDULED');
    $('#nextReminder').textContent=next?'Next: '+next.command+' · '+new Date(next.due*1000).toLocaleTimeString():'No reminder scheduled';
  }catch{}
}
if('Notification'in window&&Notification.permission==='default')Notification.requestPermission().catch(()=>{});
connectEvents();refresh();refreshReminder();setInterval(refresh,5000);setInterval(refreshReminder,5000);
