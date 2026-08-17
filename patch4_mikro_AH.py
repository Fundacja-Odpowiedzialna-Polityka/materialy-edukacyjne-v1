#!/usr/bin/env python3
# patch4_mikro_AH.py — rozszerza mikrolearning z R6 na pełny trzon R1–R8:
# 1) MIKRO_AH_Q: 36 pytań (A–E, G) -> QUIZY_PL per etap i rola (walidacja skilla 0/0)
# 2) MIKRO_ROZDZIALY: definicje rozdziałów R1–R8 (R6 wskazuje istniejące MIKRO; R8 czerpie z banku v1.0 SRC_QUIZ_*)
# 3) UI: ekran wyboru rozdziału -> rola -> lekcje; R8 ze statyczną plakietką "bank v1.0"
# 4) Panel Banku: zbiorcze podsumowanie statusów per rozdział
import json

SRC = 'prototyp-FOP-PL-EN_04_08.html'
src = open(SRC, encoding='utf-8').read()
orig = len(src)

def rep(old, new, n=1):
    global src
    assert src.count(old) == n, f'anchor x{src.count(old)}: {old[:70]!r}'
    src = src.replace(old, new, 1)

bank = json.load(open('bank-mikrolearning-A-H.json', encoding='utf-8'))
items = []
for q in bank['pytania']:
    q = dict(q); q.pop('recenzja', None); items.append(q)
items_js = json.dumps(items, ensure_ascii=False)

