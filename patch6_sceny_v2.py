#!/usr/bin/env python3
# patch6_sceny_v2.py — przebudowa mikrolearningu wg decyzji ownera (2026-08-18):
# 1) SCENY2: 15 scen (3 z kursu 1:1 + 12 wg scene-authoring-spec) — rejestr + źródło kreatora
# 2) Jednostka mikro: rozdział→rola→ 1 scena + 5 pytań + ułożenie listy (DnD), 10–12 min; koniec budżetu 2h
# 3) Runner beatów: 4 opcje (losowa kolejność), liczniki depletion (Zaufanie/Czas/Autorytet|Wiarygodność),
#    critical → konsekwencja + powtórka beatu; sceny z kursu: opcje 1:1, bez liczników
# 4) DnD listy kontrolnej: kolejność wzorcowa = kolejność pozycji banku; strzałki jako fallback
# 5) Pochodzenie elementów: kurs / silnik / bank v1.0 — widoczne chipy; status recenzji jak dotąd
# 6) Kreator scenek: typ materiału „scenka” w ścieżce produkcji; propozycja→recenzja→publikacja
import json, sys

SRC = 'prototyp-FOP-PL-EN_04_08.html'
src = open(SRC, encoding='utf-8').read()
orig = len(src)

def rep(old, new, n=1):
    global src
    assert src.count(old) == n, f'anchor x{src.count(old)}: {old[:80]!r}'
    src = src.replace(old, new, 1)

SCENY = json.load(open('sceny_v2_all.json', encoding='utf-8'))
sceny_js = json.dumps(SCENY, ensure_ascii=False)

JS_DATA = r'''
/* ============ SCENY2 — rejestr scen v2 (kurs 1:1 + silnik wg scene-authoring-spec) ============ */
const SCENY2 = ''' + sceny_js + r''';
const MIKRO_UNITS = {
  A:{komisja:"A-PSC",  obserwator:"SC-RA-01"},
  B:{komisja:"B-PSC",  obserwator:"SC-RA-03"},
  C:{komisja:"C-PSC",  obserwator:"C-OBS"},
  D:{komisja:"D-PSC",  obserwator:"D-OBS"},
  E:{komisja:"E-PSC",  obserwator:"E-OBS"},
  F:{komisja:"SC-R6-01", obserwator:"SC-R6-01"},
  G:{komisja:"G-PSC",  obserwator:"G-OBS"},
  H:{komisja:"H-PSC",  obserwator:"H-OBS"}
};
const LICZNIKI_DEF = {
  komisja:    [["trust","Zaufanie wyborców","Voter trust"],["time","Czas","Time"],["third","Autorytet komisji","Committee authority"]],
  obserwator: [["trust","Zaufanie","Trust"],["time","Czas","Time"],["third","Wiarygodność raportu","Report credibility"]]
};
function scena2(id){ return SCENY2.filter(s=>s.scene_id===id)[0]||null; }
function scenyDla(rola, etap){
  const r = rola==="komisja" ? "PSC" : "OBS";
  return SCENY2.filter(s=>s.stage===etap && s.role===r);
}
function pochodzenieChip(z){
  if(z==="kurs") return '<span class="schip opublikowane">'+esc(mkT("źródło: kurs FOP","source: FOP course"))+'</span>';
  if(z==="bank_v1") return '<span class="schip opublikowane">'+esc(mkT("bank v1.0","bank v1.0"))+'</span>';
  return '<span class="schip niezatw">'+esc(mkT("źródło: silnik (wygenerowane)","source: engine (generated)"))+'</span>';
}
'''

# ---------- A) dane po MIKRO_ROZDZIALY ----------
rep('function mkRozdz(){', JS_DATA + '\nfunction mkRozdz(){')

