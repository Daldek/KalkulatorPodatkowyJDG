"""
Schematy odpowiedzi API (Pydantic).

Definiują strukturę danych zwracanych przez API.
"""

from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal


class PeriodSummaryResponse(BaseModel):
    """
    Podsumowanie za określony okres.

    Attributes
    ----------
    label : str
        Etykieta okresu (np. "Po 6 miesiącach (koniec ulgi ZUS)").
    months_count : int
        Liczba miesięcy w okresie.
    revenue : Decimal
        Suma przychodów za okres.
    costs : Decimal
        Suma kosztów za okres.
    income : Decimal
        Suma dochodu za okres.
    zus : Decimal
        Suma ZUS za okres.
    tax : Decimal
        Suma podatku za okres.
    health_insurance : Decimal
        Suma składki zdrowotnej za okres.
    total_contributions : Decimal
        Suma składek razem (ZUS + składka zdrowotna).
    total_burden : Decimal
        Suma obciążeń (ZUS + składka zdrowotna + podatek).
    net_income : Decimal
        Dochód netto za okres.
    """

    label: str
    months_count: int
    revenue: Decimal
    costs: Decimal
    income: Decimal
    zus: Decimal
    tax: Decimal
    health_insurance: Decimal
    total_contributions: Decimal
    total_burden: Decimal
    net_income: Decimal

    class Config:
        """Konfiguracja Pydantic."""

        from_attributes = True


class MonthlyDataResponse(BaseModel):
    """
    Dane miesięczne dla pojedynczego miesiąca.

    Attributes
    ----------
    month : str
        Miesiąc w formacie 'YYYY-MM'.
    revenue : Decimal
        Przychód w PLN.
    costs : Decimal
        Koszty w PLN.
    income : Decimal
        Dochód (przychód - koszty) w PLN.
    zus : Decimal
        Składka ZUS w PLN.
    """

    month: str
    revenue: Decimal
    costs: Decimal
    income: Decimal
    zus: Decimal

    class Config:
        """Konfiguracja Pydantic."""

        from_attributes = True


class TaxFormResultResponse(BaseModel):
    """
    Wynik obliczeń dla konkretnej formy opodatkowania.

    Attributes
    ----------
    form_name : str
        Nazwa formy: 'tax_scale', 'linear_tax', 'lump_sum'.
    months : List[str]
        Lista miesięcy w formacie 'YYYY-MM' (60 elementów).
    monthly_revenue : List[Decimal]
        Miesięczne przychody (60 wartości).
    monthly_costs : List[Decimal]
        Miesięczne koszty (60 wartości).
    monthly_income : List[Decimal]
        Miesięczny dochód (60 wartości).
    monthly_zus : List[Decimal]
        Miesięczny ZUS (60 wartości).
    monthly_tax : List[Decimal]
        Miesięczny podatek (60 wartości).
    monthly_health_insurance : List[Decimal]
        Miesięczna składka zdrowotna (60 wartości).
    monthly_net_income : List[Decimal]
        Miesięczny dochód netto po wszystkich obciążeniach (60 wartości).
    summary_6_months : PeriodSummaryResponse
        Podsumowanie po 6 miesiącach (koniec ulgi ZUS).
    summary_12_months : PeriodSummaryResponse
        Podsumowanie po 12 miesiącach (pierwszy rok).
    summary_30_months : PeriodSummaryResponse
        Podsumowanie po 30 miesiącach (koniec preferencyjnego ZUS).
    summary_60_months : PeriodSummaryResponse
        Podsumowanie po 60 miesiącach (5 lat).
    """

    form_name: str
    months: List[str]
    monthly_revenue: List[Decimal]
    monthly_costs: List[Decimal]
    monthly_income: List[Decimal]
    monthly_zus: List[Decimal]
    monthly_tax: List[Decimal]
    monthly_health_insurance: List[Decimal]
    monthly_net_income: List[Decimal]
    summary_6_months: PeriodSummaryResponse
    summary_12_months: PeriodSummaryResponse
    summary_30_months: PeriodSummaryResponse
    summary_60_months: PeriodSummaryResponse


class ComparisonResultResponse(BaseModel):
    """
    Porównanie wszystkich form opodatkowania.

    Attributes
    ----------
    tax_scale : TaxFormResultResponse
        Wyniki dla skali podatkowej.
    linear_tax : TaxFormResultResponse
        Wyniki dla podatku liniowego.
    lump_sum : TaxFormResultResponse
        Wyniki dla ryczałtu.
    best_form : str
        Nazwa najkorzystniejszej formy (najwyższy total_net_income).
    best_form_description : str
        Opis najkorzystniejszej formy.
    """

    tax_scale: TaxFormResultResponse
    linear_tax: TaxFormResultResponse
    lump_sum: TaxFormResultResponse
    best_form: str
    best_form_description: str = Field(
        ...,
        description="Informacyjny opis najkorzystniejszej formy (wynik matematyczny)",
    )

    class Config:
        """Konfiguracja Pydantic."""

        json_schema_extra = {
            "example": {
                "tax_scale": {
                    "form_name": "tax_scale",
                    "months": ["2025-01", "2025-02"],
                    "monthly_revenue": [50000, 50000],
                    "monthly_costs": [5000, 5000],
                    "monthly_income": [45000, 45000],
                    "monthly_zus": [0, 0],
                    "monthly_tax": [5100, 5100],
                    "monthly_health_insurance": [4050, 4050],
                    "monthly_net_income": [35850, 35850],
                    "total_revenue": 3000000,
                    "total_costs": 300000,
                    "total_income": 2700000,
                    "total_zus": 50000,
                    "total_tax": 306000,
                    "total_health_insurance": 243000,
                    "total_net_income": 2151000,
                },
                "linear_tax": {
                    "form_name": "linear_tax",
                    "months": ["2025-01", "2025-02"],
                    "monthly_revenue": [50000, 50000],
                    "monthly_costs": [5000, 5000],
                    "monthly_income": [45000, 45000],
                    "monthly_zus": [0, 0],
                    "monthly_tax": [8550, 8550],
                    "monthly_health_insurance": [4050, 4050],
                    "monthly_net_income": [32400, 32400],
                    "total_revenue": 3000000,
                    "total_costs": 300000,
                    "total_income": 2700000,
                    "total_zus": 50000,
                    "total_tax": 513000,
                    "total_health_insurance": 243000,
                    "total_net_income": 1944000,
                },
                "lump_sum": {
                    "form_name": "lump_sum",
                    "months": ["2025-01", "2025-02"],
                    "monthly_revenue": [50000, 50000],
                    "monthly_costs": [0, 0],
                    "monthly_income": [50000, 50000],
                    "monthly_zus": [0, 0],
                    "monthly_tax": [2750, 2750],
                    "monthly_health_insurance": [554.53, 554.53],
                    "monthly_net_income": [46695.47, 46695.47],
                    "total_revenue": 3000000,
                    "total_costs": 0,
                    "total_income": 3000000,
                    "total_zus": 50000,
                    "total_tax": 165000,
                    "total_health_insurance": 33271.80,
                    "total_net_income": 2801728.20,
                },
                "best_form": "lump_sum",
                "best_form_description": "Na podstawie obliczeń matematycznych najkorzystniejsza forma to ryczałt (najwyższy dochód netto)",
            }
        }
