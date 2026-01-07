"""
Testy jednostkowe dla ryczałtu.

Testuje obliczenia podatku ryczałtowego z wieloma stawkami.
"""

import pytest
from decimal import Decimal

from app.domain.lump_sum import (
    calculate_tax_lump_sum,
    calculate_monthly_tax_lump_sum,
    calculate_annual_tax_lump_sum,
    calculate_net_income_lump_sum,
    aggregate_revenue_by_rate,
    validate_lump_sum_rates,
)


class TestCalculateTaxLumpSum:
    """Testy obliczania podatku ryczałtowego."""

    def test_single_rate(self):
        """Test: jedna stawka."""
        revenue_by_rate = {Decimal("0.055"): Decimal("100000")}
        tax = calculate_tax_lump_sum(revenue_by_rate)

        # 100000 * 0.055 = 5500
        expected = Decimal("5500.00")
        assert tax == expected

    def test_multiple_rates(self):
        """Test: wiele stawek jednocześnie."""
        revenue_by_rate = {
            Decimal("0.055"): Decimal("50000"),  # IT: 50000 * 0.055 = 2750
            Decimal("0.085"): Decimal("30000"),  # Handel: 30000 * 0.085 = 2550
        }
        tax = calculate_tax_lump_sum(revenue_by_rate)

        # Suma: 2750 + 2550 = 5300
        expected = Decimal("5300.00")
        assert tax == expected

    def test_zero_revenue(self):
        """Test: zerowy przychód = zerowy podatek."""
        revenue_by_rate = {Decimal("0.055"): Decimal("0")}
        tax = calculate_tax_lump_sum(revenue_by_rate)
        assert tax == Decimal("0.00")

    def test_empty_dict(self):
        """Test: pusty słownik = zerowy podatek."""
        revenue_by_rate = {}
        tax = calculate_tax_lump_sum(revenue_by_rate)
        assert tax == Decimal("0.00")

    def test_various_rates(self):
        """Test: różne dostępne stawki."""
        revenue_by_rate = {
            Decimal("0.02"): Decimal("10000"),   # 200
            Decimal("0.03"): Decimal("10000"),   # 300
            Decimal("0.055"): Decimal("10000"),  # 550
            Decimal("0.085"): Decimal("10000"),  # 850
        }
        tax = calculate_tax_lump_sum(revenue_by_rate)

        # Suma: 200 + 300 + 550 + 850 = 1900
        expected = Decimal("1900.00")
        assert tax == expected

    def test_tax_is_decimal(self):
        """Test: wynik jest Decimal z 2 miejscami po przecinku."""
        revenue_by_rate = {Decimal("0.055"): Decimal("100000")}
        tax = calculate_tax_lump_sum(revenue_by_rate)
        assert isinstance(tax, Decimal)
        assert tax == tax.quantize(Decimal("0.01"))


class TestCalculateMonthlyTaxLumpSum:
    """Testy miesięcznego podatku ryczałtowego."""

    def test_monthly_equals_general(self):
        """Test: miesięczny podatek używa tej samej funkcji."""
        revenue_by_rate = {Decimal("0.055"): Decimal("10000")}

        monthly = calculate_monthly_tax_lump_sum(revenue_by_rate)
        general = calculate_tax_lump_sum(revenue_by_rate)

        assert monthly == general


class TestCalculateAnnualTaxLumpSum:
    """Testy rocznego podatku ryczałtowego."""

    def test_annual_equals_general(self):
        """Test: roczny podatek używa tej samej funkcji."""
        revenue_by_rate = {Decimal("0.055"): Decimal("120000")}

        annual = calculate_annual_tax_lump_sum(revenue_by_rate)
        general = calculate_tax_lump_sum(revenue_by_rate)

        assert annual == general


