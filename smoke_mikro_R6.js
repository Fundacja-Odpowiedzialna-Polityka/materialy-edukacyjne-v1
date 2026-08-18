// smoke_mikro_R6.js — testy dymne po włączeniu mikrolearningu R6 do pilotażu
const fs = require('fs');
const html = fs.readFileSync('prototyp-FOP-PL-EN_04_08.html', 'utf-8');
const parts = html.split('<script>');
let src = parts[parts.length - 1].split('</script>')[0];

// hoisting state do globalThis (wzorzec harnessu)
src = src.replace('const state = {', 'globalThis.state = {');
for (const name of ['MIKRO_R6_Q','MIKRO','QUIZY_PL','QUIZY_EN','QUIZY','LISTY','ETAPY','MIKRO_AH_Q','MIKRO_FAZA_ETAP','MIKRO_ROZDZIALY','SRC_QUIZ_KOM','SRC_QUIZ_OBS','QMETA','LISTA','SCENY2','MIKRO_UNITS','LICZNIKI_DEF']) {
  src = src.replace('const ' + name + ' = ', 'globalThis.' + name + ' = ');
}

// mock DOM
const elProxy = () => new Proxy(function(){}, {
  get: (t, p) => {
    if (p === 'style') return new Proxy({}, { get: () => '', set: () => true });
    if (p === 'classList') return { add(){}, remove(){}, toggle(){}, contains(){ return false; } };
    if (p === 'innerHTML' || p === 'value' || p === 'textContent') return '';
    if (p === 'children') return [];
    if (p === Symbol.toPrimitive) return () => '';
    return typeof p === 'string' && /^[a-z]/i.test(p) ? (['addEventListener','setAttribute','appendChild','removeChild','focus','click','remove','scrollIntoView'].includes(p) ? () => {} : elProxy()) : undefined;
  },
  set: () => true,
  apply: () => elProxy()
});
global.window = global;
global.document = {
  documentElement: { setAttribute(){}, getAttribute(){ return null; } },
  getElementById: () => elProxy(),
  querySelector: () => elProxy(),
  querySelectorAll: () => [],
  createElement: () => elProxy(),
  addEventListener(){},
  body: elProxy(),
  title: ''
};
global.scrollTo = () => {};
global.setTimeout = fn => { fn(); return 0; };
global.location = { search: '', href: '' };
global.navigator = { language: 'pl' };
global.URL = { createObjectURL: () => 'blob:x', revokeObjectURL(){} };
global.Blob = function(){};
global.localStorage = { getItem: () => null, setItem(){}, removeItem(){} };

(0, eval)(src);

let fails = 0;
const t = (name, cond) => { console.log((cond ? 'PASS' : 'FAIL') + ' ' + name); if (!cond) fails++; };

// 1. Struktury danych
t('MIKRO zdefiniowane, rozdział R6', typeof MIKRO === 'object' && MIKRO.rozdzial.id === 'R6');
t('MIKRO_R6_Q ma 8 pozycji', Array.isArray(MIKRO_R6_Q) && MIKRO_R6_Q.length === 8);
t('każda pozycja R6 ma jednostkę i stan prawny (zero zgadywania)', MIKRO_R6_Q.every(q => q.zrodlo && /pkt \d+/.test(q.zrodlo.jednostka) && q.zrodlo.stan_prawny === '2023-09-25'));

// 2. Wstrzyknięcie do QUIZY_PL (kolejność: R6 na początku)
const komF = QUIZY_PL.komisja.F, obsF = QUIZY_PL.obserwator.F;
t('komisja.F: 36 pozycji (6 R6 + 30 roboczych)', komF.length === 36);
t('obserwator.F: 34 pozycje (4 R6 + 30 roboczych)', obsF.length === 34);
t('komisja.F zaczyna się od wsp-R6-001', komF[0].id === 'wsp-R6-001');
t('komisja.F zawiera czl-R6-002..005', ['czl-R6-002','czl-R6-003','czl-R6-004','czl-R6-005'].every(id => komF.some(q => q.id === id)));
t('obserwator.F zawiera obs-R6-006/007 i wsp-R6-008', ['obs-R6-006','obs-R6-007','wsp-R6-008'].every(id => obsF.some(q => q.id === id)));
t('brak duplikatów id w komisja.F', new Set(komF.map(q => q.id)).size === komF.length);

