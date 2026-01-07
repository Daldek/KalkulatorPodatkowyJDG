# Claude.md — Pamięć projektowa i zasady współpracy

## Cel tego pliku

Ten plik definiuje **jak Claude ma interpretować i stosować pozostałe pliki Markdown**
znajdujące się w tym repozytorium.

Claude musi traktować ten plik jako **wiążącą instrukcję nadrzędną**.

---

## Hierarchia źródeł prawdy

Claude MUSI stosować następującą hierarchię dokumentów
podczas generowania lub modyfikowania kodu:

1. **IMPLEMENTATION_PROMPT.md**  
   → nadrzędna i wiążąca specyfikacja implementacyjna  
   → główne źródło prawdy przy generowaniu kodu

2. **RULES.md**  
   → niezmienne zasady projektu  
   → jeśli coś narusza RULES.md, jest błędem, nawet jeśli zostało zasugerowane gdzie indziej

3. **ARCHITECTURE.md**  
   → intencja architektoniczna i struktura systemu  
   → opisuje *jak* system ma być zorganizowany

4. **PRD.md**  
   → intencja produktowa i zakres funkcjonalny  
   → opisuje *co* budujemy i *czego nie budujemy*

W przypadku konfliktu lub niejednoznaczności:
- IMPLEMENTATION_PROMPT.md ma zawsze pierwszeństwo
- RULES.md ma pierwszeństwo przed ARCHITECTURE.md i PRD.md

---

## Obowiązkowe zachowanie Claude

Claude MUSI:

- ściśle stosować się do IMPLEMENTATION_PROMPT.md przy generowaniu kodu
- zapewnić, że cały kod jest zgodny z RULES.md
- respektować granice architektoniczne opisane w ARCHITECTURE.md
- nie dodawać funkcji ani logiki poza zakresem PRD.md
- nie wprowadzać założeń, które nie są jawnie opisane w dokumentach

Claude NIE MOŻE:

- dodawać AI, LLM, heurystyk ani „inteligentnej” logiki, jeśli nie zostało to wyraźnie zlecone
- przenosić logiki biznesowej poza warstwę domain
- dodawać frameworków lub zależności, które nie są wymienione
- interpretować prawa podatkowego poza zdefiniowanymi stałymi
- optymalizować kosztem czytelności lub testowalności

---

## Zasady generowania kodu

- Generuj **pełne pliki**, nigdy fragmenty
- Brak TODO, placeholderów i pseudokodu
- Implementacje mają być jawne i czytelne
- Stosuj dobre praktyki Pythona
- Wszystkie obliczenia finansowe wykonuj z użyciem `Decimal`
- Stosuj docstringi w stylu **NumPy**
- Przestrzegaj rozdzielenia odpowiedzialności (separation of concerns)

---

## Docker i środowisko

- Docker jest **narzędziem technicznym**, a nie elementem projektowym
- Docker **nie może wpływać na logikę domenową**
- Backend musi działać:
  - lokalnie (Python 3.14),
  - w kontenerze Docker
- Frontend pozostaje statyczny i **nie jest konteneryzowany**

---

## W razie wątpliwości

Jeśli pojawia się niepewność:

1. Wybierz jawność zamiast sprytu
2. Wybierz poprawność zamiast wygody
3. Wybierz czystość domeny zamiast skrótów
4. Wybierz dokumentację projektu zamiast domysłów

Jeżeli decyzji **nie da się jednoznacznie wyprowadzić z dokumentów**:
- zadaj pytanie
- **nie zgaduj**

---

## Koniec instrukcji

Ten plik jest celowo krótki.
Jego rolą jest wymuszanie spójności, dyscypliny i przewidywalności
w całym projekcie.
