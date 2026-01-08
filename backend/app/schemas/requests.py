"""
Schematy requestów API (Pydantic).

Definiują strukturę danych wejściowych od użytkownika.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, List
from decimal import Decimal
from datetime import date


class OneTimeCost(BaseModel):
    """
    Koszt jednorazowy.

    Attributes
    ----------
    month_index : int
        Indeks miesiąca (0-59), w którym występuje koszt.
    amount : Decimal
        Kwota kosztu w PLN.
    """

    month_index: int = Field(..., ge=0, le=59, description="Indeks miesiąca (0-59)")
    amount: Decimal = Field(..., gt=0, description="Kwota kosztu w PLN")


class LumpSumMonthlyRevenue(BaseModel):
    """
    Przychody ryczałtowe dla pojedynczego miesiąca.

    Attributes
    ----------
    month_index : int
        Indeks miesiąca (0-59).
    revenues_by_rate : Dict[str, Decimal]
        Słownik: {"stawka": kwota_przychodu}.
        Przykład: {"0.055": 50000, "0.085": 30000}
    """

    month_index: int = Field(..., ge=0, le=59, description="Indeks miesiąca (0-59)")
    revenues_by_rate: Dict[str, Decimal] = Field(
        ..., description="Przychody według stawek ryczałtu"
    )

    @field_validator("revenues_by_rate")
    @classmethod
    def validate_rates(cls, v):
        """Waliduje stawki ryczałtu."""
        for rate_str, amount in v.items():
            try:
                rate = Decimal(rate_str)
                if rate <= 0 or rate >= 1:
                    raise ValueError(
                        f"Stawka ryczałtu musi być między 0 a 1, otrzymano: {rate}"
                    )
                if amount < 0:
                    raise ValueError(
                        f"Kwota przychodu nie może być ujemna: {amount}"
                    )
            except Exception as e:
                raise ValueError(f"Niepoprawna stawka ryczałtu '{rate_str}': {e}")
        return v


class CalculationRequest(BaseModel):
    """
    Request do kalkulacji podatkowej.

    Attributes
    ----------
    base_month : str
        Miesiąc bazowy w formacie 'YYYY-MM'.
    business_start_date : date
        Data rozpoczęcia działalności gospodarczej.
    monthly_revenues : List[Decimal]
        Lista przychodów miesięcznych (60 wartości).
        Dla skali podatkowej i podatku liniowego.
    monthly_costs_fixed : Decimal
        Stałe koszty miesięczne w PLN.
    one_time_costs : Optional[List[OneTimeCost]]
        Lista kosztów jednorazowych (opcjonalne).
    lump_sum_revenues : Optional[List[LumpSumMonthlyRevenue]]
        Lista przychodów ryczałtowych (opcjonalne, dla formy ryczałtu).
    """

    base_month: str = Field(
        ...,
        pattern=r"^\d{4}-(0[1-9]|1[0-2])$",
        description="Miesiąc bazowy w formacie YYYY-MM",
        examples=["2025-01"],
    )
    business_start_date: date = Field(
        ...,
        description="Data rozpoczęcia działalności gospodarczej",
        examples=["2025-01-01"],
    )
    monthly_revenues: List[Decimal] = Field(
        ...,
        min_length=60,
        max_length=60,
        description="Lista 60 przychodów miesięcznych w PLN (dla skali i liniowego)",
    )
    monthly_costs: List[Decimal] = Field(
        ...,
        min_length=60,
        max_length=60,
        description="Lista 60 kosztów miesięcznych w PLN",
    )
    one_time_costs: Optional[List[OneTimeCost]] = Field(
        default=None, description="Lista kosztów jednorazowych (opcjonalne)"
    )
    lump_sum_revenues: Optional[List[LumpSumMonthlyRevenue]] = Field(
        default=None,
        description="Lista przychodów ryczałtowych dla 60 miesięcy (opcjonalne)",
    )

    @field_validator("monthly_revenues")
    @classmethod
    def validate_revenues(cls, v):
        """Waliduje przychody miesięczne."""
        if any(rev < 0 for rev in v):
            raise ValueError("Przychody miesięczne nie mogą być ujemne")
        return v

    @field_validator("monthly_costs")
    @classmethod
    def validate_costs(cls, v):
        """Waliduje koszty miesięczne."""
        if any(cost < 0 for cost in v):
            raise ValueError("Koszty miesięczne nie mogą być ujemne")
        return v

    @field_validator("lump_sum_revenues")
    @classmethod
    def validate_lump_sum_length(cls, v):
        """Waliduje długość listy przychodów ryczałtowych."""
        if v is not None and len(v) != 60:
            raise ValueError(
                f"Lista przychodów ryczałtowych musi mieć 60 elementów, otrzymano: {len(v)}"
            )
        return v

    class Config:
        """Konfiguracja Pydantic."""

        json_schema_extra = {
            "example": {
                "base_month": "2025-01",
                "business_start_date": "2025-01-01",
                "monthly_revenues": [50000] * 60,
                "monthly_costs_fixed": 5000,
                "one_time_costs": [
                    {"month_index": 0, "amount": 10000},
                    {"month_index": 12, "amount": 5000},
                ],
                "lump_sum_revenues": [
                    {"month_index": i, "revenues_by_rate": {"0.055": 50000}}
                    for i in range(60)
                ],
            }
        }