// 3. Zakres i silnik
t('inScope(komisja,F,quiz) = true', inScope('komisja','F','quiz') === true);
t('inScope(obserwator,F,quiz) = true', inScope('obserwator','F','quiz') === true);
t('qset zwraca pozycje R6', qset('komisja','F')[0].id === 'wsp-R6-001');
t('zakresOpis liczy F (36)', zakresOpis().includes('F (36)'));

// 4. Panel mikrolearningu — status przed recenzją
const p1 = mikroPanel();
t('mikroPanel renderuje rozdział R6', typeof p1 === 'string' && p1.includes('Mikrolearning') && p1.includes('R6-L1') && p1.includes('R6-L2'));
t('elementy przed recenzją mają status niezatw', p1.includes('przed recenzją FOP') && p1.includes('schip niezatw'));
t('sceny V2 z linkami wsad_v1', p1.includes('SC-R6-01') && p1.includes('wsad_v1: kom-F-001'));
t('job aid kom-F-001..004 widoczny', p1.includes('kom-F-004'));

// 5. Bramka ludzka: po publikacji status w panelu się zmienia
state.bank.push({uid:'x', id:'wsp-R6-001', rola:'komisja', etap:'F', typ:'quiz', status:'opublikowane', wersja:'v1.0', data:'2026-08-17', owner:'Ekspert 5', uwagi:null, tagi:[], payload:MIKRO_R6_Q[0]});
const p2 = mikroPanel();
t('po decyzji TAK element pokazuje zatwierdzone v1.0', p2.includes('wsp-R6-001 · zatwierdzone v1.0'));
t('pozostałe elementy wciąż przed recenzją', p2.includes('czl-R6-002 · przed recenzją FOP'));

// 6. rBank zawiera panel; render pełnego ekranu nie rzuca wyjątku
state.bank.pop();
let bankHtml = '';
try { bankHtml = rBank(); } catch (e) { console.log('rBank threw: ' + e.message); }
t('rBank zawiera panel mikrolearningu', bankHtml.includes('Mikrolearning'));
try { state.screen = 'bank'; render(); t('render(bank) bez wyjątku', true); } catch (e) { t('render(bank) bez wyjątku: ' + e.message, false); }

// 7. EN: etykiety panelu tłumaczone
// LANG jest const w skrypcie — test mkT pośrednio przez strukturę
t('MIKRO ma etykiety EN', MIKRO.rozdzial.tytul_en.length > 0 && MIKRO.sceny.every(s => s.status_en));

console.log(fails === 0 ? '\nALL PASS (dane+bank)' : '\n' + fails + ' FAILURES');
if (fails > 0) process.exit(1);

// ==== TESTY TRYBU: ekran wyboru + runner mikrolearningu ====
let f2 = 0;
const t2 = (name, cond) => { console.log((cond ? 'PASS' : 'FAIL') + ' ' + name); if (!cond) f2++; };

testOpen();
const chooser = rTest();
t2('ekran wyboru trybu z dwiema opcjami', chooser.includes('Tryb testowy — testuj pytania') && chooser.includes('Mikro-learning') && chooser.includes("trybSet('test')") && chooser.includes("trybSet('mikro')"));

// stary tryb testowy nadal działa
trybSet('test');
t2('trybSet(test) -> ekran wyboru zestawów', rTest().includes('chips'));
testRola('komisja');
testSel('F','quiz');
t2('testSel F/quiz -> karta zestawu (36 poz.)', state.test.phase==='karta' && state.test.set.items.length===36);

