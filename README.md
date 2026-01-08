# Kalkulator Podatkowy JDG

> Aplikacja do porównania form opodatkowania dla jednoosobowej działalności gospodarczej w Polsce (rok podatkowy 2025)

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ⚠️ Zastrzeżenie

**UWAGA:** Aplikacja ma charakter **informacyjny i symulacyjny**. Nie stanowi doradztwa podatkowego i nie zastępuje księgowego ani interpretacji indywidualnej. Wyniki oparte wyłącznie na obliczeniach matematycznych zgodnie z przepisami na rok 2025.

---

## 📋 Spis treści

- [O projekcie](#o-projekcie)
- [Funkcjonalności](#funkcjonalności)
- [Architektura](#architektura)
- [Wymagania](#wymagania)
- [Instalacja](#instalacja)
- [Uruchomienie](#uruchomienie)
- [Struktura projektu](#struktura-projektu)
- [Testy](#testy)
- [Użycie API](#użycie-api)
- [Zasady projektowe](#zasady-projektowe)

---

## 🎯 O projekcie

Kalkulator Podatkowy JDG to aplikacja webowa umożliwiająca przedsiębiorcom prowadzącym jednoosobową działalność gospodarczą w Polsce **porównanie trzech form opodatkowania**:

- **Skala podatkowa** (12% / 32%)
- **Podatek liniowy** (19%)
- **Ryczałt od przychodów ewidencjonowanych** (różne stawki)

Aplikacja wykonuje symulację finansową na **60 miesięcy** (5 lat), uwzględniając:
- Automatyczne etapy ZUS (ulga na start, preferencyjny, pełny)
- Składkę zdrowotną (różną dla każdej formy)
- Koszty uzyskania przychodu (dla skali i liniowego)
- Przychody z wieloma stawkami ryczałtu jednocześnie

---

## ✨ Funkcjonalności

### W zakresie (v1.2)

✅ Trzy formy opodatkowania: skala, liniowy, ryczałt
✅ Automatyczne rozpoznawanie etapów ZUS
✅ Horyzont 60 miesięcy (5 lat)
✅ Miesięczne serie danych
✅ **Modelowanie wzrostu przychodów**:
  - Parametr rocznego wzrostu % (compound miesięczny)
  - Edytowalna tabela 5×12 dla wszystkich 60 miesięcy
  - Ręczna edycja przychodów dla dowolnego miesiąca
✅ Trzy wykresy wizualizacyjne (Chart.js):
  - Struktura kosztów pierwszego miesiąca (grouped bar chart)
  - Miesięczny dochód netto (line chart)
  - Skumulowany dochód netto (line chart)
✅ Szczegółowe tabele miesięczne (60 miesięcy dla każdej formy)
✅ Cztery okresy podsumowań (6, 12, 30, 60 miesięcy)
✅ Wskazanie najkorzystniejszej formy (wynik matematyczny)
✅ Przychody ryczałtowe z wieloma stawkami
✅ Koszty stałe i jednorazowe

### Poza zakresem

❌ AI / agenci LLM
❌ Kwalifikowanie kosztów
❌ Konta użytkowników
❌ Płatności
❌ Zapis danych wrażliwych
❌ Integracje z US / ZUS

---

## 🏗️ Architektura

Aplikacja zbudowana zgodnie z **clean/layered architecture**:

```
┌─────────────────────────────────────────┐
│          Frontend (Vanilla JS)          │
│    HTML5 + CSS3 + Chart.js              │
└──────────────┬──────────────────────────┘
               │ HTTP (JSON)
┌──────────────▼──────────────────────────┐
│           API Layer (FastAPI)           │
│    Walidacja requestów / responses      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│        Services Layer                   │
│    Składanie scenariuszy 60-m-cy        │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│         Domain Layer                    │
│  Czysta logika podatkowa (2025)         │
│  - Skala, liniowy, ryczałt              │
│  - ZUS, składka zdrowotna               │
└─────────────────────────────────────────┘
```

### Zasady architektury

1. **Domain nie zależy od niczego** - można uruchomić i przetestować w izolacji
2. **Services składają wyniki** - budują scenariusze z modułów domain
3. **API tylko mapuje** - brak logiki biznesowej
4. **Frontend tylko renderuje** - nie wykonuje obliczeń

---

## 📦 Wymagania

### Backend

- **Python 3.12** (lub nowszy)
- FastAPI 0.115+
- Pydantic 2.10+
- python-dateutil 2.9+
- pytest 8.3+ (do testów)

### Frontend

- Przeglądarka z obsługą ES6
- Chart.js 4.4+ (ładowane z CDN)

### Opcjonalnie

- Docker 20.10+ (dla konteneryzacji)

---

## 🚀 Instalacja

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/twoj-user/kalkulator-podatkowy-jdg.git
cd kalkulator-podatkowy-jdg
```

### 2. Backend - instalacja zależności

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend - bez instalacji

Frontend jest statyczny i nie wymaga instalacji. Wystarczy otworzyć `frontend/index.html` w przeglądarce (po uruchomieniu backendu).

---

## ▶️ Uruchomienie

### Lokalnie (bez Dockera)

#### Backend

```bash
cd backend
source venv/bin/activate  # Aktywuj venv
python main.py
```

Backend będzie dostępny pod adresem: **http://localhost:8000**

- Dokumentacja API (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

#### Frontend

1. Otwórz plik `frontend/index.html` w przeglądarce
2. Lub użyj prostego serwera HTTP:

```bash
cd frontend
python -m http.server 8080
```

Frontend będzie dostępny pod adresem: **http://localhost:8080**

### Z Dockerem

```bash
cd backend
docker build -t kalkulator-podatkowy:latest .
docker run -p 8000:8000 kalkulator-podatkowy:latest
```

---

## 📂 Struktura projektu

```
kalkulator_podatkowy/
│
├── backend/
│   ├── app/
│   │   ├── api/              # Endpointy FastAPI
│   │   │   └── calculator.py
│   │   ├── core/             # Stałe i konfiguracja
│   │   │   └── constants_2025.py
│   │   ├── domain/           # Czysta logika podatkowa
│   │   │   ├── zus.py
│   │   │   ├── tax_scale.py
│   │   │   ├── linear_tax.py
│   │   │   ├── lump_sum.py
│   │   │   └── health_insurance.py
│   │   ├── services/         # Składanie scenariuszy
│   │   │   ├── time_utils.py
│   │   │   └── tax_calculator.py
│   │   ├── schemas/          # Modele Pydantic
│   │   │   ├── requests.py
│   │   │   └── responses.py
│   │   └── storage/          # Persystencja (nieużywane w v1.0)
│   ├── tests/                # Testy jednostkowe
│   │   ├── test_zus.py
│   │   ├── test_tax_scale.py
│   │   ├── test_linear_tax.py
│   │   ├── test_lump_sum.py
│   │   └── test_health_insurance.py
│   ├── main.py               # Punkt startowy
│   ├── requirements.txt
│   └── pyproject.toml
│
├── frontend/
│   ├── css/
│   │   └── style.css         # Stylowanie
│   ├── js/
│   │   └── app.js            # Logika frontendu
│   └── index.html            # Główna strona
│
├── ARCHITECTURE.md
├── PRD.md
├── RULES.md
├── IMPLEMENTATION_PROMPT.md
├── CLAUDE.md
└── README.md
```

---

## 🧪 Testy

Projekt zawiera testy jednostkowe dla warstwy **domain/**.

### Uruchomienie testów

```bash
cd backend
source venv/bin/activate
pytest
```

### Testy z pokryciem kodu

```bash
pytest --cov=app --cov-report=html
```

Raport HTML zostanie wygenerowany w `htmlcov/index.html`.

### Co jest testowane?

- ✅ Obliczenia ZUS (etapy, kwoty)
- ✅ Skala podatkowa (progresja, kwota wolna)
- ✅ Podatek liniowy (19%)
- ✅ Ryczałt (wiele stawek)
- ✅ Składka zdrowotna (różne formy)

---

## 🔌 Użycie API

### Endpoint: POST /api/calculate

Główny endpoint do obliczania porównania form opodatkowania.

#### Request

```json
{
  "base_month": "2025-01",
  "business_start_date": "2025-01-01",
  "monthly_revenues": [50000, 50000, ...],  // 60 wartości
  "monthly_costs_fixed": 5000,
  "one_time_costs": [
    {
      "month_index": 0,
      "amount": 10000
    }
  ],
  "lump_sum_revenues": [
    {
      "month_index": 0,
      "revenues_by_rate": {
        "0.055": 50000
      }
    },
    ...  // 60 elementów
  ]
}
```

#### Response

```json
{
  "tax_scale": {
    "form_name": "tax_scale",
    "months": ["2025-01", "2025-02", ...],
    "monthly_revenue": [50000, 50000, ...],
    "monthly_net_income": [35850, 35850, ...],
    "total_net_income": 2151000,
    ...
  },
  "linear_tax": { ... },
  "lump_sum": { ... },
  "best_form": "lump_sum",
  "best_form_description": "Na podstawie obliczeń matematycznych..."
}
```

### Endpoint: GET /api/tax-rates

Zwraca dostępne stawki ryczałtu.

```bash
curl http://localhost:8000/api/tax-rates
```

---

## 📐 Zasady projektowe

### Niezmienne zasady (RULES.md)

1. **Brak doradztwa podatkowego** - aplikacja nie wydaje zaleceń
2. **Matematyka ponad interpretacją** - tylko jawne obliczenia
3. **Rozdzielenie odpowiedzialności** - domain/services/api
4. **Domain w izolacji** - brak zależności od FastAPI/JSON
5. **Stałość przepisów** - rok 2025, brak zmian w czasie
6. **Automatyczne etapy ZUS** - brak ręcznego wyboru
7. **Precyzja obliczeń** - Decimal, 2 miejsca po przecinku

### Hierarchia dokumentów (CLAUDE.md)

1. **IMPLEMENTATION_PROMPT.md** - główne źródło prawdy
2. **RULES.md** - niezmienne zasady
3. **ARCHITECTURE.md** - struktura systemu
4. **PRD.md** - zakres produktowy

---

## 🤝 Wkład

Projekt ma charakter edukacyjny i demonstracyjny. Pull requesty mile widziane, szczególnie:

- Aktualizacje stałych podatkowych na kolejne lata
- Poprawki błędów w obliczeniach
- Testy dla warstwy services i API
- Ulepszenia UI/UX frontendu

---

## 📄 Licencja

MIT License - szczegóły w pliku LICENSE.

---

## 📞 Kontakt

W razie pytań lub problemów, zgłoś issue na GitHubie.

---

**Wersja:** 1.2.0
**Rok podatkowy:** 2025
**Ostatnia aktualizacja:** 2026-01-08