class TestCalculateNetIncomeLumpSum:
    """Testy obliczania dochodu netto dla ryczałtu."""

    def test_net_income_single_rate(self):
        """Test: dochód netto = przychód - podatek."""
        revenue_by_rate = {Decimal("0.055"): Decimal("100000")}
        net = calculate_net_income_lump_sum(revenue_by_rate)

        # Przychód: 100000
        # Podatek: 100000 * 0.055 = 5500
        # Netto: 100000 - 5500 = 94500
        expected = Decimal("94500.00")
        assert net == expected

    def test_net_income_multiple_rates(self):
        """Test: dochód netto z wieloma stawkami."""
        revenue_by_rate = {
            Decimal("0.055"): Decimal("50000"),
            Decimal("0.085"): Decimal("30000"),
        }
        net = calculate_net_income_lump_sum(revenue_by_rate)

        # Przychód: 50000 + 30000 = 80000
        # Podatek: (50000 * 0.055) + (30000 * 0.085) = 2750 + 2550 = 5300
        # Netto: 80000 - 5300 = 74700
        expected = Decimal("74700.00")
        assert net == expected

    def test_costs_are_ignored(self):
        """Test: ryczałt ignoruje koszty (to właściwość funkcji calculate_net_income_lump_sum)."""
        # Funkcja nie przyjmuje parametru costs, więc koszty są ignorowane
        revenue_by_rate = {Decimal("0.055"): Decimal("100000")}
        net = calculate_net_income_lump_sum(revenue_by_rate)

        # Tylko przychód i podatek, brak kosztów
        assert net > Decimal("0")


class TestAggregateRevenueByRate:
    """Testy agregacji przychodów według stawek."""

    def test_single_month(self):
        """Test: jeden miesiąc."""
        monthly_revenues = [
            {Decimal("0.055"): Decimal("10000")}
        ]
        aggregated = aggregate_revenue_by_rate(monthly_revenues)

        assert aggregated == {Decimal("0.055"): Decimal("10000")}

    def test_multiple_months_same_rate(self):
        """Test: wiele miesięcy z tą samą stawką."""
        monthly_revenues = [
            {Decimal("0.055"): Decimal("10000")},
            {Decimal("0.055"): Decimal("15000")},
            {Decimal("0.055"): Decimal("20000")},
        ]
        aggregated = aggregate_revenue_by_rate(monthly_revenues)

        # Suma: 10000 + 15000 + 20000 = 45000
        assert aggregated == {Decimal("0.055"): Decimal("45000")}

    def test_multiple_months_multiple_rates(self):
        """Test: wiele miesięcy z różnymi stawkami."""
        monthly_revenues = [
            {Decimal("0.055"): Decimal("10000"), Decimal("0.085"): Decimal("5000")},
            {Decimal("0.055"): Decimal("15000")},
            {Decimal("0.085"): Decimal("10000")},
        ]
        aggregated = aggregate_revenue_by_rate(monthly_revenues)

        expected = {
            Decimal("0.055"): Decimal("25000"),  # 10000 + 15000
            Decimal("0.085"): Decimal("15000"),  # 5000 + 10000
        }
        assert aggregated == expected

    def test_empty_list(self):
        """Test: pusta lista = pusty słownik."""
        monthly_revenues = []
        aggregated = aggregate_revenue_by_rate(monthly_revenues)
        assert aggregated == {}


class TestValidateLumpSumRates:
    """Testy walidacji stawek ryczałtu."""

    def test_valid_rates(self):
        """Test: poprawne stawki."""
        revenue_by_rate = {
            Decimal("0.055"): Decimal("10000"),
            Decimal("0.085"): Decimal("20000"),
        }
        assert validate_lump_sum_rates(revenue_by_rate) is True

    def test_invalid_rate_zero(self):
        """Test: stawka zerowa jest niepoprawna."""
        revenue_by_rate = {Decimal("0"): Decimal("10000")}
        assert validate_lump_sum_rates(revenue_by_rate) is False

    def test_invalid_rate_negative(self):
        """Test: stawka ujemna jest niepoprawna."""
        revenue_by_rate = {Decimal("-0.05"): Decimal("10000")}
        assert validate_lump_sum_rates(revenue_by_rate) is False

    def test_invalid_rate_too_high(self):
        """Test: stawka >= 1 jest niepoprawna."""
        revenue_by_rate = {Decimal("1.0"): Decimal("10000")}
        assert validate_lump_sum_rates(revenue_by_rate) is False

    def test_empty_dict_is_valid(self):
        """Test: pusty słownik jest poprawny."""
        revenue_by_rate = {}
        assert validate_lump_sum_rates(revenue_by_rate) is True