// mikro: wybór roli i lekcji
testOpen(); trybSet('mikro'); mikroRozdzSel('R6');
let h = rTest();
t2('mikro: ekran rozdziału R6 z rolami', h.includes('Zamknięcie lokalu') && h.includes("mikroRola('komisja')"));
mikroRola('komisja');
h = rTest();
// jednostka F / komisja: stara scena + 5 pytań (nowy model)
mikroRola('komisja'); mikroUnit();
t2('F/komisja: jednostka scena+5 pytań(+dnd)', state.test.mk.els[0].typ==='scena' && state.test.mk.els.filter(e=>e.typ==='pytanie').length===5);
// przejdź scenę SC-R6-01 minimalnie: 6 kroków starego runnera
mikroScNext(); mikroScPick(0); mikroScCheck(); mikroScNext(); mikroScNext(); mikroScPick(0); mikroScCheck(); mikroScNext(); mikroScNext(); mikroScNext();
t2('po starej scenie: pytanie 1/5', state.test.mk.idx===1 && state.test.mk.els[1].typ==='pytanie');
let h2=rTest();
t2('runner pytań działa w jednostce', h2.includes('Sprawdź'));
mikroPick(1); mikroCheck();
h2=rTest();
t2('feedback z uzasadnieniem dystraktora lub kotwicą', h2.includes('Źródło:')||h2.includes('pkt'));
const full=src;
t2('etykieta górnego przycisku zmieniona (PL/EN)', full.includes('"Tryb testowy i Mikro-learning", "Practice mode & Microlearning"'));
t2('przycisk startowy zmieniony', full.includes('Przejdź do trybu testowego i mikro-learningu'));
t2('testFromBank ustawia mode=test', full.includes('state.test={mode:"test", phase:"karta"'));

console.log(f2 === 0 ? 'ALL PASS (tryb+mikro)' : f2 + ' FAILURES (tryb+mikro)');
if (f2 > 0) process.exitCode = 1;


// ==== TESTY SCEN INTERAKTYWNYCH ====
let f3 = 0;
const t3 = (name, cond) => { console.log((cond ? 'PASS' : 'FAIL') + ' ' + name); if (!cond) f3++; };

// --- L2 / komisja (Tomasz): SC-R6-01 (6 kroków: n, d, n, d, d-alt, n) -> wsp-R6-008 -> SC-R6-02 (5 kroków) ---
testOpen(); trybSet('mikro'); mikroRozdzSel('R6'); mikroRola('komisja'); mikroLekcja('R6-L2');
let sh = rTest();
t3('SC-R6-01 krok 1/6: narracja z badge do recenzji', sh.includes('Krok 1 / 6') && sh.includes('rama fikcyjna — do recenzji') && sh.includes('Wielichowie'));
mikroScNext();
sh = rTest();
t3('krok 2: decyzja Tomasza (kolejka) z 3 opcjami', sh.includes('zamknijmy listę') && sh.includes('mikroScPick(2)'));
mikroScCheck(); // guard: bez wyboru -> toast, bez zaliczenia
t3('guard: check bez wyboru nie liczy decyzji', (state.test.mk.scN||0) === 0);
mikroScPick(1); mikroScCheck(); // błędna: odesłać kolejkę
sh = rTest();
t3('feedback błędny z kotwicą wsp-R6-001+czl-R6-002 pkt 97', sh.includes('Niepoprawnie.') && sh.includes('wsp-R6-001, czl-R6-002') && sh.includes('pkt 97'));
mikroScNext(); // n2 Zbigniew
mikroScPick(0); t3('guard: pick na narracji ignorowany', state.test.mk.sc.pick === null);
mikroScNext(); // d2
mikroScPick(0); mikroScCheck();
sh = rTest();
t3('decyzja 2 poprawna, kotwica czl-R6-002', sh.includes('Poprawnie.') && sh.includes('czl-R6-002'));
mikroScNext(); // d3 obserwatora -> alt dla komisji
sh = rTest();
t3('decyzja Anny jako narracja alt (bez przycisku Sprawdź)', sh.includes('Anna nie włącza się') && !sh.includes('mikroScCheck'));
mikroScCheck(); t3('guard: check na kroku alt nie liczy decyzji', state.test.mk.scN === 2);
mikroScNext(); // n3 domknięcie
sh = rTest();
t3('domknięcie cytuje kom-F-001', sh.includes('kom-F-001'));
mikroScNext(); // koniec sceny -> element 2 (wsp-R6-008)
t3('po scenie: element 2, sc wyzerowany, decyzje 1/2', state.test.mk.idx===1 && state.test.mk.sc===null && state.test.mk.scOk===1 && state.test.mk.scN===2);
mikroPick(0); mikroCheck(); mikroNext(); // wsp-R6-008 ok
sh = rTest();
// SC-R6-02: pozostaje w rejestrze scen (warianty ról), poza przebiegiem jednostki
t3('rejestr: SC-R6-02 z wariantami rol', (MIKRO.sceny||[]).some(sc=>sc.id==='SC-R6-02'));
console.log(f3===0?'ALL PASS (sceny)':f3+' FAILURES (sceny)');
if(f3>0) process.exitCode=1;

