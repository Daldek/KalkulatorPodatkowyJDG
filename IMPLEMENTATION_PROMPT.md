# Prompt startowy dla Claude

## Rola

Jesteś doświadczonym inżynierem oprogramowania. Twoim zadaniem jest **wygenerowanie kompletnego, działającego kodu aplikacji webowej (backend + prosty frontend)** zgodnie z poniższą specyfikacją. **Nie zgaduj założeń** – trzymaj się wyłącznie tego dokumentu.

Aplikacja ma charakter **informacyjny i symulacyjny**. Nie świadczy doradztwa podatkowego.

---

## Zakres projektu (v1.0)

### CO JEST W ZAKRESIE

* Kalkulator form opodatkowania JDG (Polska)
* Formy:

  * skala podatkowa
  * podatek liniowy
  * ryczałt (wiele stawek jednocześnie)
* Rok podatkowy: **2025**
* Horyzont obliczeń: **5 lat (60 miesięcy)**
* Automatyczne rozpoznawanie etapów ZUS
* Miesięczne serie danych + wykres porównawczy

### CZEGO NIE MA

* AI / agentów LLM
* kwalifikowania kosztów
* kont użytkowników
* płatności
* zapisu danych wrażliwych
* integracji z US / ZUS

---

## Backend – wymagania

### Technologia

* Python **3.14**
* FastAPI
* Architektura warstwowa (clean / layered)
* Brak frameworków frontendowych po stronie backendu

### Struktura projektu (wymagana)

```
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── domain/
│   ├── services/
│   ├── schemas/
│   └── storage/
├── tests/
└── main.py
```

### Zasady architektoniczne

* Logika podatkowa **tylko w `domain/`**
* `services/` składają wyniki i liczą scenariusze
* `api/` nie zawiera logiki biznesowej
* Brak AI w jakiejkolwiek formie

---

## Logika czasowa

### Jednostka czasu

* Podstawowa jednostka: **miesiąc**
* Użytkownik podaje **miesiąc bazowy (YYYY-MM)**
* Obliczenia zaczynają się od miesiąca bazowego
* **Nie generuj miesięcy zerowych**

### Horyzont

* Zawsze **60 kolejnych miesięcy**
* Brak zmian przepisów w czasie

---

## Przychody

* Użytkownik wprowadza **miesięczne przychody**
* Tryb projekcji: **manualny (C)**

  * możliwość edycji przychodu dla każdego miesiąca

### Ryczałt

* Działalność może mieć **wiele stawek ryczałtu jednocześnie**
* Użytkownik wprowadza:

  * listę przychodów miesięcznych
  * każda pozycja ma przypisaną stawkę ryczałtu
* Backend sumuje przychody zgodnie z zasadami ryczałtu

---

## Koszty

* Użytkownik wprowadza:

  * **stałe koszty miesięczne**
  * **opcjonalne koszty jednorazowe** (kwota + miesiąc)
* Brak kwalifikowania kosztów
* Koszty:

  * uwzględniane w skali i liniowym
  * ignorowane w ryczałcie

---

## ZUS

* Użytkownik podaje **datę rozpoczęcia działalności**
* Backend automatycznie rozpoznaje etap ZUS **dla każdego miesiąca** zgodnie z przepisami:

  * ulga na start
  * preferencyjny ZUS
  * pełny ZUS
* Brak ręcznego wyboru ZUS

---

## Składka zdrowotna

* Liczona **rocznie** zgodnie z formą opodatkowania
* Na potrzeby wykresów:

  * rozbijana **proporcjonalnie na miesiące**

---

## Wyniki

Backend zwraca:

* miesięczne serie (60 punktów) dla:

  * przychodu
  * kosztów
  * dochodu
* osobne serie dla:

  * skali
  * liniowego
  * ryczałtu

Decyzja „najkorzystniejsza forma”:

* **wyłącznie na podstawie wyniku matematycznego**

---

## Frontend

### Technologia

* HTML5
* CSS3 (bez frameworków)
* Vanilla JS (ES6)
* Fetch API
* Chart.js (jedyne JS dependency)

### Wymagania

* minimalistyczny, szybki
* więcej HTML/CSS niż JS
* brak React/Vue/Svelte
* frontend **nie liczy**, tylko renderuje dane z API

### Wykresy

* **jeden wykres porównawczy**
* dane miesięczne
* generowany po uzupełnieniu wszystkich danych

---

## Dane i precyzja

* Waluta: PLN
* Obliczenia:

  * `Decimal`
* Prezentacja:

  * 2 miejsca po przecinku
* Zaokrąglenia:

  * matematyczne
  * na końcu obliczeń

---

## Testy

* pytest
* testy jednostkowe **tylko dla `domain/`**
* brak testów frontendowych
* brak testów AI

---

## Co masz wygenerować

* Pełny kod backendu
* Pełny frontend statyczny
* README.md:

  * opis architektury
  * instrukcja uruchomienia
* Przykładowe requesty i response JSON

### Zasady generowania kodu

* Brak TODO
* Brak pseudokodu
* Każdy plik w całości
* Czytelne nazewnictwo (snake_case)
* Docstringi w stylu **NumPy**

---

## Kolejność pracy

1. Struktura katalogów
2. `domain/` – pełna logika podatkowa 2025
3. `services/`
4. API (FastAPI)
5. Frontend
6. README

Zastosuj się ściśle do tej specyfikacji.
