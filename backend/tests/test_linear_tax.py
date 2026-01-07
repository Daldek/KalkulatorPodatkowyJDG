"""
Testy jednostkowe dla podatku liniowego.

Testuje obliczenia podatku według stawki 19%.
"""

import pytest
from decimal import Decimal

from app.domain.linear_tax import (
    calculate_income_tax_linear,
    calculate_monthly_tax_advance_linear,
    calculate_net_income_linear,
)
from app.core.constants_2025 import LINEAR_TAX_RATE


class TestCalculateIncomeTaxLinear:
    """Testy obliczania rocznego podatku liniowego."""

    def test_zero_income(self):
        """Test: zerowy dochód = zerowy podatek."""
        tax = calculate_income_tax_linear(Decimal("0"))
        assert tax == Decimal("0")

    def test_negative_income(self):
        """Test: ujemny dochód = zerowy podatek."""
        tax = calculate_income_tax_linear(Decimal("-10000"))
        assert tax == Decimal("0")

    def test_simple_calculation(self):
        """Test: prosty przykład obliczenia."""
        income = Decimal("100000")
        tax = calculate_income_tax_linear(income)

        # 100000 * 0.19 = 19000
        expected = income * LINEAR_TAX_RATE
        assert tax == expected.quantize(Decimal("0.01"))

    def test_large_income(self):
        """Test: duży dochód."""
        income = Decimal("500000")
        tax = calculate_income_tax_linear(income)

        # 500000 * 0.19 = 95000
        expected = income * LINEAR_TAX_RATE
        assert tax == expected.quantize(Decimal("0.01"))

    def test_fractional_income(self):
        """Test: dochód z częściami ułamkowymi."""
        income = Decimal("123456.78")
        tax = calculate_income_tax_linear(income)

        # 123456.78 * 0.19 = 23456.79
        expected = income * LINEAR_TAX_RATE
        assert tax == expected.quantize(Decimal("0.01"))

    def test_tax_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        income = Decimal("100000")
        tax = calculate_income_tax_linear(income)
        assert isinstance(tax, Decimal)
        assert tax == tax.quantize(Decimal("0.01"))


class TestCalculateMonthlyTaxAdvanceLinear:
    """Testy miesięcznej zaliczki na podatek liniowy."""

    def test_zero_income(self):
        """Test: zerowy miesięczny dochód = zero podatku."""
        tax = calculate_monthly_tax_advance_linear(Decimal("0"))
        assert tax == Decimal("0")

    def test_monthly_calculation(self):
        """Test: miesięczna zaliczka."""
        monthly_income = Decimal("10000")
        tax = calculate_monthly_tax_advance_linear(monthly_income)

        # 10000 * 0.19 = 1900
        expected = monthly_income * LINEAR_TAX_RATE
        assert tax == expected.quantize(Decimal("0.01"))

    def test_consistency_with_annual(self):
        """Test: 12 miesięcy powinno dać podobny wynik jak roczny."""
        monthly_income = Decimal("10000")
        monthly_tax = calculate_monthly_tax_advance_linear(monthly_income)

        annual_income = monthly_income * 12
        annual_tax = calculate_income_tax_linear(annual_income)

        # Miesięczny * 12 powinien być równy rocznemu
        assert (monthly_tax * 12) == annual_tax


class TestCalculateNetIncomeLinear:
    """Testy obliczania dochodu netto po podatku liniowym."""

    def test_net_income_calculation(self):
        """Test: dochód netto = przychód - koszty - podatek."""
        revenue = Decimal("100000")
        costs = Decimal("20000")
        net = calculate_net_income_linear(revenue, costs)

        # Dochód: 100000 - 20000 = 80000
        # Podatek: 80000 * 0.19 = 15200
        # Netto: 80000 - 15200 = 64800
        income = revenue - costs
        tax = calculate_income_tax_linear(income)
        expected = income - tax

        assert net == expected.quantize(Decimal("0.01"))

    def test_net_income_with_loss(self):
        """Test: strata (koszty > przychód) = zero netto."""
        revenue = Decimal("10000")
        costs = Decimal("20000")
        net = calculate_net_income_linear(revenue, costs)
        assert net == Decimal("0")

    def test_net_income_is_positive(self):
        """Test: dochód netto nie może być ujemny."""
        revenue = Decimal("50000")
        costs = Decimal("10000")
        net = calculate_net_income_linear(revenue, costs)
        assert net >= Decimal("0")

    def test_comparison_with_scale(self):
        """Test: dla niektórych dochodów liniowy może dać inny wynik niż skala."""
        from app.domain.tax_scale import calculate_net_income_scale

        revenue = Decimal("200000")
        costs = Decimal("50000")

        net_scale = calculate_net_income_scale(revenue, costs)
        net_linear = calculate_net_income_linear(revenue, costs)

        # Dla dużych dochodów liniowy może być mniej korzystny niż skala
        # (ale to zależy od konkretnych wartości)
        assert isinstance(net_scale, Decimal)
        assert isinstance(net_linear, Decimal)