# ---------- B) jednostka zamiast lekcji: rola -> start jednostki ----------
rep('''function mikroLekcja(id){
  const m=state.test.mk;
  m.lekcja=id; m.els=mikroElems(m.rola,id); m.idx=0; m.pick=null; m.checked=false; m.answers={}; m.sc=null; m.scOk=0; m.scN=0; m.phase="run"; render();
}''',
'''function mikroUnitEls(rola, etap){
  const els=[];
  const sid=(MIKRO_UNITS[etap]||{})[rola];
  if(sid) els.push({typ: sid.indexOf("SC-R6")===0 ? "scena" : "scena2", id: sid});
  (QUIZY_PL[rola][etap]||[]).slice(0,5).forEach(q=>els.push({typ:"pytanie", id:q.id, rola:q.rola}));
  if((LISTY[etap]||LISTA) && ((LISTY[etap]||LISTA).items||[]).length>=3) els.push({typ:"dnd", id:"LISTA-"+etap});
  return els;
}
function mikroLekcja(id){ /* zgodność wsteczna: start jednostki */ mikroUnit(); }
function mikroUnit(){
  const m=state.test.mk;
  const etap=mkRozdz().etap;
  m.lekcja="UNIT-"+etap; m.els=mikroUnitEls(m.rola, etap); m.idx=0; m.pick=null; m.checked=false; m.answers={};
  m.sc=null; m.scOk=0; m.scN=0; m.b=null; m.dnd=null; m.phase="run"; render();
}''')

# rMikroWybor: zamiast kafli lekcji — jedna karta jednostki
rep('''  let lekcje='<p class="screen-sub">'+esc(mkT("Wybierz rolę, aby zobaczyć lekcje.","Select a role to see the lessons."))+'</p>';
  if(m.rola){
    lekcje='<div class="tiles">'+mkRozdz().lekcje.map(L=>{
      const els=mikroElems(m.rola,L.id);
      const nq=els.filter(e=>e.typ==="pytanie").length, ns=els.filter(e=>e.typ==="scena").length;
      return '<button class="tile" onclick="mikroLekcja(\\''+L.id+'\\')"><span class="t-k">'+esc(L.id)+'</span><span class="t-t">'+esc(mkT(L.tytul_pl,L.tytul_en))+'</span><span class="t-d">'+L.czas_min+' min · '+nq+' '+esc(mkT("pytań","questions"))+(ns?(' · '+ns+' '+esc(mkT("sceny","scenes"))):'')+'</span></button>';
    }).join("")+'</div>'+
    '<div class="b-meta" style="margin-top:10px">'+esc(mkT(MIKRO.job_aid.opis_pl,MIKRO.job_aid.opis_en))+'</div>';
  }''',
'''  let lekcje='<p class="screen-sub">'+esc(mkT("Wybierz rolę, aby rozpocząć jednostkę.","Select a role to start the unit."))+'</p>';
  if(m.rola){
    const etap=mkRozdz().etap;
    const els=mikroUnitEls(m.rola, etap);
    const sid=(MIKRO_UNITS[etap]||{})[m.rola];
    const sc = sid && sid.indexOf("SC-R6")!==0 ? scena2(sid) : null;
    const scLab = sc ? mkT(sc.setup_pl.slice(0,70)+"…", sc.setup_en.slice(0,70)+"…") : (sid||"—");
    const zrodloChip = sc ? pochodzenieChip(sc.zrodlo) : (sid?pochodzenieChip("silnik"):"");
    const hasDnd = els.some(e=>e.typ==="dnd");
    lekcje='<div class="tiles"><button class="tile" onclick="mikroUnit()"><span class="t-k">'+esc(etap)+'</span>'+
      '<span class="t-t">'+esc(mkT("Jednostka: 1 scenka + 5 pytań","Unit: 1 scene + 5 questions"))+(hasDnd?esc(mkT(" + ułożenie listy"," + list ordering")):"")+'</span>'+
      '<span class="t-d">10–12 min · '+esc(mkT("scena: ","scene: "))+esc(sid||"—")+'</span></button></div>'+
      '<div class="b-meta" style="margin-top:8px">'+zrodloChip+' '+esc(mkT("Każdy element nosi widoczne pochodzenie (kurs / silnik / bank v1.0) i status recenzji.","Every element carries visible provenance (course / engine / bank v1.0) and its review status."))+'</div>';
  }''')