DATA = r'''
/* ================= MIKROLEARNING A–H — trzon R1–R8 (wsad do recenzji; owner v1) ================= */
const MIKRO_AH_Q = ''' + items_js + r''';
const MIKRO_FAZA_ETAP = {otwarcie_lokalu:"A", obsluga_wyborcy:"B", pelnomocnik:"C", pomoc_wyborcy:"D", zaswiadczenie:"E", rozliczenie_kart:"G"};
(function(){
  const per = {};
  MIKRO_AH_Q.forEach(q=>{
    const e = MIKRO_FAZA_ETAP[q.faza]; if(!e) return;
    per[e] = per[e] || {komisja:[], obserwator:[]};
    if(q.rola==="czlonek_komisji"||q.rola==="wspolna") per[e].komisja.push(q);
    if(q.rola==="obserwator"||q.rola==="wspolna") per[e].obserwator.push(q);
  });
  Object.keys(per).forEach(e=>{
    QUIZY_PL.komisja[e] = per[e].komisja.concat(QUIZY_PL.komisja[e]||[]);
    QUIZY_PL.obserwator[e] = per[e].obserwator.concat(QUIZY_PL.obserwator[e]||[]);
  });
})();
const MIKRO_ROZDZIALY = [
 {id:"R1", etap:"A", czas_min:10, tytul_pl:"Otwarcie lokalu", tytul_en:"Opening the polling station",
  lekcje:[
   {id:"R1-L1", czas_min:5, tytul_pl:"Zanim przyjdzie pierwszy wyborca", tytul_en:"Before the first voter",
    elementy:[{typ:"pytanie",id:"wsp-R1-001",rola:"wspolna"},{typ:"pytanie",id:"czl-R1-002",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R1-003",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-R1-004",rola:"obserwator"}]},
   {id:"R1-L2", czas_min:5, tytul_pl:"Urna pod strażą", tytul_en:"Guarding the ballot box",
    elementy:[{typ:"pytanie",id:"czl-R1-005",rola:"czlonek_komisji"},{typ:"pytanie",id:"wsp-R1-006",rola:"wspolna"},{typ:"pytanie",id:"obs-R1-004",rola:"obserwator"}]}]},
 {id:"R2", etap:"B", czas_min:10, tytul_pl:"Obsługa wyborcy", tytul_en:"Serving the voter",
  lekcje:[
   {id:"R2-L1", czas_min:5, tytul_pl:"Tożsamość i podpis", tytul_en:"Identity and signature",
    elementy:[{typ:"pytanie",id:"czl-R2-001",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R2-002",rola:"czlonek_komisji"},{typ:"pytanie",id:"wsp-R2-003",rola:"wspolna"}]},
   {id:"R2-L2", czas_min:5, tytul_pl:"Karty: odmowa, pomyłka, granica słowa", tytul_en:"Ballots: refusal, mistake, the line of words",
    elementy:[{typ:"pytanie",id:"czl-R2-004",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R2-005",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-R2-006",rola:"obserwator"},{typ:"pytanie",id:"wsp-R2-003",rola:"wspolna"}]}]},
 {id:"R3", etap:"C", czas_min:10, tytul_pl:"Głosowanie przez pełnomocnika", tytul_en:"Voting by proxy",
  lekcje:[
   {id:"R3-L1", czas_min:5, tytul_pl:"Akt, spis, podpis", tytul_en:"The deed, the roll, the signature",
    elementy:[{typ:"pytanie",id:"wsp-R3-003",rola:"wspolna"},{typ:"pytanie",id:"czl-R3-001",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R3-006",rola:"czlonek_komisji"}]},
   {id:"R3-L2", czas_min:5, tytul_pl:"Kolizje i odmowy", tytul_en:"Collisions and refusals",
    elementy:[{typ:"pytanie",id:"czl-R3-002",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R3-004",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-R3-005",rola:"obserwator"},{typ:"pytanie",id:"wsp-R3-003",rola:"wspolna"}]}]},
 {id:"R4", etap:"D", czas_min:10, tytul_pl:"Wyborca prosi o pomoc", tytul_en:"A voter asks for help",
  lekcje:[
   {id:"R4-L1", czas_min:5, tytul_pl:"Kto może pomóc, a kto nie", tytul_en:"Who may help, and who may not",
    elementy:[{typ:"pytanie",id:"wsp-R4-001",rola:"wspolna"},{typ:"pytanie",id:"czl-R4-002",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R4-003",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-R4-005",rola:"obserwator"}]},
   {id:"R4-L2", czas_min:5, tytul_pl:"Informacja bez agitacji", tytul_en:"Information without campaigning",
    elementy:[{typ:"pytanie",id:"czl-R4-006",rola:"czlonek_komisji"},{typ:"pytanie",id:"wsp-R4-004",rola:"wspolna"},{typ:"pytanie",id:"obs-R4-005",rola:"obserwator"}]}]},
 {id:"R5", etap:"E", czas_min:10, tytul_pl:"Głosowanie na zaświadczenie", tytul_en:"Voting with a certificate",
  lekcje:[
   {id:"R5-L1", czas_min:5, tytul_pl:"Bilet jednorazowy", tytul_en:"A single-use ticket",
    elementy:[{typ:"pytanie",id:"wsp-R5-003",rola:"wspolna"},{typ:"pytanie",id:"czl-R5-001",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R5-002",rola:"czlonek_komisji"}]},
   {id:"R5-L2", czas_min:5, tytul_pl:"Spis: dopisać czy odmówić", tytul_en:"The roll: add or refuse",
    elementy:[{typ:"pytanie",id:"czl-R5-005",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R5-004",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-R5-006",rola:"obserwator"},{typ:"pytanie",id:"wsp-R5-003",rola:"wspolna"}]}]},
 {id:"R6", etap:"F", czas_min:10, tytul_pl:"Zamknięcie lokalu", tytul_en:"Closing of the polling station", uzyj_MIKRO:true},
 {id:"R7", etap:"G", czas_min:10, tytul_pl:"Rozliczenie kart", tytul_en:"Reconciling the ballots",
  lekcje:[
   {id:"R7-L1", czas_min:5, tytul_pl:"Wspólnie albo wcale", tytul_en:"Together or not at all",
    elementy:[{typ:"pytanie",id:"czl-R7-001",rola:"czlonek_komisji"},{typ:"pytanie",id:"wsp-R7-002",rola:"wspolna"},{typ:"pytanie",id:"obs-R7-006",rola:"obserwator"}]},
   {id:"R7-L2", czas_min:5, tytul_pl:"Plomby, urna, punkt 1", tytul_en:"Seals, the box, item 1",
    elementy:[{typ:"pytanie",id:"czl-R7-003",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R7-004",rola:"czlonek_komisji"},{typ:"pytanie",id:"czl-R7-005",rola:"czlonek_komisji"},{typ:"pytanie",id:"wsp-R7-002",rola:"wspolna"}]}]},
 {id:"R8", etap:"H", czas_min:10, tytul_pl:"Ustalenie wyników głosowania", tytul_en:"Establishing the results", bank_v1:true,
  lekcje:[
   {id:"R8-L1", czas_min:5, tytul_pl:"Ważna karta, ważny głos", tytul_en:"Valid ballot, valid vote",
    elementy:[{typ:"pytanie",id:"kom-ustalenie-001",rola:"czlonek_komisji"},{typ:"pytanie",id:"kom-ustalenie-002",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-ustalenie-001",rola:"obserwator"},{typ:"pytanie",id:"obs-ustalenie-002",rola:"obserwator"}]},
   {id:"R8-L2", czas_min:5, tytul_pl:"Protokół bez poprawek po fakcie", tytul_en:"A protocol without after-the-fact fixes",
    elementy:[{typ:"pytanie",id:"kom-ustalenie-003",rola:"czlonek_komisji"},{typ:"pytanie",id:"kom-ustalenie-004",rola:"czlonek_komisji"},{typ:"pytanie",id:"obs-ustalenie-003",rola:"obserwator"},{typ:"pytanie",id:"obs-ustalenie-004",rola:"obserwator"}]}]}
];
function mkRozdz(){
  const id=(state.test && state.test.mk && state.test.mk.rozdz) || "R6";
  const r=MIKRO_ROZDZIALY.filter(x=>x.id===id)[0] || MIKRO_ROZDZIALY[5];
  if(r.uzyj_MIKRO) return {id:r.id, etap:r.etap, czas_min:r.czas_min, tytul_pl:MIKRO.rozdzial.tytul_pl, tytul_en:MIKRO.rozdzial.tytul_en,
    zakres_pl:MIKRO.rozdzial.zakres_pl, zakres_en:MIKRO.rozdzial.zakres_en, lekcje:MIKRO.lekcje, bank_v1:false};
  const zak_pl = r.bank_v1
    ? "Lekcje dobierają pozycje z opublikowanego banku v1.0 (Ekspert 5, 2026-07-24); selekcję pod cele lekcji zatwierdza ekspert FOP. Pozostałe pozycje banku H dostępne w trybie testowym."
    : "Wsad do recenzji FOP (bank A–H, walidacja maszynowa 0 błędów / 0 ostrzeżeń; Wytyczne PKW 211/2023, stan 2023-09-25; art. 53 KW, stan 2023-03-31). Treść prawna żyje w pozycjach banku; zmiana pozycji flaguje elementy do re-recenzji.";
  const zak_en = r.bank_v1
    ? "Lessons draw on the published bank v1.0 (Expert 5, 2026-07-24); the selection is approved by an FOP expert. The remaining stage-H items are available in practice mode."
    : "Input pending FOP review (A–H bank, machine validation 0 errors / 0 warnings; NEC Guidelines 211/2023, as of 2023-09-25; Art. 53 of the Electoral Code, as of 2023-03-31). Legal content lives in bank items; a change flags elements for re-review.";
  return {id:r.id, etap:r.etap, czas_min:r.czas_min, tytul_pl:r.tytul_pl, tytul_en:r.tytul_en, zakres_pl:zak_pl, zakres_en:zak_en, lekcje:r.lekcje, bank_v1:!!r.bank_v1};
}
function mikroRozdzSel(id){ const m=state.test.mk; m.rozdz=id; m.phase="rola"; m.lekcja=null; render(); }
function rMikroRozdz(m){
  const tiles = MIKRO_ROZDZIALY.map(r=>{
    const status = r.uzyj_MIKRO ? mkT("w pilotażu — do recenzji","in the pilot — for review")
      : r.bank_v1 ? mkT("bank v1.0 — opublikowany","bank v1.0 — published")
      : mkT("wsad — do recenzji FOP","input — pending FOP review");
    return '<button class="tile" onclick="mikroRozdzSel(\''+r.id+'\')"><span class="t-k">'+esc(r.etap)+'</span><span class="t-t">'+esc(r.id)+' · '+esc(mkT(r.tytul_pl,r.tytul_en))+'</span><span class="t-d">'+r.czas_min+' min · '+esc(status)+'</span></button>';
  }).join("");
  return '<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · trzon dnia głosowania","Microlearning · election-day core"))+'</p>'+
    '<h2 class="screen-title">'+esc(mkT("Wybierz rozdział (A–H)","Choose a chapter (A–H)"))+'</h2>'+
    '<p class="screen-sub">'+esc(mkT("Osiem rozdziałów po 10 minut — po jednym na każdy etap dnia głosowania. Treść niezatwierdzona to propozycja silnika z widocznym statusem recenzji.","Eight 10-minute chapters — one per stage of election day. Unapproved content is an engine proposal with a visible review status."))+'</p>'+
    '<div class="tiles">'+tiles+'</div>'+
    '<div class="next-row" style="margin-top:14px"><button class="btn" onclick="testOpen()">'+esc(mkT("Wróć do wyboru trybu","Back to mode selection"))+'</button></div>';
}
'''

