"""
Logika ZUS - automatyczne rozpoznawanie etapów składek społecznych.

Moduł implementuje zasady obliczania składek ZUS dla JDG w Polsce (2025).
"""

from datetime import date
from decimal import Decimal
from typing import Literal

from app.core.constants_2025 import (
    ZUS_RELIEF_MONTHS,
    ZUS_PREFERENTIAL_MONTHS,
    ZUS_RELIEF_MONTHLY,
    ZUS_PREFERENTIAL_MONTHLY,
    ZUS_FULL_MONTHLY,
)


ZusStage = Literal["relief", "preferential", "full"]


def calculate_months_since_start(start_date: date, current_date: date) -> int:
    """
    Oblicza liczbę pełnych miesięcy kalendarzowych od rozpoczęcia działalności.

    Parameters
    ----------
    start_date : date
        Data rozpoczęcia działalności gospodarczej.
    current_date : date
        Data miesiąca, dla którego liczymy miesiące.

    Returns
    -------
    int
        Liczba pełnych miesięcy kalendarzowych. Może być ujemna (-1) dla
        niepełnego miesiąca rozpoczęcia działalności.

    Notes
    -----
    Miesiąc jest "pełny", gdy działalność jest prowadzona przez cały miesiąc.
    - Jeśli działalność rozpoczęła się 1. dnia miesiąca, ten miesiąc jest pełny (miesiąc 0).
    - Jeśli działalność rozpoczęła się 2. lub później, ten miesiąc jest niepełny,
      a pierwszy pełny miesiąc to następny miesiąc (który będzie miesiącem 0).

    Przykład:
    - Start: 2025-01-01, Current: 2025-01-20 → miesiąc 0 (styczeń pełny)
    - Start: 2025-01-02, Current: 2025-01-20 → miesiąc -1 (styczeń niepełny)
    - Start: 2025-01-02, Current: 2025-02-01 → miesiąc 0 (luty to pierwszy pełny)
    - Start: 2025-01-15, Current: 2025-07-01 → miesiąc 5 (lut-lip to 6 pełnych miesięcy)
    """
    year_diff = current_date.year - start_date.year
    month_diff = current_date.month - start_date.month

    total_months = year_diff * 12 + month_diff

    # Jeśli działalność rozpoczęła się po 1. dniu miesiąca,
    # miesiąc rozpoczęcia nie jest pełny - odejmujemy 1
    if start_date.day > 1:
        total_months -= 1

    return total_months


def determine_zus_stage(start_date: date, current_date: date) -> ZusStage:
    """
    Określa etap ZUS dla danego miesiąca.

    Parameters
    ----------
    start_date : date
        Data rozpoczęcia działalności gospodarczej.
    current_date : date
        Data miesiąca, dla którego określamy etap ZUS.

    Returns
    -------
    ZusStage
        Etap ZUS: 'relief' (ulga na start), 'preferential' (preferencyjny),
        lub 'full' (pełny).

    Notes
    -----
    Zasady:
    - Ulga na start: pierwsze 6 pełnych miesięcy (miesiące -1 do 4 włącznie)
    - Preferencyjny ZUS: kolejne 24 pełne miesiące (miesiące 5-28)
    - Pełny ZUS: od 29. pełnego miesiąca włącznie

    Miesiąc -1 występuje tylko gdy działalność rozpoczęto po 1. dniu miesiąca
    (niepełny miesiąc początkowy).
    """
    months_since_start = calculate_months_since_start(start_date, current_date)

    if months_since_start < ZUS_RELIEF_MONTHS:
        return "relief"
    elif months_since_start < ZUS_RELIEF_MONTHS + ZUS_PREFERENTIAL_MONTHS:
        return "preferential"
    else:
        return "full"


def calculate_zus_monthly(start_date: date, current_date: date) -> Decimal:
    """
    Oblicza miesięczną składkę ZUS dla danego miesiąca.

    Parameters
    ----------
    start_date : date
        Data rozpoczęcia działalności gospodarczej.
    current_date : date
        Data miesiąca, dla którego obliczamy ZUS.

    Returns
    -------
    Decimal
        Miesięczna składka ZUS w PLN.

    Notes
    -----
    Funkcja automatycznie rozpoznaje etap ZUS i zwraca odpowiednią kwotę.
    """
    stage = determine_zus_stage(start_date, current_date)

    if stage == "relief":
        return ZUS_RELIEF_MONTHLY
    elif stage == "preferential":
        return ZUS_PREFERENTIAL_MONTHLY
    else:
        return ZUS_FULL_MONTHLY


def calculate_zus_for_period(
    start_date: date,
    period_months: list[date]
) -> list[tuple[date, ZusStage, Decimal]]:
    """
    Oblicza ZUS dla listy miesięcy.

    Parameters
    ----------
    start_date : date
        Data rozpoczęcia działalności gospodarczej.
    period_months : list[date]
        Lista dat miesięcy (każdy reprezentowany przez pierwszy dzień miesiąca).

    Returns
    -------
    list[tuple[date, ZusStage, Decimal]]
        Lista krotek: (data miesiąca, etap ZUS, kwota ZUS).

    Notes
    -----
    Funkcja pomocnicza do obliczania ZUS dla wielu miesięcy jednocześnie.
    """
    results = []

    for month_date in period_months:
        stage = determine_zus_stage(start_date, month_date)
        amount = calculate_zus_monthly(start_date, month_date)
        results.append((month_date, stage, amount))

    return results
