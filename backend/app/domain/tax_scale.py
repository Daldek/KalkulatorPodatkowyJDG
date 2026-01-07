"""
Skala podatkowa - dwustopniowa skala podatku dochodowego.

Moduł implementuje obliczenia podatku według skali podatkowej w Polsce (2025).
"""

from decimal import Decimal

from app.core.constants_2025 import (
    TAX_SCALE_THRESHOLD,
    TAX_SCALE_RATE_LOW,
    TAX_SCALE_RATE_HIGH,
    TAX_REDUCTION_AMOUNT,
)


def calculate_income_tax_scale(annual_income: Decimal) -> Decimal:
    """
    Oblicza roczny podatek dochodowy według skali podatkowej.

    Parameters
    ----------
    annual_income : Decimal
        Roczny dochód (przychód minus koszty uzyskania przychodu) w PLN.

    Returns
    -------
    Decimal
        Roczny podatek dochodowy w PLN.

    Notes
    -----
    Skala podatkowa 2025:
    - Do 120 000 PLN: 12% minus kwota zmniejszająca podatek (3 600 PLN)
    - Powyżej 120 000 PLN: 10 800 PLN + 32% nadwyżki ponad 120 000 PLN

    Kwota zmniejszająca podatek wynika z kwoty wolnej od podatku (30 000 PLN).
    """
    if annual_income <= 0:
        return Decimal("0")

    # Podatek progresywny
    if annual_income <= TAX_SCALE_THRESHOLD:
        # Pierwsza stawka: 12%
        tax_before_reduction = annual_income * TAX_SCALE_RATE_LOW
    else:
        # Pierwsza stawka do progu + druga stawka od nadwyżki
        tax_first_bracket = TAX_SCALE_THRESHOLD * TAX_SCALE_RATE_LOW
        tax_second_bracket = (
            annual_income - TAX_SCALE_THRESHOLD
        ) * TAX_SCALE_RATE_HIGH
        tax_before_reduction = tax_first_bracket + tax_second_bracket

    # Odejmujemy kwotę zmniejszającą podatek
    tax_after_reduction = tax_before_reduction - TAX_REDUCTION_AMOUNT

    # Podatek nie może być ujemny
    tax = max(Decimal("0"), tax_after_reduction)

    return tax.quantize(Decimal("0.01"))


def calculate_monthly_tax_advance_scale(
    monthly_income: Decimal,
    months_count: int = 1,
) -> Decimal:
    """
    Oblicza miesięczną zaliczkę na podatek dochodowy według skali.

    Parameters
    ----------
    monthly_income : Decimal
        Miesięczny dochód (przychód minus koszty) w PLN.
    months_count : int, optional
        Liczba miesięcy od początku roku (dla zasady narastającej), domyślnie 1.

    Returns
    -------
    Decimal
        Miesięczna zaliczka na podatek w PLN.

    Notes
    -----
    W praktyce zaliczki są płacone miesięcznie, ale w uproszczeniu
    można przyjąć dochód roczny / 12.

    Dla symulacji przyjmujemy miesięczne obliczenie podatku.
    """
    if monthly_income <= 0:
        return Decimal("0")

    # Uproszczone miesięczne obliczenie
    # Zakładamy że kwota zmniejszająca jest rozłożona równomiernie na miesiące
    monthly_reduction = TAX_REDUCTION_AMOUNT / 12

    if monthly_income <= (TAX_SCALE_THRESHOLD / 12):
        tax_before_reduction = monthly_income * TAX_SCALE_RATE_LOW
    else:
        # Progresja w skali miesięcznej (uproszczenie)
        threshold_monthly = TAX_SCALE_THRESHOLD / 12
        tax_first = threshold_monthly * TAX_SCALE_RATE_LOW
        tax_second = (monthly_income - threshold_monthly) * TAX_SCALE_RATE_HIGH
        tax_before_reduction = tax_first + tax_second

    tax = max(Decimal("0"), tax_before_reduction - monthly_reduction)

    return tax.quantize(Decimal("0.01"))


def calculate_net_income_scale(
    annual_revenue: Decimal,
    annual_costs: Decimal,
) -> Decimal:
    """
    Oblicza roczny dochód netto po podatku (bez ZUS i składki zdrowotnej).

    Parameters
    ----------
    annual_revenue : Decimal
        Roczny przychód w PLN.
    annual_costs : Decimal
        Roczne koszty uzyskania przychodu w PLN.

    Returns
    -------
    Decimal
        Roczny dochód netto (przychód - koszty - podatek) w PLN.

    Notes
    -----
    Funkcja nie uwzględnia ZUS ani składki zdrowotnej -
    to jest zadanie warstwy services.
    """
    annual_income = annual_revenue - annual_costs

    if annual_income <= 0:
        return Decimal("0")

    tax = calculate_income_tax_scale(annual_income)
    net_income = annual_income - tax

    return net_income.quantize(Decimal("0.01"))
