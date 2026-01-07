# Architecture Document

## 1. Cel architektury

Celem architektury jest zapewnienie:

* czytelności kodu,
* łatwego utrzymania,
* rozdzielenia odpowiedzialności,
* możliwości dalszej rozbudowy (np. o AI) bez refaktoryzacji rdzenia.

---

## 2. Architektura wysokopoziomowa

System składa się z dwóch głównych części:

* Backend (API + logika obliczeniowa)
* Frontend (statyczny interfejs użytkownika)

Frontend komunikuje się z backendem wyłącznie przez HTTP (JSON).

---

## 3. Backend

### 3.1 Technologia

* Python 3.12
* FastAPI
* pytest

### 3.2 Styl architektury

* layered / clean architecture
* silne rozdzielenie domeny od warstwy API

### 3.3 Struktura katalogów

```
backend/
├── app/
│   ├── api/        # Endpointy HTTP
│   ├── core/       # Stałe, konfiguracja, rok podatkowy
│   ├── domain/     # Czysta logika podatkowa
│   ├── services/   # Składanie scenariuszy i symulacji
│   ├── schemas/    # Modele wejścia/wyjścia (Pydantic)
│   └── storage/    # Opcjonalna persystencja
├── tests/          # Testy jednostkowe domain
└── main.py         # Punkt startowy aplikacji
```

---

## 4. Warstwa Domain

### Odpowiedzialność

* obliczenia podatkowe
* ZUS
* składka zdrowotna
* brak zależności od FastAPI, baz danych, JSON

### Cechy

* funkcje deterministyczne
* brak efektów ubocznych
* wysoka testowalność

---

## 5. Warstwa Services

### Odpowiedzialność

* budowa scenariuszy 60-miesięcznych
* agregacja wyników
* porównania form opodatkowania

Services używają wyłącznie warstwy `domain`.

---

## 6. API

### Odpowiedzialność

* walidacja danych wejściowych
* mapowanie HTTP → services
* brak logiki podatkowej

### Format komunikacji

* JSON
* brak sesji
* brak uwierzytelniania

---

## 7. Frontend

### Technologia

* HTML5
* CSS3
* Vanilla JavaScript (ES6)
* Chart.js

### Założenia

* brak frameworków JS
* minimalna ilość logiki po stronie klienta
* frontend wyłącznie renderuje dane z API

---

## 8. Dane i precyzja

* waluta: PLN
* obliczenia: Decimal
* prezentacja: 2 miejsca po przecinku
* zaokrąglenia na końcu obliczeń

---

## 9. Testy

* pytest
* testy jednostkowe wyłącznie dla warstwy `domain`
* brak testów frontendowych

---

## 10. Możliwości rozbudowy

* dodanie warstwy AI bez naruszania `domain`
* dodanie kont użytkowników
* wersjonowanie lat podatkowych

---

## 11. Ograniczenia

* architektura nie obsługuje zmian prawa w czasie
* aplikacja ma charakter informacyjny

## 12. Uruchamianie i środowisko

Backend aplikacji może być uruchamiany:
- lokalnie (Python 3.12)
- w kontenerze Docker

Docker:
- służy do zapewnienia powtarzalnego środowiska,
- obejmuje wyłącznie backend,
- nie wpływa na architekturę domenową.

Frontend pozostaje statyczny i nie wymaga konteneryzacji.
