# Kalkulator Podatkowy JDG - Quickstart

Szybki przewodnik uruchomienia aplikacji w 5 minut.

## Wymagania

- Python 3.12+
- Przeglądarka internetowa

## Krok 1: Instalacja backendu

```bash
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Krok 2: Uruchomienie backendu

```bash
python main.py
```

Backend będzie dostępny pod adresem: **http://localhost:8000**

## Krok 3: Otwarcie frontendu

Otwórz w przeglądarce plik:

```
frontend/index.html
```

Lub uruchom prosty serwer HTTP:

```bash
cd ../frontend
python -m http.server 8080
```

Frontend: **http://localhost:8080**

## Krok 4: Użycie kalkulatora

1. Uzupełnij formularz:
   - Miesiąc bazowy (np. 2025-01)
   - Data rozpoczęcia działalności
   - Miesięczny przychód
   - Stałe koszty miesięczne
   - Stawka ryczałtu

2. Kliknij **"Oblicz porównanie"**

3. Zobacz wyniki:
   - Wykres porównawczy
   - Tabela podsumowania
   - Najkorzystniejsza forma opodatkowania

## Test API (opcjonalnie)

```bash
# Health check
curl http://localhost:8000/health

# Dokumentacja API
open http://localhost:8000/docs

# Przykładowy request
cd ../examples
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

## Testy jednostkowe

```bash
cd backend
source venv/bin/activate
pytest
```

## Docker (opcjonalnie)

```bash
cd backend
docker build -t kalkulator-podatkowy:latest .
docker run -p 8000:8000 kalkulator-podatkowy:latest
```

## Troubleshooting

### Backend nie startuje

- Sprawdź czy Python 3.12 jest zainstalowany: `python3.12 --version`
- Sprawdź czy venv jest aktywowany
- Sprawdź logi błędów

### Frontend nie łączy się z API

- Upewnij się, że backend działa na http://localhost:8000
- Sprawdź konsolę przeglądarki (F12) dla błędów CORS
- Sprawdź czy URL w `frontend/js/app.js` jest poprawny

### Błędy obliczeń

- Sprawdź czy wszystkie pola formularza są wypełnione
- Sprawdź czy przychody i koszty są liczbami dodatnimi
- Zobacz szczegóły błędu w konsoli przeglądarki

## Dalsze kroki

- Przeczytaj pełną dokumentację w **README.md**
- Zobacz **ARCHITECTURE.md** dla szczegółów technicznych
- Sprawdź **examples/README.md** dla przykładów API
- Zapoznaj się z **RULES.md** dla zasad projektu

---

**Pomoc:** W razie problemów, zgłoś issue na GitHubie lub sprawdź dokumentację.
