const $ = (id) => document.getElementById(id);
const codeInput = $("codeInput");
const toast = $("toast");
let toastTimer;

function notify(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 4500);
}
function getCode() { return codeInput.value.trim(); }
function setBusy(button, busy, label) {
  button.disabled = busy;
  if (busy) { button.dataset.oldText = button.textContent; button.textContent = label; }
  else if (button.dataset.oldText) { button.textContent = button.dataset.oldText; }
}
async function postJSON(url, body) {
  const response = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}
codeInput.addEventListener("input", () => $("charCount").textContent = `${codeInput.value.length} characters`);
$("clearBtn").addEventListener("click", () => { codeInput.value=""; $("charCount").textContent="0 characters"; codeInput.focus(); });
$("reviewBtn").addEventListener("click", async () => {
  if (!getCode()) return notify("Paste some code first.");
  const button=$("reviewBtn"); setBusy(button,true,"Reviewing…");
  try {
    const data=await postJSON("/api/review",{code:getCode(),language:$("language").value});
    renderReview(data); loadHistory(); $("resultSection").scrollIntoView({behavior:"smooth"});
  } catch(e) { notify(e.message); } finally { setBusy(button,false); }
});
$("fixBtn").addEventListener("click", async () => {
  if (!getCode()) return notify("Paste some code first.");
  const button=$("fixBtn"); setBusy(button,true,"Fixing…");
  try { const data=await postJSON("/api/fix",{code:getCode(),language:$("language").value}); codeInput.value=data.code; codeInput.dispatchEvent(new Event("input")); notify("Suggested fix placed in the editor. Review it before using."); }
  catch(e){notify(e.message);} finally{setBusy(button,false);}
});
$("convertBtn").addEventListener("click", async () => {
  if (!getCode()) return notify("Paste some code first.");
  const button=$("convertBtn"); setBusy(button,true,"Converting…");
  try { const data=await postJSON("/api/convert",{code:getCode(),source:$("language").value,target:$("targetLanguage").value}); codeInput.value=data.code; codeInput.dispatchEvent(new Event("input")); $("language").value=$("targetLanguage").value; notify("Converted code placed in the editor."); }
  catch(e){notify(e.message);} finally{setBusy(button,false);}
});
function renderReview(data) {
  $("resultSection").classList.remove("hidden");
  $("summary").textContent=data.summary || "Review completed.";
  const issues=$("issues"); issues.innerHTML="";
  (data.issues || []).forEach(item=>{
    const div=document.createElement("div"); div.className="issue";
    const top=document.createElement("div"); top.className="issue-top";
    const sev=document.createElement("span"); sev.className="severity "+(item.severity||"Low"); sev.textContent=item.severity||"Info";
    const title=document.createElement("h4"); title.textContent=(item.title||"Code issue")+(item.line ? ` · line ${item.line}` : "");
    top.append(sev,title); div.append(top);
    const exp=document.createElement("p"); exp.textContent=item.explanation||"";
    const sug=document.createElement("p"); sug.textContent=item.suggestion ? "Suggestion: "+item.suggestion : "";
    div.append(exp,sug); issues.append(div);
  });
  if (!(data.issues||[]).length) issues.innerHTML='<p class="muted small">No issues were reported by the model.</p>';
  const strengths=$("strengths"); strengths.innerHTML="";
  if ((data.strengths||[]).length) {
    const h=document.createElement("h3"); h.textContent="What you did well"; strengths.append(h);
    const ul=document.createElement("ul"); ul.className="strength-list";
    data.strengths.forEach(s=>{const li=document.createElement("li");li.textContent=s;ul.append(li);}); strengths.append(ul);
  }
  const improved=(data.improved_code||"").trim();
  $("improvedWrap").classList.toggle("hidden",!improved);
  $("improvedCode").textContent=improved;
}
$("copyImproved").addEventListener("click", async()=>{try{await navigator.clipboard.writeText($("improvedCode").textContent);notify("Copied.");}catch(e){notify("Clipboard access was blocked.");}});
async function loadHistory(){
  try{
    const response=await fetch("/api/history"); if(!response.ok)return;
    const rows=await response.json(); const list=$("historyList"); list.innerHTML="";
    if(!rows.length){list.innerHTML='<p class="muted small">No reviews yet.</p>';return;}
    rows.forEach(row=>{const item=document.createElement("div");item.className="history-item";const strong=document.createElement("strong");strong.textContent=row.language+" review";const span=document.createElement("span");span.textContent=(row.created_at||"")+" · "+(row.preview||"").replace(/\s+/g," ").slice(0,55);item.append(strong,span);list.append(item);});
  }catch(e){}
}
$("refreshHistory").addEventListener("click",loadHistory);
async function checkHealth(){
  const el=$("modelStatus");
  try{
    const r=await fetch("/api/health");const d=await r.json();
    if(r.ok && d.model_available){el.innerHTML='<span class="status-dot online"></span><span>Ollama connected · model ready</span>';}
    else if(r.ok){el.innerHTML='<span class="status-dot"></span><span>Ollama connected · model not found</span>';}
    else{el.innerHTML='<span class="status-dot"></span><span>Ollama offline · open the Ollama app</span>';}
  }catch(e){el.innerHTML='<span class="status-dot"></span><span>Cannot reach Ollama</span>';}
}
loadHistory();checkHealth();
