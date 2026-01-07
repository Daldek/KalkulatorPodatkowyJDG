"""
Stałe podatkowe i składkowe dla roku 2025.

Wszystkie wartości finansowe w PLN.
Przepisy zamrożone na stan prawny obowiązujący w 2025.
"""

from decimal import Decimal

# ====================================
# SKALA PODATKOWA
# ====================================

TAX_SCALE_THRESHOLD = Decimal("120000")  # Pierwszy próg podatkowy
TAX_SCALE_RATE_LOW = Decimal("0.12")  # 12% do progu
TAX_SCALE_RATE_HIGH = Decimal("0.32")  # 32% powyżej progu
TAX_FREE_AMOUNT = Decimal("30000")  # Kwota wolna od podatku

# Kwota zmniejszająca podatek
TAX_REDUCTION_AMOUNT = Decimal("3600")  # 12% z 30 000


# ====================================
# PODATEK LINIOWY
# ====================================

LINEAR_TAX_RATE = Decimal("0.19")  # 19%


# ====================================
# RYCZAŁT OD PRZYCHODÓW EWIDENCJONOWANYCH
# ====================================

# Dostępne stawki ryczałtu w 2025
LUMP_SUM_RATES = {
    Decimal("0.02"): "Sprzedaż towarów i produktów przemysłowych (niskie stawki)",
    Decimal("0.03"): "Usługi transportowe, działalność produkcyjna",
    Decimal("0.055"): "Usługi programistyczne, IT",
    Decimal("0.085"): "Działalność gastronomiczna, handlowa",
    Decimal("0.10"): "Wolne zawody - lekarze, prawnicy (do limitu)",
    Decimal("0.12"): "Usługi remontowo-budowlane",
    Decimal("0.14"): "Wolne zawody (powyżej limitu)",
    Decimal("0.15"): "Usługi niematerialne, consulting",
    Decimal("0.17"): "Wolne zawody - najwyższa stawka",
}

# Limit przychodu dla stawki 10% w wolnych zawodach
LUMP_SUM_PROFESSION_LIMIT = Decimal("200000")


# ====================================
# ZUS - SKŁADKI SPOŁECZNE
# ====================================

# Ulga na start (6 miesięcy) - całkowite zwolnienie
ZUS_RELIEF_MONTHS = 6
ZUS_RELIEF_MONTHLY = Decimal("0")

# Preferencyjny ZUS (24 miesiące)
ZUS_PREFERENTIAL_MONTHS = 24
ZUS_PREFERENTIAL_MONTHLY = Decimal("626.49")  # 2025

# Pełny ZUS
ZUS_FULL_MONTHLY = Decimal("1860.88")  # 2025 (emerytalna + rentowa + chorobowa + wypadkowa + FP + FGŚP)

# Składki szczegółowe dla pełnego ZUS (dla referencji)
ZUS_FULL_COMPONENTS = {
    "emerytalna": Decimal("426.28"),
    "rentowa": Decimal("348.47"),
    "chorobowa": Decimal("122.45"),
    "wypadkowa": Decimal("70.13"),
    "fundusz_pracy": Decimal("122.45"),
    "fgsp": Decimal("5.10"),
}

# Minimalna podstawa wymiaru składek ZUS 2025
ZUS_MIN_BASE = Decimal("4694.40")  # 60% prognozowanego przeciętnego wynagrodzenia


# ====================================
# SKŁADKA ZDROWOTNA
# ====================================

# Minimalne wynagrodzenie 2025
MINIMUM_WAGE_2025 = Decimal("4666")  # Od 1 stycznia 2025

# Składka zdrowotna dla skali podatkowej
# 9% dochodu, ale nie mniej niż 9% z 75% minimalnego wynagrodzenia
HEALTH_INSURANCE_RATE_SCALE = Decimal("0.09")
HEALTH_INSURANCE_BASE_MIN_SCALE = MINIMUM_WAGE_2025 * Decimal("0.75")
HEALTH_INSURANCE_MIN_MONTHLY_SCALE = HEALTH_INSURANCE_BASE_MIN_SCALE * Decimal("0.09")  # ~314.96 PLN

# Składka zdrowotna dla podatku liniowego
# 4.9% dochodu, ale nie mniej niż 9% z 75% minimalnego wynagrodzenia
HEALTH_INSURANCE_RATE_LINEAR = Decimal("0.049")
HEALTH_INSURANCE_BASE_MIN_LINEAR = MINIMUM_WAGE_2025 * Decimal("0.75")
HEALTH_INSURANCE_MIN_MONTHLY_LINEAR = HEALTH_INSURANCE_BASE_MIN_LINEAR * Decimal("0.09")  # ~314.96 PLN

# Składka zdrowotna dla ryczałtu
# Ryczałt: 9% od 75% przeciętnego wynagrodzenia
AVERAGE_SALARY_2025 = Decimal("8213.76")  # Prognoza na 2025
HEALTH_INSURANCE_BASE_LUMP_SUM = AVERAGE_SALARY_2025 * Decimal("0.75")
HEALTH_INSURANCE_MONTHLY_LUMP_SUM = (
    HEALTH_INSURANCE_BASE_LUMP_SUM * Decimal("0.09")
)  # ~554.53 PLN/m-c


# ====================================
# INNE LIMITY I PROGI
# ====================================

# Limit przychodów dla małego ZUS plus
SMALL_ZUS_PLUS_LIMIT = Decimal("120000")  # Nie używane w v1.0

# Limit przychodów dla ryczałtu
LUMP_SUM_REVENUE_LIMIT = Decimal("2000000")

# Limit przychodów dla księgi przychodów i rozchodów
TAX_BOOK_REVENUE_LIMIT = Decimal("2000000")


# ====================================
# WALIDACJA
# ====================================

def validate_constants():
    """
    Waliduje poprawność stałych podatkowych.

    Raises
    ------
    ValueError
        Jeśli stałe są niespójne lub błędne.

    Notes
    -----
    Funkcja pomocnicza do sprawdzenia poprawności danych konfiguracyjnych.
    """
    assert TAX_SCALE_THRESHOLD > 0
    assert 0 < TAX_SCALE_RATE_LOW < 1
    assert 0 < TAX_SCALE_RATE_HIGH < 1
    assert TAX_SCALE_RATE_HIGH > TAX_SCALE_RATE_LOW
    assert TAX_FREE_AMOUNT >= 0
    assert 0 < LINEAR_TAX_RATE < 1
    assert ZUS_RELIEF_MONTHS > 0
    assert ZUS_PREFERENTIAL_MONTHS > 0
    assert ZUS_FULL_MONTHLY > ZUS_PREFERENTIAL_MONTHLY >= ZUS_RELIEF_MONTHLY
    assert HEALTH_INSURANCE_RATE_SCALE > 0
    assert HEALTH_INSURANCE_RATE_LINEAR > 0
    assert HEALTH_INSURANCE_MIN_MONTHLY_SCALE > 0
    assert HEALTH_INSURANCE_MIN_MONTHLY_LINEAR > 0
    assert HEALTH_INSURANCE_MONTHLY_LUMP_SUM > 0


# Uruchom walidację przy imporcie
validate_constants()
