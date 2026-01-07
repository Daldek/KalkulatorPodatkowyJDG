# Przykłady użycia API

Ten katalog zawiera przykłady requestów i responses dla API Kalkulatora Podatkowego JDG.

## Pliki

- **example_request.json** - Przykładowy pełny request do POST /api/calculate
- **example_response_summary.json** - Uproszczony przykład response (pełny jest bardzo duży)
- **test_api.sh** - Skrypt bash do testowania API

## Użycie

### 1. Uruchom backend

Upewnij się, że backend działa na http://localhost:8000:

```bash
cd ../backend
python main.py
```

### 2. Test API za pomocą skryptu

```bash
chmod +x test_api.sh
./test_api.sh
```

### 3. Test ręczny z curl

#### Health check

```bash
curl http://localhost:8000/health
```

#### Dostępne stawki ryczałtu

```bash
curl http://localhost:8000/api/tax-rates
```

#### Obliczenia podatkowe

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d @example_request.json
```

### 4. Test z przeglądarki

Otwórz Swagger UI:

```
http://localhost:8000/docs
```

## Interpretacja wyników

Response zawiera dane dla trzech form opodatkowania:

- **tax_scale** - Skala podatkowa (12%/32%)
- **linear_tax** - Podatek liniowy (19%)
- **lump_sum** - Ryczałt (stawka z requestu)

Dla każdej formy dostaniesz:

- **monthly_*** - Serie danych miesięcznych (60 punktów)
- **total_*** - Sumy za cały okres 60 miesięcy
- **best_form** - Nazwa najkorzystniejszej formy (najwyższy total_net_income)

## Dostosowanie przykładu

Możesz edytować `example_request.json` aby zmienić:

- **base_month** - Miesiąc rozpoczęcia symulacji
- **business_start_date** - Data rozpoczęcia działalności (wpływa na ZUS)
- **monthly_revenues** - Przychody dla każdego z 60 miesięcy
- **monthly_costs_fixed** - Stałe koszty miesięczne
- **one_time_costs** - Koszty jednorazowe (opcjonalne)
- **lump_sum_revenues** - Przychody ryczałtowe z różnymi stawkami

## Uwagi

- Wszystkie kwoty w PLN
- Daty w formacie ISO (YYYY-MM-DD lub YYYY-MM)
- Response zawiera Decimal jako string (np. "123.45")
- Aplikacja ma charakter informacyjny - nie stanowi doradztwa podatkowego
