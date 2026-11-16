from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .rag import answer

app = FastAPI(title="Agri RAG Demo")


class Question(BaseModel):
    question: str
    k: int = 4


@app.post("/ask")
def ask(q: Question):
    return answer(q.question, q.k)


@app.get("/health")
def health():
    return {"status": "ok"}


PAGE = """<!doctype html><meta charset=utf-8><title>Agri RAG</title>
<style>body{font-family:system-ui;max-width:720px;margin:3rem auto;padding:0 1rem}
input{width:75%;padding:.6rem}button{padding:.6rem 1rem}pre{white-space:pre-wrap;background:#f4f4f4;padding:1rem}</style>
<h2>Ask the documents / Posez une question</h2>
<input id=q placeholder="Ask in English or French"> <button onclick=go()>Ask</button>
<pre id=out></pre>
<script>
async function go(){
  out.textContent='...';
  const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:q.value})});
  const j=await r.json();
  out.textContent=j.answer+'\\n\\nSources:\\n'+j.sources.map(s=>`[${s.n}] ${s.source} p.${s.page}`).join('\\n')+`\\n\\n(${j.latency_s}s, ${j.tokens} tokens)`;
}
q.addEventListener('keydown',e=>{if(e.key==='Enter')go()});
</script>"""


@app.get("/", response_class=HTMLResponse)
def home():
    return PAGE
