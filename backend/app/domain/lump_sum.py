"""
Ryczałt od przychodów ewidencjonowanych.

Moduł implementuje obliczenia ryczałtu w Polsce (2025).
Obsługuje wiele stawek ryczałtu jednocześnie.
"""

from decimal import Decimal
from typing import Dict


def calculate_tax_lump_sum(revenue_by_rate: Dict[Decimal, Decimal]) -> Decimal:
    """
    Oblicza podatek ryczałtowy dla przychodów z różnymi stawkami.

    Parameters
    ----------
    revenue_by_rate : Dict[Decimal, Decimal]
        Słownik: {stawka_ryczałtu: przychód_dla_tej_stawki}.
        Przykład: {Decimal("0.055"): Decimal("50000"), Decimal("0.085"): Decimal("30000")}

    Returns
    -------
    Decimal
        Łączny podatek ryczałtowy w PLN.

    Notes
    -----
    Ryczałt:
    - Podatek płacony bezpośrednio od przychodu
    - Różne stawki dla różnych rodzajów działalności
    - Koszty nie są odliczane
    - Każdy rodzaj przychodu może mieć inną stawkę

    Przykładowe stawki (2025):
    - 2% - sprzedaż towarów
    - 5.5% - usługi IT
    - 8.5% - gastronomia, handel
    - 12% - usługi budowlane
    - 15% - consulting
    """
    total_tax = Decimal("0")

    for rate, revenue in revenue_by_rate.items():
        if revenue > 0:
            tax_for_rate = revenue * rate
            total_tax += tax_for_rate

    return total_tax.quantize(Decimal("0.01"))


def calculate_monthly_tax_lump_sum(
    monthly_revenue_by_rate: Dict[Decimal, Decimal]
) -> Decimal:
    """
    Oblicza miesięczny podatek ryczałtowy.

    Parameters
    ----------
    monthly_revenue_by_rate : Dict[Decimal, Decimal]
        Słownik: {stawka_ryczałtu: miesięczny_przychód_dla_tej_stawki}.

    Returns
    -------
    Decimal
        Miesięczny podatek ryczałtowy w PLN.

    Notes
    -----
    Dla ryczałtu miesięczny podatek to suma (przychód × stawka) dla każdej stawki.
    """
    return calculate_tax_lump_sum(monthly_revenue_by_rate)


def calculate_annual_tax_lump_sum(
    annual_revenue_by_rate: Dict[Decimal, Decimal]
) -> Decimal:
    """
    Oblicza roczny podatek ryczałtowy.

    Parameters
    ----------
    annual_revenue_by_rate : Dict[Decimal, Decimal]
        Słownik: {stawka_ryczałtu: roczny_przychód_dla_tej_stawki}.

    Returns
    -------
    Decimal
        Roczny podatek ryczałtowy w PLN.

    Notes
    -----
    Dla ryczałtu roczny podatek to suma (przychód × stawka) dla każdej stawki.
    """
    return calculate_tax_lump_sum(annual_revenue_by_rate)


def calculate_net_income_lump_sum(
    revenue_by_rate: Dict[Decimal, Decimal],
) -> Decimal:
    """
    Oblicza dochód netto po podatku ryczałtowym (bez ZUS i składki zdrowotnej).

    Parameters
    ----------
    revenue_by_rate : Dict[Decimal, Decimal]
        Słownik: {stawka_ryczałtu: przychód_dla_tej_stawki}.

    Returns
    -------
    Decimal
        Dochód netto (przychód - podatek ryczałtowy) w PLN.

    Notes
    -----
    W ryczałcie:
    - Koszty nie są odliczane od przychodu
    - Dochód = przychód - podatek ryczałtowy
    - Funkcja nie uwzględnia ZUS ani składki zdrowotnej
    """
    total_revenue = sum(revenue_by_rate.values())
    tax = calculate_tax_lump_sum(revenue_by_rate)

    net_income = total_revenue - tax

    return net_income.quantize(Decimal("0.01"))


def aggregate_revenue_by_rate(
    monthly_revenues: list[Dict[Decimal, Decimal]],
) -> Dict[Decimal, Decimal]:
    """
    Agreguje przychody z wielu miesięcy według stawek.

    Parameters
    ----------
    monthly_revenues : list[Dict[Decimal, Decimal]]
        Lista słowników miesięcznych przychodów według stawek.

    Returns
    -------
    Dict[Decimal, Decimal]
        Zagregowane przychody: {stawka: suma_przychodów}.

    Notes
    -----
    Funkcja pomocnicza do sumowania przychodów rocznych z miesięcznych danych.
    """
    aggregated: Dict[Decimal, Decimal] = {}

    for monthly_rev in monthly_revenues:
        for rate, revenue in monthly_rev.items():
            if rate in aggregated:
                aggregated[rate] += revenue
            else:
                aggregated[rate] = revenue

    return aggregated


def validate_lump_sum_rates(revenue_by_rate: Dict[Decimal, Decimal]) -> bool:
    """
    Waliduje poprawność stawek ryczałtu.

    Parameters
    ----------
    revenue_by_rate : Dict[Decimal, Decimal]
        Słownik: {stawka_ryczałtu: przychód}.

    Returns
    -------
    bool
        True jeśli wszystkie stawki są poprawne, False w przeciwnym razie.

    Notes
    -----
    Stawki ryczałtu muszą być dodatnie i mniejsze niż 100%.
    """
    for rate in revenue_by_rate.keys():
        if rate <= 0 or rate >= 1:
            return False
    return True