# --- wstrzyknięcie danych/funkcji przed mkT (początek bloku R6 z patcha 1) ---
rep('\nfunction mkT(pl,en){', DATA + '\nfunction mkT(pl,en){')

# --- trybSet: mikro startuje od wyboru rozdziału ---
rep('if(m==="mikro"){ t.mk={phase:"rola", rola:state.rola||null, lekcja:null, els:null, idx:0, pick:null, checked:false, answers:{}}; }',
    'if(m==="mikro"){ t.mk={phase:"rozdz", rozdz:null, rola:state.rola||null, lekcja:null, els:null, idx:0, pick:null, checked:false, answers:{}}; }')

# --- rMikro: dispatch fazy rozdziału ---
rep('''function rMikro(t){
  const m=t.mk||(t.mk={phase:"rola", rola:state.rola||null, lekcja:null, els:null, idx:0, pick:null, checked:false, answers:{}});
  if(m.phase==="rola") return rMikroWybor(m);''',
'''function rMikro(t){
  const m=t.mk||(t.mk={phase:"rozdz", rozdz:null, rola:state.rola||null, lekcja:null, els:null, idx:0, pick:null, checked:false, answers:{}});
  if(m.phase==="rozdz") return rMikroRozdz(m);
  if(m.phase==="rola") return rMikroWybor(m);''')

