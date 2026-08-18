#!/usr/bin/env python3
# patch5_koraliki.py — pasek postępu "koraliki" (podświetlane po wykonaniu zadania) we wszystkich przebiegach:
# 1) CSS: segmenty -> okrągłe koraliki z animacją zapalenia (quiz testowy i lista dostają je automatycznie przez segBar/segBarLista)
# 2) koraliki() — wspólny renderer
# 3) Recenzja: koralik na pozycję, kolor wg decyzji TAK/POPRAW/USUŃ
# 4) Mikro-learning: koraliki elementów lekcji + koraliki kroków sceny + podsumowanie na ekranie wyniku
import sys

SRC = 'prototyp-FOP-PL-EN_04_08.html'
src = open(SRC, encoding='utf-8').read()
orig = len(src)

def rep(old, new, n=1):
    global src
    assert src.count(old) == n, f'anchor x{src.count(old)}: {old[:70]!r}'
    src = src.replace(old, new, 1)

# ---------- 1) CSS: koraliki zamiast płaskich segmentów ----------
rep('''.segbar{display:flex;gap:3px;height:10px;margin:2px 0 12px}
.segbar .seg{flex:1;background:var(--line);border-radius:4px;min-width:4px}
.segbar .seg.ok{background:var(--tak)}
.segbar .seg.bad{background:var(--popraw)}
.segbar .seg.cur{outline:2px solid var(--brand);outline-offset:1px}''',
'''.segbar{display:flex;gap:6px;margin:2px 0 12px;flex-wrap:wrap;align-items:center}
.segbar .seg{flex:none;width:13px;height:13px;border-radius:50%;background:var(--card);border:2px solid var(--line);box-sizing:border-box;transition:background .25s,border-color .25s,transform .25s}
.segbar .seg.ok{background:var(--tak);border-color:var(--tak);animation:krlpop .3s ease}
.segbar .seg.bad{background:var(--popraw);border-color:var(--popraw);animation:krlpop .3s ease}
.segbar .seg.done{background:var(--brand);border-color:var(--brand);animation:krlpop .3s ease}
.segbar .seg.tak{background:var(--tak);border-color:var(--tak);animation:krlpop .3s ease}
.segbar .seg.popraw{background:var(--popraw);border-color:var(--popraw);animation:krlpop .3s ease}
.segbar .seg.usun{background:#b3433b;border-color:#b3433b;animation:krlpop .3s ease}
.segbar .seg.cur{border-color:var(--brand);box-shadow:0 0 0 3px color-mix(in srgb, var(--brand) 25%, transparent);transform:scale(1.15)}
.segbar .krl-n{font-size:11.5px;color:var(--text-soft);font-family:"Space Mono",monospace;margin-left:4px;white-space:nowrap}
@keyframes krlpop{0%{transform:scale(.5)}70%{transform:scale(1.25)}100%{transform:scale(1)}}''')

# ---------- 2) wspólny renderer (przy segBar) ----------
rep('function segBar(t){',
'''function koraliki(states, doneN, totalN){
  const beads = states.map(c=>'<i class="seg'+(c?' '+c:'')+'"></i>').join("");
  const lic = (doneN!=null && totalN!=null) ? '<span class="krl-n">'+doneN+'/'+totalN+'</span>' : "";
  return '<div class="segbar" role="progressbar" aria-valuemin="0" aria-valuemax="'+(totalN!=null?totalN:states.length)+'" aria-valuenow="'+(doneN!=null?doneN:0)+'">'+beads+lic+'</div>';
}
function segBar(t){''')

# ---------- 3) Recenzja: koralik na pozycję wg decyzji ----------
rep('''  const done=s.items.length-c.none;
  return _T(336)+''',
'''  const done=s.items.length-c.none;
  const krlRec = koraliki(s.items.map(p=>{const d=s.decisions[p.id].decyzja; return d==="TAK"?"tak":d==="POPRAW"?"popraw":d==="USUN"?"usun":"";}), done, s.items.length);
  return _T(336)+''')
rep("'<div class=\"source\">'+meta.zrodlo+'</div>'+\n    '<div class=\"infobox\">",
    "'<div class=\"source\">'+meta.zrodlo+'</div>'+\n    krlRec+\n    '<div class=\"infobox\">")

# ---------- 4) Mikro: koraliki elementów lekcji (rMikroRun, po head) ----------
rep('''  const RZ=mkRozdz();
  const L=RZ.lekcje.filter(x=>x.id===m.lekcja)[0];
  const head=''',
'''  const RZ=mkRozdz();
  const L=RZ.lekcje.filter(x=>x.id===m.lekcja)[0];
  const krlEls = koraliki(m.els.map((e2,i2)=>{
    let c = "";
    if(e2.typ==="pytanie"){ const a2=m.answers[e2.id]; if(a2) c = a2.ok?"ok":"bad"; }
    else if(i2<m.idx) c = "done";
    if(i2===m.idx) c = (c?c+" ":"")+"cur";
    return c;
  }), Object.keys(m.answers).length + m.els.slice(0,m.idx).filter(e2=>e2.typ==="scena").length, m.els.length);
  const head=''')
rep("'<p class=\"screen-sub\" style=\"margin:0 0 10px\">'+esc(mkT(\"Element \",\"Item \"))+(m.idx+1)+' / '+m.els.length+' · '+esc(mkT(L.tytul_pl,L.tytul_en))+'</p>';",
    "'<p class=\"screen-sub\" style=\"margin:0 0 6px\">'+esc(mkT(\"Element \",\"Item \"))+(m.idx+1)+' / '+m.els.length+' · '+esc(mkT(L.tytul_pl,L.tytul_en))+'</p>'+krlEls;")

# ---------- 5) Mikro: koraliki kroków sceny ----------
rep("    const prog='<p class=\"screen-sub\" style=\"margin:0 0 10px\">'+esc(mkT(\"Krok \",\"Step \"))+(s.step+1)+' / '+kroki.length+' · '+esc(mkT(sc.tytul_pl,sc.tytul_en))+'</p>';",
"""    const krlSc = koraliki(kroki.map((k2,i2)=>{
      let c = i2<s.step ? "done" : "";
      if(i2===s.step) c = (s.checked?"done ":"")+"cur";
      return c;
    }), s.step + (s.checked?1:0), kroki.length);
    const prog='<p class="screen-sub" style="margin:0 0 6px">'+esc(mkT("Krok ","Step "))+(s.step+1)+' / '+kroki.length+' · '+esc(mkT(sc.tytul_pl,sc.tytul_en))+'</p>'+krlSc;""")

# ---------- 6) Mikro: podsumowanie koralikowe na ekranie wyniku ----------
rep('''  return '<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · wynik lekcji","Microlearning · lesson result"))+'</p>'+''',
'''  const krlWynik = koraliki(m.els.map(e2=>{
    if(e2.typ==="pytanie"){ const a2=m.answers[e2.id]; return a2 ? (a2.ok?"ok":"bad") : ""; }
    return "done";
  }), m.els.length, m.els.length);
  return '<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · wynik lekcji","Microlearning · lesson result"))+'</p>'+''')
rep('''': '+ok+' / '+qids.length+'</h2>'+''',
'''': '+ok+' / '+qids.length+'</h2>'+krlWynik+''')

open(SRC, 'w', encoding='utf-8').write(src)
print(f'OK: {orig} -> {len(src)} bytes (+{len(src)-orig})')
