"""
Testy jednostkowe dla modułu ZUS.

Testuje automatyczne rozpoznawanie etapów ZUS i obliczanie składek.
"""

import pytest
from datetime import date
from decimal import Decimal

from app.domain.zus import (
    calculate_months_since_start,
    determine_zus_stage,
    calculate_zus_monthly,
)
from app.core.constants_2025 import (
    ZUS_RELIEF_MONTHLY,
    ZUS_PREFERENTIAL_MONTHLY,
    ZUS_FULL_MONTHLY,
)


class TestCalculateMonthsSinceStart:
    """Testy obliczania liczby miesięcy od rozpoczęcia działalności."""

    def test_same_month(self):
        """Test: ten sam miesiąc = 0 miesięcy."""
        start = date(2025, 1, 15)
        current = date(2025, 1, 20)
        assert calculate_months_since_start(start, current) == 0

    def test_one_month_later(self):
        """Test: miesiąc później = 1 miesiąc."""
        start = date(2025, 1, 15)
        current = date(2025, 2, 15)
        assert calculate_months_since_start(start, current) == 1

    def test_six_months_later(self):
        """Test: 6 miesięcy później."""
        start = date(2025, 1, 1)
        current = date(2025, 7, 1)
        assert calculate_months_since_start(start, current) == 6

    def test_one_year_later(self):
        """Test: rok później = 12 miesięcy."""
        start = date(2025, 1, 1)
        current = date(2026, 1, 1)
        assert calculate_months_since_start(start, current) == 12

    def test_partial_month_counted_as_full(self):
        """Test: niepełny miesiąc liczony jako pełny miesiąc kalendarzowy."""
        start = date(2025, 1, 15)
        current = date(2025, 2, 10)
        # Styczeń = miesiąc 0, luty = miesiąc 1 (pełne miesiące kalendarzowe)
        assert calculate_months_since_start(start, current) == 1


class TestDetermineZusStage:
    """Testy określania etapu ZUS."""

    def test_relief_stage_first_month(self):
        """Test: pierwszy miesiąc = ulga na start."""
        start = date(2025, 1, 1)
        current = date(2025, 1, 1)
        assert determine_zus_stage(start, current) == "relief"

    def test_relief_stage_last_month(self):
        """Test: ostatni miesiąc ulgi (miesiąc 5)."""
        start = date(2025, 1, 1)
        current = date(2025, 6, 1)
        assert determine_zus_stage(start, current) == "relief"

    def test_preferential_stage_first_month(self):
        """Test: pierwszy miesiąc preferencyjnego (miesiąc 6)."""
        start = date(2025, 1, 1)
        current = date(2025, 7, 1)
        assert determine_zus_stage(start, current) == "preferential"

    def test_preferential_stage_middle(self):
        """Test: środek okresu preferencyjnego."""
        start = date(2025, 1, 1)
        current = date(2026, 1, 1)  # 12 miesięcy
        assert determine_zus_stage(start, current) == "preferential"

    def test_preferential_stage_last_month(self):
        """Test: ostatni miesiąc preferencyjnego (miesiąc 29)."""
        start = date(2025, 1, 1)
        current = date(2027, 6, 1)  # 29 miesięcy
        assert determine_zus_stage(start, current) == "preferential"

    def test_full_stage_first_month(self):
        """Test: pierwszy miesiąc pełnego ZUS (miesiąc 30)."""
        start = date(2025, 1, 1)
        current = date(2027, 7, 1)  # 30 miesięcy
        assert determine_zus_stage(start, current) == "full"

    def test_full_stage_much_later(self):
        """Test: kilka lat później = pełny ZUS."""
        start = date(2025, 1, 1)
        current = date(2030, 1, 1)  # 60 miesięcy
        assert determine_zus_stage(start, current) == "full"


class TestCalculateZusMonthly:
    """Testy obliczania miesięcznej składki ZUS."""

    def test_relief_amount(self):
        """Test: kwota ZUS podczas ulgi."""
        start = date(2025, 1, 1)
        current = date(2025, 1, 1)
        zus = calculate_zus_monthly(start, current)
        assert zus == ZUS_RELIEF_MONTHLY
        assert zus == Decimal("0")

    def test_preferential_amount(self):
        """Test: kwota ZUS preferencyjnego."""
        start = date(2025, 1, 1)
        current = date(2025, 7, 1)  # Miesiąc 6 - preferencyjny
        zus = calculate_zus_monthly(start, current)
        assert zus == ZUS_PREFERENTIAL_MONTHLY

    def test_full_amount(self):
        """Test: kwota pełnego ZUS."""
        start = date(2025, 1, 1)
        current = date(2027, 7, 1)  # Miesiąc 30 - pełny
        zus = calculate_zus_monthly(start, current)
        assert zus == ZUS_FULL_MONTHLY

    def test_amounts_are_positive_decimals(self):
        """Test: wszystkie kwoty są dodatnimi Decimal."""
        start = date(2025, 1, 1)

        # Ulga
        zus_relief = calculate_zus_monthly(start, date(2025, 1, 1))
        assert isinstance(zus_relief, Decimal)
        assert zus_relief >= 0

        # Preferencyjny
        zus_pref = calculate_zus_monthly(start, date(2025, 7, 1))
        assert isinstance(zus_pref, Decimal)
        assert zus_pref > 0

        # Pełny
        zus_full = calculate_zus_monthly(start, date(2027, 7, 1))
        assert isinstance(zus_full, Decimal)
        assert zus_full > 0

    def test_progression_of_amounts(self):
        """Test: progresja kwot ZUS (relief < preferential < full)."""
        start = date(2025, 1, 1)

        zus_relief = calculate_zus_monthly(start, date(2025, 1, 1))
        zus_pref = calculate_zus_monthly(start, date(2025, 7, 1))
        zus_full = calculate_zus_monthly(start, date(2027, 7, 1))

        assert zus_relief <= zus_pref < zus_full