# --- mikroElems / mikroQ: rozdział bieżący zamiast sztywnego R6/F ---
rep('''function mikroElems(rola, lekcjaId){
  const L=MIKRO.lekcje.filter(x=>x.id===lekcjaId)[0]; if(!L) return [];''',
'''function mikroElems(rola, lekcjaId){
  const L=mkRozdz().lekcje.filter(x=>x.id===lekcjaId)[0]; if(!L) return [];''')

rep('''function mikroQ(rola,id){ return (QUIZY_PL[rola].F||[]).filter(q=>q.id===id)[0]||null; }''',
'''function mikroQ(rola,id){
  const e=mkRozdz().etap;
  let q=(QUIZY_PL[rola][e]||[]).filter(x=>x.id===id)[0]||null;
  if(!q && e==="H"){ const S = rola==="komisja" ? SRC_QUIZ_KOM : SRC_QUIZ_OBS; q=(S||[]).filter(x=>x.id===id)[0]||null; }
  return q;
}''')

# --- rMikroWybor: nagłówek z bieżącego rozdziału + powrót do rozdziałów ---
rep('function rMikroWybor(m){\n  const R=MIKRO.rozdzial;',
    'function rMikroWybor(m){\n  const R=mkRozdz();')
rep('''    lekcje='<div class="tiles">'+MIKRO.lekcje.map(L=>{''',
'''    lekcje='<div class="tiles">'+mkRozdz().lekcje.map(L=>{''')
rep('''  return '<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · rozdział R6","Microlearning · chapter R6"))+'</p>'+''',
'''  return '<p class="screen-eyebrow">'+esc(mkT("Mikro-learning · rozdział ","Microlearning · chapter ")+R.id+' ('+mkT("etap ","stage ")+R.etap+')')+'</p>'+''')
rep('''    '<div class="next-row" style="margin-top:14px"><button class="btn" onclick="testOpen()">'+esc(mkT("Wróć do wyboru trybu","Back to mode selection"))+'</button></div>';
}
function rMikroRun(m){''',
'''    '<div class="next-row" style="margin-top:14px"><button class="btn" onclick="(function(){state.test.mk.phase=\\'rozdz\\';render();})()">'+esc(mkT("Wróć do rozdziałów","Back to chapters"))+'</button> <button class="btn" onclick="testOpen()">'+esc(mkT("Wróć do wyboru trybu","Back to mode selection"))+'</button></div>';
}
function rMikroRun(m){''')

