"""
Endpointy API dla kalkulatora podatkowego.

Warstwa HTTP - walidacja i mapowanie requestów na services.
"""

from fastapi import APIRouter, HTTPException
from decimal import Decimal
from typing import Dict

from app.schemas.requests import CalculationRequest
from app.schemas.responses import (
    ComparisonResultResponse,
    TaxFormResultResponse,
    PeriodSummaryResponse,
)
from app.services.tax_calculator import TaxCalculator, TaxFormResult
from app.core.constants_2025 import LUMP_SUM_RATES


router = APIRouter()


def _convert_lump_sum_revenues(
    lump_sum_revenues_input: list,
) -> list[Dict[Decimal, Decimal]]:
    """
    Konwertuje dane wejściowe ryczałtu na format wewnętrzny.

    Parameters
    ----------
    lump_sum_revenues_input : list
        Lista obiektów LumpSumMonthlyRevenue.

    Returns
    -------
    list[Dict[Decimal, Decimal]]
        Lista słowników {stawka_Decimal: kwota_Decimal} dla 60 miesięcy.
    """
    # Inicjalizuj pustymi słownikami dla 60 miesięcy
    result = [{} for _ in range(60)]

    if not lump_sum_revenues_input:
        return result

    for item in lump_sum_revenues_input:
        month_idx = item.month_index
        revenues_by_rate = {}

        for rate_str, amount in item.revenues_by_rate.items():
            rate_decimal = Decimal(rate_str)
            revenues_by_rate[rate_decimal] = amount

        result[month_idx] = revenues_by_rate

    return result


def _convert_one_time_costs(one_time_costs_input: list) -> Dict[int, Decimal]:
    """
    Konwertuje koszty jednorazowe na słownik.

    Parameters
    ----------
    one_time_costs_input : list
        Lista obiektów OneTimeCost.

    Returns
    -------
    Dict[int, Decimal]
        Słownik {indeks_miesiąca: kwota}.
    """
    if not one_time_costs_input:
        return {}

    result = {}
    for cost in one_time_costs_input:
        if cost.month_index in result:
            # Jeśli jest już koszt dla tego miesiąca, dodaj
            result[cost.month_index] += cost.amount
        else:
            result[cost.month_index] = cost.amount

    return result


def _tax_form_result_to_response(result: TaxFormResult) -> TaxFormResultResponse:
    """
    Konwertuje TaxFormResult na TaxFormResultResponse.

    Parameters
    ----------
    result : TaxFormResult
        Wynik z warstwy services.

    Returns
    -------
    TaxFormResultResponse
        Odpowiedź API.
    """
    months = [data.month for data in result.monthly_data]
    monthly_revenue = [data.revenue for data in result.monthly_data]
    monthly_costs = [data.costs for data in result.monthly_data]
    monthly_income = [data.income for data in result.monthly_data]
    monthly_zus = [data.zus for data in result.monthly_data]

    # Konwersja podsumowań okresowych
    summary_6m_response = PeriodSummaryResponse(
        label=result.summary_6_months.label,
        months_count=result.summary_6_months.months_count,
        revenue=result.summary_6_months.revenue,
        costs=result.summary_6_months.costs,
        income=result.summary_6_months.income,
        zus=result.summary_6_months.zus,
        tax=result.summary_6_months.tax,
        health_insurance=result.summary_6_months.health_insurance,
        total_contributions=result.summary_6_months.total_contributions,
        total_burden=result.summary_6_months.total_burden,
        net_income=result.summary_6_months.net_income,
    )

    summary_12m_response = PeriodSummaryResponse(
        label=result.summary_12_months.label,
        months_count=result.summary_12_months.months_count,
        revenue=result.summary_12_months.revenue,
        costs=result.summary_12_months.costs,
        income=result.summary_12_months.income,
        zus=result.summary_12_months.zus,
        tax=result.summary_12_months.tax,
        health_insurance=result.summary_12_months.health_insurance,
        total_contributions=result.summary_12_months.total_contributions,
        total_burden=result.summary_12_months.total_burden,
        net_income=result.summary_12_months.net_income,
    )

    summary_30m_response = PeriodSummaryResponse(
        label=result.summary_30_months.label,
        months_count=result.summary_30_months.months_count,
        revenue=result.summary_30_months.revenue,
        costs=result.summary_30_months.costs,
        income=result.summary_30_months.income,
        zus=result.summary_30_months.zus,
        tax=result.summary_30_months.tax,
        health_insurance=result.summary_30_months.health_insurance,
        total_contributions=result.summary_30_months.total_contributions,
        total_burden=result.summary_30_months.total_burden,
        net_income=result.summary_30_months.net_income,
    )

    summary_60m_response = PeriodSummaryResponse(
        label=result.summary_60_months.label,
        months_count=result.summary_60_months.months_count,
        revenue=result.summary_60_months.revenue,
        costs=result.summary_60_months.costs,
        income=result.summary_60_months.income,
        zus=result.summary_60_months.zus,
        tax=result.summary_60_months.tax,
        health_insurance=result.summary_60_months.health_insurance,
        total_contributions=result.summary_60_months.total_contributions,
        total_burden=result.summary_60_months.total_burden,
        net_income=result.summary_60_months.net_income,
    )

    return TaxFormResultResponse(
        form_name=result.form_name,
        months=months,
        monthly_revenue=monthly_revenue,
        monthly_costs=monthly_costs,
        monthly_income=monthly_income,
        monthly_zus=monthly_zus,
        monthly_tax=result.monthly_tax,
        monthly_health_insurance=result.monthly_health_insurance,
        monthly_net_income=result.monthly_net_income,
        summary_6_months=summary_6m_response,
        summary_12_months=summary_12m_response,
        summary_30_months=summary_30m_response,
        summary_60_months=summary_60m_response,
    )