# ---------- C) runner: obsługa scena2 (beaty+liczniki) i dnd ----------
rep('''function rMikroRun(m){
  const el=m.els[m.idx];''',
'''function beatOptsShuffled(m, kr){
  if(!m.b.ord || m.b.ordBeat!==m.b.step){
    const idx=kr.options.map((_,i)=>i);
    for(let i=idx.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [idx[i],idx[j]]=[idx[j],idx[i]]; }
    m.b.ord=idx; m.b.ordBeat=m.b.step;
  }
  return m.b.ord.map(i=>[i, kr.options[i]]);
}
function sc2Meters(m){
  const defs=LICZNIKI_DEF[m.rola];
  return '<div class="chips" style="margin:0 0 10px">'+defs.map(d=>{
    const v=m.b.meters[d[0]];
    const cls = v<=30 ? "usun" : (v<=60 ? "popraw" : "tak");
    return '<span class="schip '+cls+'">'+esc(mkT(d[1],d[2]))+': '+v+'</span>';
  }).join(" ")+'</div>';
}
function sc2Pick(i){ const m=state.test.mk; if(m.b.checked) return; m.b.pick=i; render(); }
function sc2Check(){
  const m=state.test.mk; const sc=scena2(m.b.id); const kr=sc.beats[m.b.step];
  if(m.b.pick==null){ toast(mkT("Wybierz odpowiedź","Select an answer")); return; }
  const o=kr.options[m.b.pick];
  m.scN=(m.scN||0)+1; if(o["class"]==="best") m.scOk=(m.scOk||0)+1;
  if(o.score){ ["trust","time","third"].forEach(k=>{ m.b.meters[k]=Math.max(0, Math.min(100, m.b.meters[k]+(o.score[k]||0))); }); }
  m.b.checked=true; m.b.wasCritical=!!o.critical; render();
}
function sc2Next(){
  const m=state.test.mk; const sc=scena2(m.b.id); 
  if(m.b.checked && m.b.wasCritical){ m.b.pick=null; m.b.checked=false; m.b.wasCritical=false; m.b.ord=null; render(); return; }
  if(m.b.step+1>=sc.beats.length){ if(!m.b.closed){ m.b.closed=true; render(); return; } m.b=null; mikroNext(); return; }
  m.b.step++; m.b.pick=null; m.b.checked=false; m.b.ord=null; render();
}
function rScena2(m, el){
  const sc=scena2(el.id);
  if(!m.b || m.b.id!==sc.scene_id){ m.b={id:sc.scene_id, step:-1, pick:null, checked:false, ord:null, ordBeat:null, closed:false, meters:{trust:100,time:100,third:100}}; }
  const b=m.b;
  const hasMeters = sc.zrodlo==="silnik";
  const badge='<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:0 0 10px"><span class="qchip">'+esc(mkT("scena","scene"))+' '+esc(sc.scene_id)+'</span>'+pochodzenieChip(sc.zrodlo)+statusChip(statusPozycji(m.rola, mkRozdz().etap, "scenka", sc.scene_id))+'</div>';
  const dalej=(lab)=>'<div class="next-row" style="margin:14px 0 0"><button class="btn btn-primary" onclick="sc2Next()">'+esc(lab)+'</button></div>';
  if(b.step===-1){
    return '<div class="tst-box">'+badge+
      '<h3 style="margin:0 0 10px;font-size:16.5px">'+esc(mkT(sc.stage_label_pl+" — scena", (sc.stage_label_pl||"")+" — scene"))+'</h3>'+
      '<p style="font-size:14.5px;line-height:1.55">'+esc(mkT(sc.setup_pl,sc.setup_en))+'</p>'+
      (sc.cast?'<div class="b-meta">'+esc(mkT("Obsada: ","Cast: "))+sc.cast.map(esc).join(", ")+'</div>':"")+
      '<div class="next-row" style="margin:14px 0 0"><button class="btn btn-primary" onclick="(function(){state.test.mk.b.step=0;render();})()">'+esc(mkT("Rozpocznij scenę","Start the scene"))+'</button></div></div>';
  }
  if(b.closed){
    const mm=hasMeters?sc2Meters(m):"";
    return '<div class="tst-box">'+badge+mm+
      '<h3 style="margin:0 0 10px;font-size:16.5px">'+esc(mkT("Zamknięcie sceny","Scene closing"))+'</h3>'+
      '<p style="font-size:14.5px;line-height:1.55">'+esc(mkT(sc.closing_pl,sc.closing_en))+'</p>'+dalej(mkT("Dalej: pytania","Next: questions"))+'</div>';
  }
  const kr=sc.beats[b.step];
  const prog='<p class="screen-sub" style="margin:0 0 6px">'+esc(mkT("Beat ","Beat "))+(b.step+1)+' / '+sc.beats.length+'</p>'+
    koraliki(sc.beats.map((x,i)=>{ let c=i<b.step?"done":""; if(i===b.step)c=(b.checked?"done ":"")+"cur"; return c; }), b.step+(b.checked?1:0), sc.beats.length);
  const zrodloLine = kr.source ? '<div class="b-meta" style="margin-top:8px">'+esc(mkT("Źródło: ","Source: "))+esc(kr.source)+(kr.source_verified===false?' <span class="schip niezatw">'+esc(mkT("źródło do weryfikacji","source unverified"))+'</span>':"")+'</div>' : "";
  if(!kr.options || !kr.options.length){
    return prog+'<div class="tst-box">'+badge+(hasMeters?sc2Meters(m):"")+
      '<p style="font-size:14.5px;line-height:1.55;white-space:pre-line">'+esc(mkT(kr.prompt_pl,kr.prompt_en))+'</p>'+zrodloLine+dalej(mkT("Dalej","Next"))+'</div>';
  }
  const opts=beatOptsShuffled(m,kr).map(([oi,o])=>{
    let cls="tst-opt";
    if(!b.checked){ if(b.pick===oi) cls+=" sel"; }
    else { if(o["class"]==="best") cls+=" ok"; else if(b.pick===oi) cls+=" bad"; }
    return '<button class="'+cls+'" '+(b.checked?'disabled ':'')+'onclick="sc2Pick('+oi+')"><span class="radio"></span><span>'+esc(mkT(o.text_pl,o.text_en))+'</span></button>';
  }).join("");
  let fb="";
  if(b.checked){
    const o=kr.options[b.pick];
    const ok=o["class"]==="best";
    fb='<div class="fbp '+(ok?"ok":"bad")+'">'+(o.critical?'<b>'+esc(mkT("Błąd krytyczny — beat zostanie powtórzony. ","Critical error — the beat will replay. "))+'</b>':"")+esc(mkT(o.feedback_pl,o.feedback_en))+'</div>'+zrodloLine;
  }
  const lastLab = b.checked && b.wasCritical ? mkT("Powtórz beat","Replay the beat") : (b.step+1>=sc.beats.length ? mkT("Zamknięcie sceny","Scene closing") : mkT("Dalej","Next"));
  return prog+'<div class="tst-box">'+badge+(hasMeters?sc2Meters(m):"")+
    '<p style="font-size:14.5px;line-height:1.55;white-space:pre-line">'+esc(mkT(kr.prompt_pl,kr.prompt_en))+'</p>'+opts+fb+
    '<div class="next-row" style="margin:14px 0 0">'+
    (b.checked ? '<button class="btn btn-primary" onclick="sc2Next()">'+esc(lastLab)+'</button>'
               : '<button class="btn btn-primary" onclick="sc2Check()">'+esc(mkT("Sprawdź decyzję","Check the decision"))+'</button>')+
    '</div></div>';
}
function dndInit(m, etap){
  const L=(LISTY[etap]||LISTA); const items=(L.items||[]).slice(0,6);
  const ord=items.map((_,i)=>i);
  for(let i=ord.length-1;i>0;i--){ const j=Math.floor(Math.random()*(i+1)); [ord[i],ord[j]]=[ord[j],ord[i]]; }
  m.dnd={etap:etap, items:items, ord:ord, checked:false, drag:null};
}
function dndMove(i, dir){ const d=state.test.mk.dnd; if(d.checked) return; const j=i+dir; if(j<0||j>=d.ord.length) return; [d.ord[i],d.ord[j]]=[d.ord[j],d.ord[i]]; render(); }
function dndDragStart(i){ state.test.mk.dnd.drag=i; }
function dndDrop(i){ const d=state.test.mk.dnd; if(d.checked||d.drag==null) return; const from=d.drag; d.drag=null; if(from===i) return; const v=d.ord.splice(from,1)[0]; d.ord.splice(i,0,v); render(); }
function dndCheck(){ const d=state.test.mk.dnd; d.checked=true; const m=state.test.mk; const ok=d.ord.every((v,i)=>v===i); m.answers["DND-"+d.etap]={ok:ok}; render(); }
function rDnd(m, el){
  const etap=mkRozdz().etap;
  if(!m.dnd) dndInit(m, etap);
  const d=m.dnd;
  const L=(LISTY[etap]||LISTA);
  const rows=d.ord.map((v,i)=>{
    const it=d.items[v];
    let cls="tst-opt"; if(d.checked){ cls+= v===i ? " ok" : " bad"; }
    return '<div class="'+cls+'" draggable="'+(!d.checked)+'" ondragstart="dndDragStart('+i+')" ondragover="event.preventDefault()" ondrop="dndDrop('+i+')" style="cursor:'+(d.checked?'default':'grab')+'">'+
      '<span class="radio" style="border-radius:4px">'+(i+1)+'</span><span><b>'+esc(it.nazwa)+'</b>'+
      (d.checked && v!==i ? '<div class="m-desc" style="margin-top:4px">'+esc(mkT("Właściwe miejsce: ","Correct position: "))+(v+1)+'</div>':"")+'</span>'+
      (!d.checked?'<span style="margin-left:auto;display:flex;gap:6px"><button class="btn" style="padding:2px 10px" onclick="event.stopPropagation();dndMove('+i+',-1)">↑</button><button class="btn" style="padding:2px 10px" onclick="event.stopPropagation();dndMove('+i+',1)">↓</button></span>':"")+
      '</div>';
  }).join("");
  const okN=d.checked?d.ord.filter((v,i)=>v===i).length:0;
  return '<div class="tst-box">'+
    '<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:0 0 10px"><span class="qchip">'+esc(mkT("ułożenie listy","list ordering"))+'</span>'+pochodzenieChip("bank_v1")+'</div>'+
    '<h3 style="margin:0 0 10px;font-size:16.5px">'+esc(mkT("Ułóż czynności listy kontrolnej we właściwej kolejności","Arrange the checklist steps in the correct order"))+'</h3>'+
    '<div class="b-meta" style="margin:0 0 10px">'+esc(L.meta && L.meta.tytul ? L.meta.tytul : "")+' · '+esc(mkT("przeciągnij pozycje albo użyj strzałek","drag the items or use the arrows"))+'</div>'+
    rows+
    (d.checked?'<div class="fbp '+(okN===d.ord.length?"ok":"bad")+'"><b>'+okN+' / '+d.ord.length+'</b> '+esc(mkT("pozycji na właściwym miejscu. Kolejność wzorcowa pochodzi z zatwierdzonej listy banku.","items in the right place. The model order comes from the approved bank checklist."))+'</div>':"")+
    '<div class="next-row" style="margin:14px 0 0">'+
    (d.checked?'<button class="btn btn-primary" onclick="(function(){state.test.mk.dnd=null;mikroNext();})()">'+esc(mkT("Dalej","Next"))+'</button>'
              :'<button class="btn btn-primary" onclick="dndCheck()">'+esc(mkT("Sprawdź kolejność","Check the order"))+'</button>')+
    '</div></div>';
}
function rMikroRun(m){
  const el=m.els[m.idx];
  if(el.typ==="scena2"){
    const head0='<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · jednostka ","Microlearning · unit ")+mkRozdz().etap+' · ')+esc(ROLE[m.rola])+'</p>'+
      '<p class="screen-sub" style="margin:0 0 6px">'+esc(mkT("Element ","Item "))+(m.idx+1)+' / '+m.els.length+'</p>';
    return head0+rScena2(m, el);
  }
  if(el.typ==="dnd"){
    const head0='<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · jednostka ","Microlearning · unit ")+mkRozdz().etap+' · ')+esc(ROLE[m.rola])+'</p>'+
      '<p class="screen-sub" style="margin:0 0 6px">'+esc(mkT("Element ","Item "))+(m.idx+1)+' / '+m.els.length+'</p>';
    return head0+rDnd(m, el);
  }''')

