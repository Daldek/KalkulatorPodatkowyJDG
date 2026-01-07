"""
Składka zdrowotna dla różnych form opodatkowania JDG.

Moduł implementuje zasady obliczania składki zdrowotnej w Polsce (2025).
"""

from decimal import Decimal

from app.core.constants_2025 import (
    HEALTH_INSURANCE_RATE_SCALE,
    HEALTH_INSURANCE_RATE_LINEAR,
    HEALTH_INSURANCE_MIN_MONTHLY_SCALE,
    HEALTH_INSURANCE_MIN_MONTHLY_LINEAR,
    HEALTH_INSURANCE_MONTHLY_LUMP_SUM,
)


def calculate_health_insurance_monthly_scale(
    monthly_income: Decimal,
) -> Decimal:
    """
    Oblicza miesięczną składkę zdrowotną dla skali podatkowej.

    Parameters
    ----------
    monthly_income : Decimal
        Miesięczny dochód (przychód minus koszty) w PLN.

    Returns
    -------
    Decimal
        Miesięczna składka zdrowotna w PLN.

    Notes
    -----
    Skala podatkowa (2025):
    - 9% dochodu
    - Nie mniej niż 9% z 75% minimalnego wynagrodzenia (~314.96 PLN)
    """
    if monthly_income <= 0:
        return HEALTH_INSURANCE_MIN_MONTHLY_SCALE

    calculated = monthly_income * HEALTH_INSURANCE_RATE_SCALE

    # Nie może być niższa niż minimum
    health_insurance = max(calculated, HEALTH_INSURANCE_MIN_MONTHLY_SCALE)

    return health_insurance.quantize(Decimal("0.01"))


def calculate_health_insurance_monthly_linear(
    monthly_income: Decimal,
) -> Decimal:
    """
    Oblicza miesięczną składkę zdrowotną dla podatku liniowego.

    Parameters
    ----------
    monthly_income : Decimal
        Miesięczny dochód (przychód minus koszty) w PLN.

    Returns
    -------
    Decimal
        Miesięczna składka zdrowotna w PLN.

    Notes
    -----
    Podatek liniowy (2025):
    - 4.9% dochodu
    - Nie mniej niż 9% z 75% minimalnego wynagrodzenia (~314.96 PLN)
    """
    if monthly_income <= 0:
        return HEALTH_INSURANCE_MIN_MONTHLY_LINEAR

    calculated = monthly_income * HEALTH_INSURANCE_RATE_LINEAR

    # Nie może być niższa niż minimum
    health_insurance = max(calculated, HEALTH_INSURANCE_MIN_MONTHLY_LINEAR)

    return health_insurance.quantize(Decimal("0.01"))


# Deprecated - pozostawiona dla kompatybilności
def calculate_health_insurance_monthly_scale_linear(
    monthly_income: Decimal,
) -> Decimal:
    """
    Deprecated: Użyj calculate_health_insurance_monthly_scale() lub
    calculate_health_insurance_monthly_linear() zamiast tego.

    Domyślnie zwraca wartość dla skali podatkowej.
    """
    return calculate_health_insurance_monthly_scale(monthly_income)


def calculate_health_insurance_monthly_lump_sum() -> Decimal:
    """
    Oblicza miesięczną składkę zdrowotną dla ryczałtu.

    Returns
    -------
    Decimal
        Miesięczna składka zdrowotna w PLN.

    Notes
    -----
    Dla ryczałtu składka zdrowotna jest stała miesięcznie:
    - 9% od 75% przeciętnego wynagrodzenia
    - Niezależna od wysokości przychodów
    """
    return HEALTH_INSURANCE_MONTHLY_LUMP_SUM.quantize(Decimal("0.01"))


def calculate_health_insurance_annual_lump_sum(months: int = 12) -> Decimal:
    """
    Oblicza roczną składkę zdrowotną dla ryczałtu.

    Parameters
    ----------
    months : int, optional
        Liczba miesięcy działalności w roku (domyślnie 12).

    Returns
    -------
    Decimal
        Roczna składka zdrowotna w PLN.

    Notes
    -----
    Dla ryczałtu składka jest stała co miesiąc,
    więc roczna = miesięczna × liczba miesięcy.
    """
    monthly = calculate_health_insurance_monthly_lump_sum()
    annual = monthly * months
    return annual.quantize(Decimal("0.01"))


def distribute_annual_to_monthly(annual_amount: Decimal, months: int) -> Decimal:
    """
    Rozbija roczną kwotę proporcjonalnie na miesiące.

    Parameters
    ----------
    annual_amount : Decimal
        Roczna kwota do rozłożenia.
    months : int
        Liczba miesięcy.

    Returns
    -------
    Decimal
        Miesięczna kwota (średnia).

    Notes
    -----
    Funkcja pomocnicza do wizualizacji rocznych składek na wykresach miesięcznych.
    """
    if months <= 0:
        return Decimal("0")

    monthly = annual_amount / months
    return monthly.quantize(Decimal("0.01"))
