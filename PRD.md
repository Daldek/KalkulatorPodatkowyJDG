# Product Requirements Document (PRD)

## 1. Cel produktu

Celem aplikacji jest umożliwienie osobom prowadzącym jednoosobową działalność gospodarczą (JDG) w Polsce **porównania form opodatkowania** (skala podatkowa, podatek liniowy, ryczałt) na podstawie własnych danych finansowych, w sposób **przejrzysty, szybki i informacyjny**.

Aplikacja ma charakter **symulacyjny** i **nie stanowi doradztwa podatkowego**.

---

## 2. Grupa docelowa

* osoby prowadzące JDG
* osoby rozpoczynające działalność gospodarczą
* użytkownicy chcący zrozumieć skutki finansowe wyboru formy opodatkowania

Poziom wiedzy użytkownika: od podstawowego do średniozaawansowanego.

---

## 3. Problem użytkownika

Użytkownicy:

* nie wiedzą, która forma opodatkowania jest dla nich korzystniejsza,
* nie rozumieją wpływu ZUS i składki zdrowotnej na realny dochód,
* nie potrafią porównać skutków finansowych w dłuższym horyzoncie czasu,
* nie mają narzędzia pozwalającego na symulację miesięczną i wieloletnią.

---

## 4. Zakres funkcjonalny (In Scope)

### 4.1 Formy opodatkowania

* skala podatkowa
* podatek liniowy
* ryczałt od przychodów ewidencjonowanych (wiele stawek jednocześnie)

### 4.2 Dane wejściowe

* miesiąc bazowy (YYYY-MM)
* data rozpoczęcia działalności
* miesięczne przychody
* przychody ryczałtowe z różnymi stawkami
* stałe koszty miesięczne
* koszty jednorazowe (kwota + miesiąc)

### 4.3 ZUS

* automatyczne rozpoznawanie etapów ZUS:

  * ulga na start
  * preferencyjny ZUS
  * pełny ZUS

### 4.4 Horyzont czasowy

* 5 lat (60 miesięcy)
* brak miesięcy zerowych
* brak zmian przepisów w czasie

### 4.5 Wyniki

* miesięczne przychody, koszty i dochód
* porównanie form opodatkowania
* wskazanie najkorzystniejszej formy **wyłącznie na podstawie obliczeń matematycznych**

### 4.6 Wizualizacja

* jeden wykres porównawczy
* krok miesięczny

---

## 5. Poza zakresem (Out of Scope)

* doradztwo podatkowe
* kwalifikowanie kosztów
* konta użytkowników
* płatności
* AI / agenci językowi
* integracje z instytucjami publicznymi

---

## 6. Wymagania niefunkcjonalne

* szybkie działanie
* brak ciężkich frameworków frontendowych
* czytelny, minimalistyczny interfejs
* brak zapisu danych wrażliwych

---

## 7. Kryteria sukcesu

* użytkownik otrzymuje wynik porównania po jednym uzupełnieniu formularza
* użytkownik rozumie różnice między formami opodatkowania
* aplikacja poprawnie odwzorowuje logikę roku podatkowego 2025

---

## 8. Ograniczenia i ryzyka

* brak zmian przepisów w horyzoncie 5 lat
* poprawność zależna od danych wejściowych użytkownika
* aplikacja nie zastępuje księgowego ani interpretacji indywidualnej