# nagłówek starej gałęzi (scena v1 + pytania) — L może nie istnieć w jednostce
rep('''  const RZ=mkRozdz();
  const L=RZ.lekcje.filter(x=>x.id===m.lekcja)[0];''',
'''  const RZ=mkRozdz();
  const L=(RZ.lekcje||[]).filter(x=>x.id===m.lekcja)[0]||{tytul_pl:mkT("Jednostka ","Unit ")+RZ.etap,tytul_en:"Unit "+RZ.etap,czas_min:12};''')

# wynik: DND w liczniku pytań pomijamy (answers ma DND-*) — filtruj
rep('''function rMikroWynik(m){
  const qids=m.els.filter(e=>e.typ==="pytanie").map(e=>e.id);''',
'''function rMikroWynik(m){
  const qids=m.els.filter(e=>e.typ==="pytanie").map(e=>e.id);
  const dnd=m.answers["DND-"+mkRozdz().etap];''')
rep('''    (m.scN?'<p class="screen-sub" style="margin:0 0 6px"><b>'+esc(mkT("Decyzje w scenach: ","Scene decisions: "))+m.scOk+' / '+m.scN+'</b></p>':'')+''',
'''    (m.scN?'<p class="screen-sub" style="margin:0 0 6px"><b>'+esc(mkT("Decyzje w scenie: ","Scene decisions: "))+m.scOk+' / '+m.scN+'</b></p>':'')+
    (dnd?'<p class="screen-sub" style="margin:0 0 6px"><b>'+esc(mkT("Ułożenie listy: ","List ordering: "))+esc(dnd.ok?mkT("poprawne","correct"):mkT("do powtórki","to retry"))+'</b></p>':'')+''')
