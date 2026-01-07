"""
Podatek liniowy - 19% podatek dochodowy od osób fizycznych.

Moduł implementuje obliczenia podatku liniowego w Polsce (2025).
"""

from decimal import Decimal

from app.core.constants_2025 import LINEAR_TAX_RATE


def calculate_income_tax_linear(annual_income: Decimal) -> Decimal:
    """
    Oblicza roczny podatek dochodowy według stawki liniowej.

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
    Podatek liniowy 2025:
    - Stała stawka: 19%
    - Brak kwoty wolnej od podatku
    - Brak kwoty zmniejszającej podatek
    """
    if annual_income <= 0:
        return Decimal("0")

    tax = annual_income * LINEAR_TAX_RATE

    return tax.quantize(Decimal("0.01"))


def calculate_monthly_tax_advance_linear(monthly_income: Decimal) -> Decimal:
    """
    Oblicza miesięczną zaliczkę na podatek dochodowy według stawki liniowej.

    Parameters
    ----------
    monthly_income : Decimal
        Miesięczny dochód (przychód minus koszty) w PLN.

    Returns
    -------
    Decimal
        Miesięczna zaliczka na podatek w PLN.

    Notes
    -----
    Dla podatku liniowego miesięczna zaliczka to po prostu 19% dochodu miesięcznego.
    """
    if monthly_income <= 0:
        return Decimal("0")

    tax = monthly_income * LINEAR_TAX_RATE

    return tax.quantize(Decimal("0.01"))


def calculate_net_income_linear(
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

    tax = calculate_income_tax_linear(annual_income)
    net_income = annual_income - tax

    return net_income.quantize(Decimal("0.01"))
