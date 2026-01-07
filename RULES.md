# rules.md

## 1. Cel dokumentu

Plik `rules.md` definiuje **niezmienne zasady projektu**, które obowiązują:

* podczas generowania kodu (np. przez Claude),
* podczas dalszego rozwoju aplikacji,
* przy refaktoryzacji i rozbudowie funkcjonalnej.

Jeśli nowa funkcja lub zmiana **łamie którąkolwiek z tych zasad**, oznacza to błąd projektowy.

---

## 2. Zasady nadrzędne

### R1. Brak doradztwa podatkowego

Aplikacja:

* ma charakter **informacyjny i symulacyjny**,
* nie wydaje zaleceń prawnych ani podatkowych,
* nie zastępuje księgowego ani interpretacji indywidualnej.

W kodzie i UI **nie wolno używać** sformułowań typu:

* „należy”, „musisz”, „powinieneś”,
* „najlepszy wybór”, „jedyna poprawna opcja”.

---

### R2. Matematyka ponad interpretacją

* Wyniki aplikacji są efektem **jawnych obliczeń matematycznych**.
* Każda liczba musi wynikać z:

  * danych wejściowych użytkownika,
  * stałych zdefiniowanych w kodzie.

Zakazane jest:

* ukrywanie założeń,
* heurystyki bez wyjaśnienia,
* „inteligentne” zgadywanie danych.

---

## 3. Zasady architektoniczne

### R3. Rozdzielenie odpowiedzialności

* `domain/`:

  * czysta logika podatkowa,
  * brak FastAPI, baz danych, JSON.
* `services/`:

  * składanie scenariuszy,
  * brak szczegółowych wzorów podatkowych.
* `api/`:

  * walidacja i mapowanie HTTP,
  * brak logiki biznesowej.

Złamanie tej zasady = błąd architektury.

---

### R4. Domain nie zależy od niczego

* Warstwa `domain/`:

  * nie importuje żadnych bibliotek webowych,
  * nie zna pojęć request/response,
  * nie operuje na JSON.

Domain musi być możliwy do uruchomienia i przetestowania **w izolacji**.

---

## 4. Zasady czasowe

### R5. Jednostka czasu = miesiąc

* Wszystkie obliczenia operują na **miesiącach**.
* Brak miesięcy zerowych.
* Oś czasu zaczyna się od **miesiąca bazowego**.

---

### R6. Stałość przepisów

* Przepisy są **zamrożone na rok podatkowy 2025**.
* Brak automatycznych zmian prawa w czasie.
* Wszystkie stałe i progi:

  * w jednym module (`constants_2025.py`).

---

## 5. ZUS i składki

### R7. Automatyczne etapy ZUS

* Użytkownik podaje **datę rozpoczęcia działalności**.
* System sam określa:

  * ulgę na start,
  * preferencyjny ZUS,
  * pełny ZUS,
    **dla każdego miesiąca**.

Brak ręcznego wyboru ZUS w v1.0.

---

### R8. Składka zdrowotna

* Składka zdrowotna liczona:

  * **rocznie**.
* Na potrzeby wizualizacji:

  * rozbijana proporcjonalnie na miesiące.

---

## 6. Dane finansowe

### R9. Precyzja obliczeń

* Waluta: PLN.
* Obliczenia:

  * `Decimal`.
* Prezentacja:

  * 2 miejsca po przecinku.
* Zaokrąglenia:

  * matematyczne,
  * tylko na końcu obliczeń.

---

### R10. Koszty

* Aplikacja:

  * **nie kwalifikuje kosztów**,
  * nie ocenia ich zasadności.
* Koszty:

  * uwzględniane w skali i liniowym,
  * ignorowane w ryczałcie.

---

## 7. Frontend

### R11. Prostota ponad efekciarstwo

* Brak frameworków JS.
* HTML + CSS + Vanilla JS.
* Jedyna biblioteka JS: **Chart.js**.

Frontend:

* nie liczy podatków,
* nie interpretuje danych,
* tylko renderuje odpowiedź API.

---

## 8. Testy i jakość

### R12. Testowalność

* Testy jednostkowe:

  * tylko dla `domain/`.
* Każda funkcja domenowa:

  * deterministyczna,
  * testowalna bez mocków.

---

## 9. Rozszerzenia w przyszłości

### R13. AI jako warstwa opcjonalna

* AI może zostać dodane wyłącznie jako:

  * warstwa interpretacyjna,
  * bez wpływu na `domain/`.

AI:

* nie zmienia wyników obliczeń,
* nie podejmuje decyzji podatkowych.

### R14. Docker jako narzędzie, nie zależność

* Docker:
  * służy wyłącznie do uruchamiania i testowania backendu,
  * nie może wpływać na logikę domenową,
  * nie jest wymagany do zrozumienia kodu.

* Kod musi być czytelny i testowalny również poza Dockerem.

---

## 10. Zasada końcowa

Jeśli pojawia się wątpliwość:

* **czy dana logika należy do domain?** → tak
* **czy frontend powinien to liczyć?** → nie
* **czy AI (w przyszłości) może to zmienić?** → nie

Ten plik jest nadrzędny wobec decyzji implementacyjnych.