@router.post("/calculate", response_model=ComparisonResultResponse)
async def calculate_taxes(request: CalculationRequest) -> ComparisonResultResponse:
    """
    Oblicza porównanie form opodatkowania dla JDG.

    Endpoint główny - przyjmuje dane użytkownika i zwraca 60-miesięczną projekcję
    dla wszystkich form opodatkowania (skala, liniowy, ryczałt).

    Parameters
    ----------
    request : CalculationRequest
        Dane wejściowe użytkownika.

    Returns
    -------
    ComparisonResultResponse
        Porównanie wszystkich form opodatkowania z danymi miesięcznymi i sumami.

    Raises
    ------
    HTTPException
        Jeśli wystąpił błąd podczas obliczeń.

    Notes
    -----
    - Aplikacja ma charakter informacyjny i symulacyjny
    - Nie stanowi doradztwa podatkowego
    - Wyniki oparte wyłącznie na obliczeniach matematycznych
    """
    try:
        # Konwersja danych wejściowych
        lump_sum_revenues = _convert_lump_sum_revenues(
            request.lump_sum_revenues or []
        )
        one_time_costs = _convert_one_time_costs(request.one_time_costs or [])

        # Inicjalizacja kalkulatora
        calculator = TaxCalculator(
            base_month=request.base_month,
            business_start_date=request.business_start_date,
            monthly_revenues=request.monthly_revenues,
            monthly_costs=request.monthly_costs,
            one_time_costs=one_time_costs,
            lump_sum_revenues=lump_sum_revenues,
        )

        # Obliczenia
        comparison = calculator.compare_all_forms()

        # Konwersja na response
        tax_scale_response = _tax_form_result_to_response(comparison.tax_scale)
        linear_tax_response = _tax_form_result_to_response(comparison.linear_tax)
        lump_sum_response = _tax_form_result_to_response(comparison.lump_sum)

        # Opis najkorzystniejszej formy (bez "powinieneś", "musisz")
        form_names = {
            "tax_scale": "skala podatkowa",
            "linear_tax": "podatek liniowy",
            "lump_sum": "ryczałt",
        }
        best_form_name = form_names.get(comparison.best_form, comparison.best_form)
        best_net_income = comparison.__dict__[comparison.best_form].summary_60_months.net_income
        description = (
            f"Na podstawie obliczeń matematycznych najkorzystniejsza forma to "
            f"{best_form_name} (najwyższy dochód netto: "
            f"{best_net_income:.2f} PLN)"
        )

        return ComparisonResultResponse(
            tax_scale=tax_scale_response,
            linear_tax=linear_tax_response,
            lump_sum=lump_sum_response,
            best_form=comparison.best_form,
            best_form_description=description,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas obliczeń: {str(e)}")


@router.get("/tax-rates")
async def get_tax_rates():
    """
    Zwraca dostępne stawki ryczałtu.

    Returns
    -------
    dict
        Słownik stawek ryczałtu i ich opisów.

    Notes
    -----
    Endpoint pomocniczy do wyświetlenia użytkownikowi dostępnych stawek.
    """
    # Konwersja Decimal na string dla JSON
    rates_dict = {str(rate): description for rate, description in LUMP_SUM_RATES.items()}
    return {
        "tax_year": 2025,
        "rates": rates_dict,
        "note": "Wybór stawki zależy od rodzaju działalności. Aplikacja nie kwalifikuje przychodów automatycznie.",
    }