// ==== TESTY JEDNOSTEK v2, BEATÓW, DND, KREATORA, KORALIKÓW ====
let f9=0; const t9=(n,c)=>{ console.log((c?'PASS ':'FAIL ')+n); if(!c) f9++; };

// dane scen
t9('SCENY2: 15 scen, 3 kurs + 12 silnik', SCENY2.length===15 && SCENY2.filter(s=>s.zrodlo==='kurs').length===3);
t9('MIKRO_UNITS: 8 etapów × 2 role', Object.keys(MIKRO_UNITS).length===8 && Object.values(MIKRO_UNITS).every(u=>u.komisja&&u.obserwator));
t9('sceny silnika: 4 opcje i 1 best per beat', SCENY2.filter(s=>s.zrodlo==='silnik').every(s=>s.beats.every(b=>b.options.length===4 && b.options.filter(o=>o['class']==='best').length===1)));

// koraliki unit
const kk = koraliki(['ok','bad','cur',''], 2, 4);
t9('koraliki(): 4 kropki, licznik 2/4', (kk.match(/class="seg[ "]/g)||[]).length===4 && kk.includes('2/4'));

// jednostka A / komisja: scena A-PSC (silnik, liczniki) -> 5 pytań -> DnD -> wynik
testOpen(); trybSet('mikro'); mikroRozdzSel('R1'); mikroRola('komisja'); mikroUnit();
let mU=state.test.mk;
t9("jednostka A/komisja: scena2 + 5 pytań + dnd", mU.els.length===7 && mU.els[0].typ==='scena2' && mU.els[6].typ==='dnd');
let hU=rTest();
t9('karta otwarcia sceny z pochodzeniem silnika', hU.includes('Rozpocznij scenę') && hU.includes('silnik'));
state.test.mk.b.step=0; hU=rTest();
t9('beat 1: 4 opcje, liczniki 100', (hU.match(/sc2Pick\(/g)||[]).length===4 && hU.includes('Zaufanie wyborców: 100'));
// wybór best (indeks 0 w danych; klik przez oryginalny indeks)
sc2Pick(0); sc2Check(); hU=rTest();
t9('feedback best + źródło pkt 39', hU.includes('pkt 39') && state.test.mk.scOk===1);
sc2Next(); sc2Pick(3); sc2Check();
t9('opcja incorrect obniża liczniki', state.test.mk.b.meters.trust===85 && state.test.mk.b.meters.third===90);
sc2Next(); sc2Pick(1); sc2Check(); sc2Next(); // beat 3
hU=rTest();
t9('karta zamknięcia sceny', hU.includes('Zamknięcie sceny'));
sc2Next();
t9('po scenie: pytanie 1/5', state.test.mk.idx===1 && state.test.mk.els[1].typ==='pytanie');
for(let q=0;q<5;q++){ mikroPick(0); mikroCheck(); mikroNext(); }
t9('po pytaniach: element DnD', state.test.mk.els[state.test.mk.idx].typ==='dnd');
hU=rTest();
t9('DnD renderuje 6 pozycji ze strzałkami', (hU.match(/dndMove\(/g)||[]).length===12);
// ułóż poprawnie: sortuj ord rosnąco
state.test.mk.dnd.ord.sort((a,b)=>a-b); dndCheck();
hU=rTest();
t9('DnD: 6/6 na miejscu', hU.includes('6 / 6'));
(function(){ state.test.mk.dnd=null; mikroNext(); })();
t9('wynik jednostki z linią DnD', state.test.mk.phase==='wynik' && rTest().includes('Ułożenie listy'));

// critical replay: C-PSC beat 2 opcja d (critical)
testOpen(); trybSet('mikro'); mikroRozdzSel('R3'); mikroRola('komisja'); mikroUnit();
state.test.mk.b={id:'C-PSC', step:1, pick:null, checked:false, ord:null, ordBeat:null, closed:false, meters:{trust:100,time:100,third:100}};
sc2Pick(3); sc2Check(); hU=rTest();
t9('critical: komunikat powtórki i kara -25', hU.includes('powtórzony') && state.test.mk.b.meters.trust===75);
sc2Next();
t9('critical: beat powtórzony (nie przeszedł dalej)', state.test.mk.b.step===1 && state.test.mk.b.checked===false);

// jednostka A / obserwator: scena kursu SC-RA-01 (bez liczników, kroki narracyjne)
testOpen(); trybSet('mikro'); mikroRozdzSel('R1'); mikroRola('obserwator'); mikroUnit();
t9('A/obs: scena kursu SC-RA-01', state.test.mk.els[0].id==='SC-RA-01');
state.test.mk.b={id:'SC-RA-01', step:0, pick:null, checked:false, ord:null, ordBeat:null, closed:false, meters:{trust:100,time:100,third:100}};
hU=rTest();
t9('krok narracyjny bez opcji, chip kurs', hU.includes('źródło: kurs FOP') && !hU.includes('sc2Pick(') && hU.includes('Dalej'));
t9('bez liczników dla sceny kursu', !hU.includes('Zaufanie: 100'));
sc2Next(); hU=rTest();
t9('beat decyzyjny kursu: 2 opcje 1:1', (hU.match(/sc2Pick\(/g)||[]).length===2 && hU.includes('wyciągnęłam'));

// jednostka F: stara scena SC-R6-01 przez typ "scena"
testOpen(); trybSet('mikro'); mikroRozdzSel('R6'); mikroRola('komisja'); mikroUnit();
t9('F: jednostka używa SC-R6-01 (stary format)', state.test.mk.els[0].typ==='scena' && state.test.mk.els[0].id==='SC-R6-01');
hU=rTest();
t9('stary runner scen działa w jednostce', hU.includes('SC-R6-01'));

// jednostka H: pytania z banku v1.0
testOpen(); trybSet('mikro'); mikroRozdzSel('R8'); mikroRola('obserwator'); mikroUnit();
const qidsH=state.test.mk.els.filter(e=>e.typ==='pytanie').map(e=>e.id);
t9('H/obs: 5 pytań, w tym bank v1.0', qidsH.length===5 && qidsH.includes('obs-ustalenie-001'));

// kreator scenek: scope + generacja + recenzja + publikacja
state.rola='komisja'; state.etap='G'; state.material='scenka';
t9('inScope scenka G/komisja', inScope('komisja','G','scenka')===true);
buildSession();
t9('sesja scenki: 1 pozycja G-PSC', state.session.items.length===1 && state.session.items[0].id==='G-PSC');
state.rFilter='all';
try{ hU=rRecenzja(); }catch(e){ console.log('rRecenzja ERR: '+e.message); hU=''; }
t9('karta recenzji scenki: beaty + klasy + źródło do weryfikacji flagi', hU.includes('Beat 1') && hU.includes('best') && hU.includes('pkt 112'));
setDecision('G-PSC','TAK');
t9('decyzja TAK zapisana', state.session.decisions['G-PSC'].decyzja==='TAK');
// publikacja standardowym torem
publish();
const wBanku = state.bank.filter(b=>b.id==='G-PSC');
t9('scenka opublikowana do banku', wBanku.length>=1 && wBanku[0].status==='opublikowane');
const chip=statusPozycji('komisja','G','scenka','G-PSC');
t9('statusPozycji widzi scenkę w mikro', !!chip && chip.status==='opublikowane');

// panel banku: rejestr scen
const bpU=mikroPanel();
t9('panel banku: rejestr 15 scen z pochodzeniem', bpU.includes("Sceny interaktywne") && bpU.includes('A-PSC') && bpU.includes('kurs'));

console.log(f9===0 ? 'ALL PASS (jednostki v2)' : f9+' FAILURES (jednostki v2)');
if(f9>0) process.exitCode=1;