# wynik: tytuł bez L (jednostka)
rep("  const L=mkRozdz().lekcje.filter(x=>x.id===m.lekcja)[0];",
    "  const L=((mkRozdz().lekcje)||[]).filter(x=>x.id===m.lekcja)[0]||{tytul_pl:mkT('Jednostka ','Unit ')+mkRozdz().etap,tytul_en:'Unit '+mkRozdz().etap};")

# mikroQ: dla jednostek H bierze SRC (już jest); pytania jednostki mają rola z QUIZY — ok.
# mikroElems zostaje (stary format F w rejestrze), ale jednostka F używa starej sceny przez typ 'scena':
# stara gałąź 'scena' w rMikroRun czyta MIKRO.sceny — SC-R6-01 tam jest. OK.

# ---------- D) grid rozdziałów: opis jednostkowy ----------
rep('''    return '<button class="tile" onclick="mikroRozdzSel(\\''+r.id+'\\')"><span class="t-k">'+esc(r.etap)+'</span><span class="t-t">'+esc(r.id)+' · '+esc(mkT(r.tytul_pl,r.tytul_en))+'</span><span class="t-d">'+r.czas_min+' min · '+esc(status)+'</span></button>';''',
'''    return '<button class="tile" onclick="mikroRozdzSel(\\''+r.id+'\\')"><span class="t-k">'+esc(r.etap)+'</span><span class="t-t">'+esc(r.id)+' · '+esc(mkT(r.tytul_pl,r.tytul_en))+'</span><span class="t-d">10–12 min · '+esc(mkT("1 scenka + 5 pytań","1 scene + 5 questions"))+' · '+esc(status)+'</span></button>';''')

# ---------- E) kreator scenek w ścieżce produkcji ----------
# TYP: dodaj 'scenka'
rep('const TYP = {get wielokrotny_wybor()',
    'const TYP = {get scenka(){return LANG==="en"?"interactive scene":"scenka interaktywna";}, get wielokrotny_wybor()')
open(SRC,'w',encoding='utf-8').write(src)
print(f'OK czesc E1: {orig} -> {len(src)}')
