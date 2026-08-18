// smoke_mikro_R6.js — testy dymne po włączeniu mikrolearningu R6 do pilotażu
const fs = require('fs');
const html = fs.readFileSync('prototyp-FOP-PL-EN_04_08.html', 'utf-8');
const parts = html.split('<script>');
let src = parts[parts.length - 1].split('</script>')[0];

// hoisting state do globalThis (wzorzec harnessu)
src = src.replace('const state = {', 'globalThis.state = {');
for (const name of ['MIKRO_R6_Q','MIKRO','QUIZY_PL','QUIZY_EN','QUIZY','LISTY','ETAPY','MIKRO_AH_Q','MIKRO_FAZA_ETAP','MIKRO_ROZDZIALY','SRC_QUIZ_KOM','SRC_QUIZ_OBS']) {
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
t2('mikro: lekcje widoczne po wyborze roli', h.includes('R6-L1') && h.includes('R6-L2'));

// lekcja L1 dla komisji: 5 pytań (wsp+4 czl), bez obs-R6-006
mikroLekcja('R6-L1');
const m = state.test.mk;
t2('L1/komisja: 5 elementów, start od wsp-R6-001', m.els.length===5 && m.els[0].id==='wsp-R6-001' && !m.els.some(e=>e.id==='obs-R6-006'));
h = rTest();
t2('runner pokazuje pytanie T/F ze statusem recenzji', h.includes('Wyborcy, którzy o godzinie 21:00') && h.includes('niezatwierdzona propozycja') || h.includes('schip'));
mikroPick(1); mikroCheck();
h = rTest();
t2('feedback poprawny z cytatem pkt 97', h.includes('Poprawnie.') && h.includes('pkt 97'));
mikroNext(); mikroPick(0); mikroCheck(); mikroNext(); // czl-R6-002 ok
mikroPick(1); mikroCheck(); // czl-R6-003 źle
h = rTest();
t2('feedback błędny z uzasadnieniem dystraktora', h.includes('Niepoprawnie.') && h.includes('pułapka'));
mikroNext(); mikroPick(0); mikroCheck(); mikroNext(); mikroPick(0); mikroCheck(); mikroNext();
t2('wynik lekcji: 4/5', state.test.mk.phase==='wynik' && rTest().includes('4 / 5'));

// L2 dla Anny: scena -> pytania -> scena
mikroBack(); mikroRola('obserwator'); mikroLekcja('R6-L2');
const m2 = state.test.mk;
t2('L2/obserwator: 4 elementy, sceny na pozycjach 1 i 4', m2.els.length===4 && m2.els[0].id==='SC-R6-01' && m2.els[3].id==='SC-R6-02');
h = rTest();
t2('scena interaktywna: krok 1 z wsad_v1 i mikroScNext', h.includes('SC-R6-01') && h.includes('wsad_v1: kom-F-001') && h.includes('mikroScNext()'));
mikroNext();
h = rTest();
t2('po scenie pytanie obs-R6-007', h.includes('Rozpoznaj, jakie jest prawo Anny'));

// etykiety przycisków
const full = fs.readFileSync('prototyp-FOP-PL-EN_04_08.html','utf-8');
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
t3('SC-R6-02 wariant komisji: intro 21:20, 5 kroków', sh.includes('21:20') && sh.includes('Krok 1 / 5'));
mikroScNext(); mikroScPick(0); mikroScCheck();
sh = rTest();
t3('d1: kotwica kom-F-003 pkt 99–100', sh.includes('kom-F-003') && sh.includes('99'));
mikroScNext(); mikroScPick(0); mikroScCheck(); mikroScNext(); // d2 ok
mikroScPick(2); mikroScCheck(); // d3 błędna (liczyć karty)
sh = rTest();
t3('d3 błędna: feedback z obs-R6-007', sh.includes('nie wykonuje') && sh.includes('obs-R6-007'));
mikroScNext(); mikroScNext(); // n domknięcie -> koniec sceny -> wynik
sh = rTest();
t3('wynik L2 komisji: pytania 1/1, decyzje scen 3/5', state.test.mk.phase==='wynik' && sh.includes('Decyzje w scenach: ') && state.test.mk.scOk===3 && state.test.mk.scN===5);

// --- L2 / obserwator (Anna) ---
testOpen(); trybSet('mikro'); mikroRozdzSel('R6'); mikroRola('obserwator'); mikroLekcja('R6-L2');
mikroScNext(); // krok2: d-kom alt
sh = rTest();
t3('SC-R6-01/Anna: decyzja komisji jako alt', sh.includes('Komisja zamyka drzwi dla nowych') && !sh.includes('mikroScCheck'));
mikroScNext(); mikroScNext(); // n2 -> d2-kom alt... krok4
mikroScNext(); // krok5: d-obs (szepcze)
sh = rTest();
t3('SC-R6-01/Anna: jej decyzja aktywna', sh.includes('szepcze') && sh.includes('mikroScCheck'));
mikroScPick(0); mikroScCheck();
sh = rTest();
t3('kotwica obs-R6-006 w feedbacku Anny', sh.includes('Poprawnie.') && sh.includes('obs-R6-006'));
mikroScNext(); mikroScNext(); // n3 -> koniec sceny -> obs-R6-007
t3('po scenie pytanie obs-R6-007', state.test.mk.els[state.test.mk.idx].id==='obs-R6-007');
mikroPick(0); mikroCheck(); mikroNext();
mikroPick(0); mikroCheck(); mikroNext(); // wsp-R6-008
sh = rTest();
t3('SC-R6-02/Anna: wariant obserwatora', sh.includes('oczami Anny') && sh.includes('Krok 1 / 5'));
mikroScNext(); mikroScPick(0); mikroScCheck(); // d1 obecność
sh = rTest();
t3('d1: kotwica obs-R6-007', sh.includes('obs-R6-007'));
mikroScNext(); mikroScPick(0); mikroScCheck(); mikroScNext(); // d2 notowanie
mikroScPick(0); mikroScCheck(); // d3 kamera
sh = rTest();
t3('d3 kamera: flaga [DO UZUPEŁNIENIA] w feedbacku', sh.includes('DO UZUPEŁNIENIA'));
mikroScNext(); mikroScNext(); // n -> wynik
sh = rTest();
t3('wynik Anny: decyzje 4/4 (1 z SC-01 + 3 z SC-02)', state.test.mk.phase==='wynik' && state.test.mk.scOk===4 && state.test.mk.scN===4);

// --- panel banku ---
const bp = mikroPanel();
t3('panel banku: sceny interaktywne z liczbą kroków', bp.includes('scena interaktywna') && bp.includes('kroków'));

console.log(f3 === 0 ? 'ALL PASS (sceny)' : f3 + ' FAILURES (sceny)');
if (f3 > 0) process.exitCode = 1;

// ==== TESTY A–H: rozdziały, wstrzyknięcia, R8 z banku v1.0 ====
let f4 = 0;
const t4 = (name, cond) => { console.log((cond ? 'PASS' : 'FAIL') + ' ' + name); if (!cond) f4++; };

// wstrzyknięcia do QUIZY_PL
t4('MIKRO_AH_Q: 36 pozycji z kotwicami', MIKRO_AH_Q.length===36 && MIKRO_AH_Q.every(q=>q.zrodlo && q.zrodlo.jednostka && q.zrodlo.stan_prawny));
t4('A: komisja 30->35, obserwator 30->33', QUIZY_PL.komisja.A.length===35 && QUIZY_PL.obserwator.A.length===33);
t4('B: komisja 10->15, obserwator 10->12', QUIZY_PL.komisja.B.length===15 && QUIZY_PL.obserwator.B.length===12);
t4('G: komisja 30->35, obserwator 30->32', QUIZY_PL.komisja.G.length===35 && QUIZY_PL.obserwator.G.length===32);
t4('zakresOpis: A (35) i G (35)', zakresOpis().includes('A (35)') && zakresOpis().includes('G (35)'));

// ekran rozdziałów
testOpen(); trybSet('mikro');
let hh = rTest();
t4('grid 8 rozdziałów z etapami A–H', ['R1','R2','R3','R4','R5','R6','R7','R8'].every(r=>hh.includes("mikroRozdzSel('"+r+"')")));
t4('R8 oznaczony jako bank v1.0', hh.includes('bank v1.0'));

// R3 / komisja / L2 — pytanie z realną kotwicą pkt 59
mikroRozdzSel('R3'); mikroRola('komisja'); mikroLekcja('R3-L2');
t4('R3-L2/komisja: 3 elementy (bez obs)', state.test.mk.els.length===3 && !state.test.mk.els.some(e=>e.id==='obs-R3-005'));
hh = rTest();
t4('pytanie czl-R3-002 renderuje się', hh.includes('pełnomocnik') || hh.includes('Pełnomocnik') || hh.includes('pełnomocnictwa'));
mikroPick(0); mikroCheck();
hh = rTest();
t4('feedback z kotwicą pkt 59', hh.includes('pkt 59') && hh.includes('2023-09-25'));

// R8 / obserwator — pozycja z SRC_QUIZ_OBS + statyczna plakietka
testOpen(); trybSet('mikro'); mikroRozdzSel('R8'); mikroRola('obserwator'); mikroLekcja('R8-L1');
t4('R8-L1/obserwator: 2 elementy obs', state.test.mk.els.length===2 && state.test.mk.els[0].id==='obs-ustalenie-001');
hh = rTest();
t4('plakietka bank v1.0 · Ekspert 5', hh.includes('bank v1.0 · Ekspert 5 · 2026-07-24'));
mikroPick(0); mikroCheck();
hh = rTest();
t4('feedback pozycji banku H ze źródłem', hh.includes('Źródło:'));
mikroNext(); mikroPick(0); mikroCheck(); mikroNext();
t4('wynik R8-L1 osiągnięty', state.test.mk.phase==='wynik');
hh = rTest();
t4('wynik ma przycisk Inny rozdział', hh.includes('Inny rozdział'));

// R6 wciąż działa przez nowy ekran (regresja pełnego przejścia była wyżej)
testOpen(); trybSet('mikro'); mikroRozdzSel('R6'); mikroRola('komisja');
hh = rTest();
t4('R6 przez grid: lekcje R6-L1/L2 widoczne', hh.includes('R6-L1') && hh.includes('R6-L2'));

// panel banku: sekcja A–H + szczegóły R6
const bp2 = mikroPanel();
t4('panel banku: sekcja R1–R8 + statusy', bp2.includes('R1 ·') && bp2.includes('R8 ·') && bp2.includes('bank v1.0') && bp2.includes('Mikrolearning'));

console.log(f4 === 0 ? 'ALL PASS (A–H)' : f4 + ' FAILURES (A–H)');
if (f4 > 0) process.exitCode = 1;
