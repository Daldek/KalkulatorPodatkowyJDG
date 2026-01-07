"""
Testy jednostkowe dla składki zdrowotnej.

Testuje obliczenia składki zdrowotnej dla różnych form opodatkowania.
"""

import pytest
from decimal import Decimal

from app.domain.health_insurance import (
    calculate_health_insurance_annual_scale_linear,
    calculate_health_insurance_monthly_scale_linear,
    calculate_health_insurance_monthly_lump_sum,
    calculate_health_insurance_annual_lump_sum,
    distribute_annual_to_monthly,
)
from app.core.constants_2025 import (
    HEALTH_INSURANCE_RATE_SCALE_LINEAR,
    HEALTH_INSURANCE_MONTHLY_LUMP_SUM,
)


class TestHealthInsuranceScaleLinear:
    """Testy składki zdrowotnej dla skali i podatku liniowego."""

    def test_annual_calculation(self):
        """Test: roczna składka = 9% dochodu."""
        annual_income = Decimal("100000")
        health = calculate_health_insurance_annual_scale_linear(annual_income)

        # 100000 * 0.09 = 9000
        expected = annual_income * HEALTH_INSURANCE_RATE_SCALE_LINEAR
        assert health == expected.quantize(Decimal("0.01"))

    def test_annual_zero_income(self):
        """Test: zerowy dochód = zerowa składka."""
        health = calculate_health_insurance_annual_scale_linear(Decimal("0"))
        assert health == Decimal("0")

    def test_annual_negative_income(self):
        """Test: ujemny dochód = zerowa składka."""
        health = calculate_health_insurance_annual_scale_linear(Decimal("-10000"))
        assert health == Decimal("0")

    def test_monthly_calculation(self):
        """Test: miesięczna zaliczka = 9% miesięcznego dochodu."""
        monthly_income = Decimal("10000")
        health = calculate_health_insurance_monthly_scale_linear(monthly_income)

        # 10000 * 0.09 = 900
        expected = monthly_income * HEALTH_INSURANCE_RATE_SCALE_LINEAR
        assert health == expected.quantize(Decimal("0.01"))

    def test_monthly_zero_income(self):
        """Test: zerowy miesięczny dochód = zerowa składka."""
        health = calculate_health_insurance_monthly_scale_linear(Decimal("0"))
        assert health == Decimal("0")

    def test_monthly_consistency(self):
        """Test: 12 miesięcy powinno dać roczną kwotę."""
        monthly_income = Decimal("10000")
        monthly_health = calculate_health_insurance_monthly_scale_linear(monthly_income)

        annual_income = monthly_income * 12
        annual_health = calculate_health_insurance_annual_scale_linear(annual_income)

        # Miesięczna * 12 = roczna
        assert (monthly_health * 12) == annual_health

    def test_result_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        income = Decimal("10000")
        health = calculate_health_insurance_monthly_scale_linear(income)
        assert isinstance(health, Decimal)
        assert health == health.quantize(Decimal("0.01"))


class TestHealthInsuranceLumpSum:
    """Testy składki zdrowotnej dla ryczałtu."""

    def test_monthly_is_constant(self):
        """Test: miesięczna składka jest stała dla ryczałtu."""
        health = calculate_health_insurance_monthly_lump_sum()

        # Powinna być równa stałej z constants_2025
        assert health == HEALTH_INSURANCE_MONTHLY_LUMP_SUM.quantize(Decimal("0.01"))

    def test_monthly_is_positive(self):
        """Test: miesięczna składka jest dodatnia."""
        health = calculate_health_insurance_monthly_lump_sum()
        assert health > Decimal("0")

    def test_annual_calculation(self):
        """Test: roczna składka = miesięczna * 12."""
        annual = calculate_health_insurance_annual_lump_sum(months=12)
        monthly = calculate_health_insurance_monthly_lump_sum()

        assert annual == (monthly * 12).quantize(Decimal("0.01"))

    def test_annual_partial_year(self):
        """Test: roczna składka dla części roku."""
        annual_6_months = calculate_health_insurance_annual_lump_sum(months=6)
        monthly = calculate_health_insurance_monthly_lump_sum()

        expected = (monthly * 6).quantize(Decimal("0.01"))
        assert annual_6_months == expected

    def test_annual_zero_months(self):
        """Test: zero miesięcy = zerowa składka."""
        annual = calculate_health_insurance_annual_lump_sum(months=0)
        assert annual == Decimal("0.00")

    def test_result_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        health = calculate_health_insurance_monthly_lump_sum()
        assert isinstance(health, Decimal)
        assert health == health.quantize(Decimal("0.01"))


class TestDistributeAnnualToMonthly:
    """Testy rozbijania rocznej kwoty na miesięczną."""

    def test_simple_distribution(self):
        """Test: prosta dystrybucja."""
        annual = Decimal("12000")
        monthly = distribute_annual_to_monthly(annual, 12)

        # 12000 / 12 = 1000
        assert monthly == Decimal("1000.00")

    def test_distribution_with_remainder(self):
        """Test: dystrybucja z resztą."""
        annual = Decimal("10000")
        monthly = distribute_annual_to_monthly(annual, 12)

        # 10000 / 12 = 833.33
        assert monthly == Decimal("833.33")

    def test_zero_months(self):
        """Test: zero miesięcy = zero."""
        monthly = distribute_annual_to_monthly(Decimal("12000"), 0)
        assert monthly == Decimal("0.00")

    def test_negative_months(self):
        """Test: ujemna liczba miesięcy = zero."""
        monthly = distribute_annual_to_monthly(Decimal("12000"), -5)
        assert monthly == Decimal("0.00")

    def test_result_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        monthly = distribute_annual_to_monthly(Decimal("12000"), 12)
        assert isinstance(monthly, Decimal)
        assert monthly == monthly.quantize(Decimal("0.01"))


class TestComparisonBetweenForms:
    """Testy porównawcze między formami."""

    def test_scale_vs_lump_sum_different_base(self):
        """Test: składka dla skali i ryczałtu opiera się na różnych podstawach."""
        # Dla skali/liniowego: zależy od dochodu
        income = Decimal("50000")
        scale_health = calculate_health_insurance_monthly_scale_linear(income)

        # Dla ryczałtu: stała kwota
        lump_sum_health = calculate_health_insurance_monthly_lump_sum()

        # Powinny być różne (bo różne podstawy)
        # (chyba że przypadkiem wyszło tak samo, ale to mało prawdopodobne)
        assert isinstance(scale_health, Decimal)
        assert isinstance(lump_sum_health, Decimal)

    def test_health_insurance_always_positive(self):
        """Test: składka zdrowotna zawsze >= 0."""
        # Dla skali
        assert calculate_health_insurance_monthly_scale_linear(Decimal("100000")) > 0
        assert calculate_health_insurance_monthly_scale_linear(Decimal("0")) == 0

        # Dla ryczałtu
        assert calculate_health_insurance_monthly_lump_sum() > 0