# --- rMikroRun: etap i lekcje bieżącego rozdziału; plakietka bank v1.0 dla R8 ---
# zamiany wewnątrz rMikroRun — segmentowo, bo anchory kolidują z rTestRunQuiz
i = src.find('function rMikroRun(')
j = src.find('function rMikroWynik(')
assert 0 < i < j
seg = src[i:j]
def srep(old, new):
    global seg
    assert seg.count(old) == 1, f'seg anchor x{seg.count(old)}: {old[:60]!r}'
    seg = seg.replace(old, new, 1)
srep("  const L=MIKRO.lekcje.filter(x=>x.id===m.lekcja)[0];\n  const head=",
     "  const RZ=mkRozdz();\n  const L=RZ.lekcje.filter(x=>x.id===m.lekcja)[0];\n  const head=")
srep('''  const rec=statusPozycji(m.rola,"F","quiz",q.id);''',
'''  let recChip;
  if(RZ.bank_v1){ recChip='<span class="schip opublikowane">'+esc(mkT("bank v1.0 · Ekspert 5 · 2026-07-24","bank v1.0 · Expert 5 · 2026-07-24"))+'</span>'; }
  else { recChip=statusChip(statusPozycji(m.rola,RZ.etap,"quiz",q.id)); }''')
srep('''<span class="qchip">'+esc(TYP[q.typ]||q.typ)+'</span>'+statusChip(rec)+'</div>'+''',
'''<span class="qchip">'+esc(TYP[q.typ]||q.typ)+'</span>'+recChip+'</div>'+''')
src = src[:i] + seg + src[j:]

# --- rMikroWynik: lekcja z bieżącego rozdziału ---
rep("function rMikroWynik(m){\n  const qids=m.els.filter(e=>e.typ===\"pytanie\").map(e=>e.id);\n  const ok=qids.filter(id=>m.answers[id]&&m.answers[id].ok).length;\n  const L=MIKRO.lekcje.filter(x=>x.id===m.lekcja)[0];",
    "function rMikroWynik(m){\n  const qids=m.els.filter(e=>e.typ===\"pytanie\").map(e=>e.id);\n  const ok=qids.filter(id=>m.answers[id]&&m.answers[id].ok).length;\n  const L=mkRozdz().lekcje.filter(x=>x.id===m.lekcja)[0];")
