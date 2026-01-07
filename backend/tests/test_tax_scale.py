"""
Testy jednostkowe dla skali podatkowej.

Testuje obliczenia podatku według skali progresywnej.
"""

import pytest
from decimal import Decimal

from app.domain.tax_scale import (
    calculate_income_tax_scale,
    calculate_monthly_tax_advance_scale,
    calculate_net_income_scale,
)
from app.core.constants_2025 import (
    TAX_SCALE_THRESHOLD,
    TAX_SCALE_RATE_LOW,
    TAX_SCALE_RATE_HIGH,
    TAX_REDUCTION_AMOUNT,
)


class TestCalculateIncomeTaxScale:
    """Testy obliczania rocznego podatku według skali."""

    def test_zero_income(self):
        """Test: zerowy dochód = zerowy podatek."""
        tax = calculate_income_tax_scale(Decimal("0"))
        assert tax == Decimal("0")

    def test_negative_income(self):
        """Test: ujemny dochód = zerowy podatek."""
        tax = calculate_income_tax_scale(Decimal("-10000"))
        assert tax == Decimal("0")

    def test_income_below_threshold(self):
        """Test: dochód poniżej progu = pierwsza stawka."""
        income = Decimal("50000")
        tax = calculate_income_tax_scale(income)

        # Obliczenie ręczne: 50000 * 0.12 - 3600 = 6000 - 3600 = 2400
        expected = income * TAX_SCALE_RATE_LOW - TAX_REDUCTION_AMOUNT
        assert tax == expected.quantize(Decimal("0.01"))

    def test_income_at_threshold(self):
        """Test: dochód równy progowi."""
        income = TAX_SCALE_THRESHOLD  # 120000
        tax = calculate_income_tax_scale(income)

        # 120000 * 0.12 - 3600 = 14400 - 3600 = 10800
        expected = income * TAX_SCALE_RATE_LOW - TAX_REDUCTION_AMOUNT
        assert tax == expected.quantize(Decimal("0.01"))

    def test_income_above_threshold(self):
        """Test: dochód powyżej progu = druga stawka dla nadwyżki."""
        income = Decimal("200000")
        tax = calculate_income_tax_scale(income)

        # Pierwsza stawka do progu: 120000 * 0.12 = 14400
        # Druga stawka od nadwyżki: (200000 - 120000) * 0.32 = 80000 * 0.32 = 25600
        # Suma: 14400 + 25600 = 40000
        # Po redukcji: 40000 - 3600 = 36400
        tax_first = TAX_SCALE_THRESHOLD * TAX_SCALE_RATE_LOW
        tax_second = (income - TAX_SCALE_THRESHOLD) * TAX_SCALE_RATE_HIGH
        expected = tax_first + tax_second - TAX_REDUCTION_AMOUNT

        assert tax == expected.quantize(Decimal("0.01"))

    def test_small_income_with_reduction(self):
        """Test: mały dochód, kwota zmniejszająca może dać 0."""
        income = Decimal("10000")
        tax = calculate_income_tax_scale(income)

        # 10000 * 0.12 - 3600 = 1200 - 3600 = -2400 -> 0
        assert tax == Decimal("0")

    def test_tax_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        income = Decimal("100000")
        tax = calculate_income_tax_scale(income)
        assert isinstance(tax, Decimal)
        assert tax == tax.quantize(Decimal("0.01"))


class TestCalculateMonthlyTaxAdvanceScale:
    """Testy miesięcznej zaliczki na podatek."""

    def test_zero_income(self):
        """Test: zerowy miesięczny dochód = zero podatku."""
        tax = calculate_monthly_tax_advance_scale(Decimal("0"))
        assert tax == Decimal("0")

    def test_regular_monthly_income(self):
        """Test: zwykły miesięczny dochód."""
        monthly_income = Decimal("10000")
        tax = calculate_monthly_tax_advance_scale(monthly_income)

        # Uproszczone obliczenie miesięczne
        # Miesięczna redukcja: 3600 / 12 = 300
        # Podatek: 10000 * 0.12 - 300 = 1200 - 300 = 900
        assert tax > Decimal("0")
        assert isinstance(tax, Decimal)


class TestCalculateNetIncomeScale:
    """Testy obliczania dochodu netto po podatku."""

    def test_net_income_calculation(self):
        """Test: dochód netto = przychód - koszty - podatek."""
        revenue = Decimal("100000")
        costs = Decimal("20000")
        net = calculate_net_income_scale(revenue, costs)

        # Dochód: 100000 - 20000 = 80000
        # Podatek: 80000 * 0.12 - 3600 = 9600 - 3600 = 6000
        # Netto: 80000 - 6000 = 74000
        income = revenue - costs
        tax = calculate_income_tax_scale(income)
        expected = income - tax

        assert net == expected.quantize(Decimal("0.01"))

    def test_net_income_with_loss(self):
        """Test: strata (koszty > przychód) = zero netto."""
        revenue = Decimal("10000")
        costs = Decimal("20000")
        net = calculate_net_income_scale(revenue, costs)
        assert net == Decimal("0")

    def test_net_income_is_positive(self):
        """Test: dochód netto nie może być ujemny."""
        revenue = Decimal("50000")
        costs = Decimal("10000")
        net = calculate_net_income_scale(revenue, costs)
        assert net >= Decimal("0")
