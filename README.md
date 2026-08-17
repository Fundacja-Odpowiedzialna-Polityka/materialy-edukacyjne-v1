# Odporna Demokracja — silnik treści mikrolearningu (prototyp v1)

Klikalny prototyp panelu administratora Fundacji Odpowiedzialna Polityka: AI proponuje wsad (listy kontrolne, pytania, mikrolearning R6) → recenzja eksperta FOP (bramka ludzka TAK/POPRAW/USUŃ) → publikacja z wersją, datą i ownerem. Zawiera tryb testowy i mikro-learning (rozdział R6 z interaktywnymi scenami).

## Uruchomienie
Jeden samodzielny plik: otwórz `index.html` w przeglądarce albo wejdź na URL live (Vercel). Stan sesji tylko w pamięci przeglądarki — eksport przez „Eksport JSON".

- **URL live:** _[uzupełnić po deployu]_
- **Owner produktu (v1):** Carlos (karol@odpowiedzialnapolityka.pl)
- **Partner:** Tech To The Rescue · AI Impact Lab

## Test happy path
1. Wybierz eksperta → odbiorcę → etap F → quiz → „Generuj propozycję wsadu".
2. Oceń wszystkie pozycje (TAK/POPRAW/USUŃ z uzasadnieniami) → „Zatwierdź recenzję i opublikuj" → CSV-y dowodu recenzji.
3. „Tryb testowy i Mikro-learning" → Mikro-learning → rola → lekcja R6 → pytania i sceny z kotwicami prawnymi.

## Znane ograniczenia
- Dane pilotażowe: Wytyczne PKW 211/2023 (stan 2023-09-25) + Kodeks wyborczy (stan 2023-03-31); wybory 15.10.2023.
- Aplikacja pokazuje także treści **niezatwierdzone** (propozycje silnika) — zawsze z widoczną plakietką statusu recenzji. Nie stanowią materiału szkoleniowego.
- Sceny mikrolearningu: rama fikcyjna do recenzji (owner scen: Dominika); dwa `[DO UZUPEŁNIENIA]` opisane w treści.
- Brak zapisu po stronie serwera; brak logowania; brak danych osobowych.

## Warunek STOP
Publikacja wytycznych PKW 2027 → re-recenzja banku R6 i scen przed dalszym użyciem treści.