rep('''<button class="btn" onclick="mikroBack()">'+esc(mkT("Inna lekcja","Another lesson"))+'</button>'+''',
'''<button class="btn" onclick="mikroBack()">'+esc(mkT("Inna lekcja","Another lesson"))+'</button>'+
    '<button class="btn" onclick="(function(){state.test.mk.phase=\\'rozdz\\';state.test.mk.lekcja=null;render();})()">'+esc(mkT("Inny rozdział","Another chapter"))+'</button>'+''')

# --- panel Banku: zbiorczy przegląd rozdziałów przed panelem R6 ---
rep('''  return '<div class="bank-sec"><div class="bank-head"><span class="bk">R6</span><h3>'+esc(mkT("Mikrolearning — rozdział: ","Microlearning — chapter: ")+mkT(R.tytul_pl,R.tytul_en))+'</h3><span class="cn">'+R.czas_min+' min</span></div>'+''',
'''  const przeglad = MIKRO_ROZDZIALY.map(function(r){
    if(r.uzyj_MIKRO) return '<div class="b-item"><div class="b-row"><span class="tag">'+esc(r.etap)+'</span><b>'+esc(r.id)+' · '+esc(mkT(r.tytul_pl,r.tytul_en))+'</b><span class="schip niezatw">'+esc(mkT("w pilotażu — do recenzji","in the pilot — for review"))+'</span></div></div>';
    let n=0; const seen={};
    (r.lekcje||[]).forEach(L=>L.elementy.forEach(el=>{ if(!seen[el.id]){seen[el.id]=1;n++;} }));
    const chip = r.bank_v1 ? '<span class="schip opublikowane">'+esc(mkT("bank v1.0 — opublikowany","bank v1.0 — published"))+'</span>'
                           : '<span class="schip niezatw">'+esc(mkT("wsad — do recenzji FOP","input — pending FOP review"))+'</span>';
    return '<div class="b-item"><div class="b-row"><span class="tag">'+esc(r.etap)+'</span><b>'+esc(r.id)+' · '+esc(mkT(r.tytul_pl,r.tytul_en))+'</b><span class="tag">'+n+' '+esc(mkT("pozycji","items"))+'</span>'+chip+'</div></div>';
  }).join("");
  const sekcjaAH = '<div class="bank-sec"><div class="bank-head"><span class="bk">A–H</span><h3>'+esc(mkT("Mikrolearning — trzon dnia głosowania (R1–R8)","Microlearning — election-day core (R1–R8)"))+'</h3><span class="cn">80 min</span></div>'+
    '<div class="bank-body"><div class="b-meta" style="margin:0 0 10px">'+esc(mkT("Rozszerzenie zakresu pilotażu decyzją ownera v1 (2026-08-17). Pytania A–E i G: bank-mikrolearning-A-H.json (36 pozycji, walidacja 0/0, do recenzji). R8: pozycje opublikowanego banku v1.0. Zmiana pozycji banku flaguje elementy lekcji do re-recenzji.","Pilot scope extension by the v1 owner decision (2026-08-17). Stage A–E and G questions: bank-mikrolearning-A-H.json (36 items, validation 0/0, pending review). R8: items of the published bank v1.0. A bank item change flags lesson elements for re-review."))+'</div>'+przeglad+'</div></div>';
  return sekcjaAH + '<div class="bank-sec"><div class="bank-head"><span class="bk">R6</span><h3>'+esc(mkT("Mikrolearning — rozdział: ","Microlearning — chapter: ")+mkT(R.tytul_pl,R.tytul_en))+'</h3><span class="cn">'+R.czas_min+' min</span></div>'+''')

open(SRC, 'w', encoding='utf-8').write(src)
print(f'OK: {orig} -> {len(src)} bytes (+{len(src)-orig})')
