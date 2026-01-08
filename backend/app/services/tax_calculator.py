"""
Kalkulator scenariuszy podatkowych - główna logika symulacji.

Moduł składa wyniki z warstwy domain w 60-miesięczne scenariusze.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from dataclasses import dataclass

from app.services.time_utils import generate_months, format_month, group_months_by_year
from app.domain.zus import calculate_zus_monthly
from app.domain.tax_scale import (
    calculate_income_tax_scale,
    calculate_monthly_tax_advance_scale,
)
from app.domain.linear_tax import (
    calculate_income_tax_linear,
    calculate_monthly_tax_advance_linear,
)
from app.domain.lump_sum import (
    calculate_monthly_tax_lump_sum,
    aggregate_revenue_by_rate,
)
from app.domain.health_insurance import (
    calculate_health_insurance_monthly_scale,
    calculate_health_insurance_monthly_linear,
    calculate_health_insurance_monthly_lump_sum,
)


@dataclass
class MonthlyData:
    """
    Dane dla pojedynczego miesiąca.

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


@dataclass
class PeriodSummary:
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


@dataclass
class TaxFormResult:
    """
    Wynik obliczeń dla konkretnej formy opodatkowania.

    Attributes
    ----------
    form_name : str
        Nazwa formy: 'tax_scale', 'linear_tax', 'lump_sum'.
    monthly_data : List[MonthlyData]
        Dane miesięczne.
    monthly_tax : List[Decimal]
        Miesięczny podatek dla każdego miesiąca.
    monthly_health_insurance : List[Decimal]
        Miesięczna składka zdrowotna dla każdego miesiąca.
    monthly_net_income : List[Decimal]
        Miesięczny dochód netto (po wszystkich obciążeniach).
    summary_6_months : PeriodSummary
        Podsumowanie po 6 miesiącach (koniec ulgi ZUS).
    summary_12_months : PeriodSummary
        Podsumowanie po 12 miesiącach (pierwszy rok).
    summary_30_months : PeriodSummary
        Podsumowanie po 30 miesiącach (koniec preferencyjnego ZUS).
    summary_60_months : PeriodSummary
        Podsumowanie po 60 miesiącach (5 lat).
    """

    form_name: str
    monthly_data: List[MonthlyData]
    monthly_tax: List[Decimal]
    monthly_health_insurance: List[Decimal]
    monthly_net_income: List[Decimal]
    summary_6_months: PeriodSummary
    summary_12_months: PeriodSummary
    summary_30_months: PeriodSummary
    summary_60_months: PeriodSummary


@dataclass
class ComparisonResult:
    """
    Porównanie wszystkich form opodatkowania.

    Attributes
    ----------
    tax_scale : TaxFormResult
        Wyniki dla skali podatkowej.
    linear_tax : TaxFormResult
        Wyniki dla podatku liniowego.
    lump_sum : TaxFormResult
        Wyniki dla ryczałtu.
    best_form : str
        Nazwa najkorzystniejszej formy (najwyższy total_net_income).
    """

    tax_scale: TaxFormResult
    linear_tax: TaxFormResult
    lump_sum: TaxFormResult
    best_form: str


class TaxCalculator:
    """
    Kalkulator scenariuszy podatkowych.

    Oblicza 60-miesięczne projekcje dla wszystkich form opodatkowania.
    """

    def __init__(
        self,
        base_month: str,
        business_start_date: date,
        monthly_revenues: List[Decimal],
        monthly_costs: List[Decimal],
        one_time_costs: Optional[Dict[int, Decimal]] = None,
        lump_sum_revenues: Optional[List[Dict[Decimal, Decimal]]] = None,
    ):
        """
        Inicjalizuje kalkulator.

        Parameters
        ----------
        base_month : str
            Miesiąc bazowy w formacie 'YYYY-MM'.
        business_start_date : date
            Data rozpoczęcia działalności gospodarczej.
        monthly_revenues : List[Decimal]
            Lista przychodów miesięcznych (60 wartości dla skali i liniowego).
        monthly_costs : List[Decimal]
            Lista kosztów miesięcznych (60 wartości).
        one_time_costs : Optional[Dict[int, Decimal]], optional
            Koszty jednorazowe: {indeks_miesiąca: kwota}.
        lump_sum_revenues : Optional[List[Dict[Decimal, Decimal]]], optional
            Lista słowników przychodów ryczałtowych: [{stawka: przychód}, ...].
            Musi mieć 60 elementów (po jednym dla każdego miesiąca).
        """
        self.base_month = base_month
        self.business_start_date = business_start_date
        self.monthly_revenues = monthly_revenues
        self.monthly_costs = monthly_costs
        self.one_time_costs = one_time_costs or {}
        self.lump_sum_revenues = lump_sum_revenues or []

        # Generuj 60 miesięcy
        self.months = generate_months(base_month, 60)

    def _calculate_monthly_costs(self, month_index: int) -> Decimal:
        """Oblicza koszty dla danego miesiąca."""
        costs = self.monthly_costs[month_index]

        if month_index in self.one_time_costs:
            costs += self.one_time_costs[month_index]

        return costs

    def _calculate_zus_for_months(self) -> List[Decimal]:
        """Oblicza ZUS dla wszystkich miesięcy."""
        zus_list = []
        for month_date in self.months:
            zus = calculate_zus_monthly(self.business_start_date, month_date)
            zus_list.append(zus)
        return zus_list

    def _calculate_period_summary(
        self,
        label: str,
        months_count: int,
        monthly_data: List[MonthlyData],
        monthly_tax: List[Decimal],
        monthly_health: List[Decimal],
        monthly_net: List[Decimal],
    ) -> PeriodSummary:
        """
        Oblicza podsumowanie za określony okres.

        Parameters
        ----------
        label : str
            Etykieta okresu.
        months_count : int
            Liczba miesięcy do zsumowania.
        monthly_data : List[MonthlyData]
            Dane miesięczne.
        monthly_tax : List[Decimal]
            Miesięczne podatki.
        monthly_health : List[Decimal]
            Miesięczne składki zdrowotne.
        monthly_net : List[Decimal]
            Miesięczne dochody netto.

        Returns
        -------
        PeriodSummary
            Podsumowanie za określony okres.
        """
        period_data = monthly_data[:months_count]
        period_tax = monthly_tax[:months_count]
        period_health = monthly_health[:months_count]
        period_net = monthly_net[:months_count]

        total_zus = sum(d.zus for d in period_data)
        total_tax = sum(period_tax)
        total_health = sum(period_health)
        total_contributions = total_zus + total_health
        total_burden = total_zus + total_health + total_tax

        return PeriodSummary(
            label=label,
            months_count=months_count,
            revenue=sum(d.revenue for d in period_data),
            costs=sum(d.costs for d in period_data),
            income=sum(d.income for d in period_data),
            zus=total_zus,
            tax=total_tax,
            health_insurance=total_health,
            total_contributions=total_contributions,
            total_burden=total_burden,
            net_income=sum(period_net),
        )

    def calculate_tax_scale(self) -> TaxFormResult:
        """
        Oblicza scenariusz dla skali podatkowej.

        Returns
        -------
        TaxFormResult
            Kompletny wynik dla skali podatkowej.
        """
        zus_list = self._calculate_zus_for_months()

        monthly_data_list = []
        monthly_tax_list = []
        monthly_health_list = []
        monthly_net_list = []

        for i, month_date in enumerate(self.months):
            revenue = self.monthly_revenues[i]
            costs = self._calculate_monthly_costs(i)
            income = revenue - costs
            zus = zus_list[i]

            # Podatek miesięczny
            tax = calculate_monthly_tax_advance_scale(income)

            # Składka zdrowotna miesięczna (skala: 9% dochodu, min ~315 PLN)
            health = calculate_health_insurance_monthly_scale(income)

            # Dochód netto
            net_income = income - zus - tax - health

            monthly_data_list.append(
                MonthlyData(
                    month=format_month(month_date),
                    revenue=revenue,
                    costs=costs,
                    income=income,
                    zus=zus,
                )
            )
            monthly_tax_list.append(tax)
            monthly_health_list.append(health)
            monthly_net_list.append(net_income)

        # Podsumowania dla kluczowych okresów
        summary_6m = self._calculate_period_summary(
            "Po 6 miesiącach (koniec ulgi ZUS)",
            6,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_12m = self._calculate_period_summary(
            "Po 12 miesiącach (pierwszy rok)",
            12,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_30m = self._calculate_period_summary(
            "Po 30 miesiącach (koniec preferencyjnego ZUS)",
            30,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_60m = self._calculate_period_summary(
            "Po 60 miesiącach (5 lat)",
            60,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        return TaxFormResult(
            form_name="tax_scale",
            monthly_data=monthly_data_list,
            monthly_tax=monthly_tax_list,
            monthly_health_insurance=monthly_health_list,
            monthly_net_income=monthly_net_list,
            summary_6_months=summary_6m,
            summary_12_months=summary_12m,
            summary_30_months=summary_30m,
            summary_60_months=summary_60m,
        )

    def calculate_linear_tax(self) -> TaxFormResult:
        """
        Oblicza scenariusz dla podatku liniowego.

        Returns
        -------
        TaxFormResult
            Kompletny wynik dla podatku liniowego.
        """
        zus_list = self._calculate_zus_for_months()

        monthly_data_list = []
        monthly_tax_list = []
        monthly_health_list = []
        monthly_net_list = []

        for i, month_date in enumerate(self.months):
            revenue = self.monthly_revenues[i]
            costs = self._calculate_monthly_costs(i)
            income = revenue - costs
            zus = zus_list[i]

            # Podatek miesięczny
            tax = calculate_monthly_tax_advance_linear(income)

            # Składka zdrowotna miesięczna (liniowy: 4.9% dochodu, min ~315 PLN)
            health = calculate_health_insurance_monthly_linear(income)

            # Dochód netto
            net_income = income - zus - tax - health

            monthly_data_list.append(
                MonthlyData(
                    month=format_month(month_date),
                    revenue=revenue,
                    costs=costs,
                    income=income,
                    zus=zus,
                )
            )
            monthly_tax_list.append(tax)
            monthly_health_list.append(health)
            monthly_net_list.append(net_income)

        # Podsumowania dla kluczowych okresów
        summary_6m = self._calculate_period_summary(
            "Po 6 miesiącach (koniec ulgi ZUS)",
            6,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_12m = self._calculate_period_summary(
            "Po 12 miesiącach (pierwszy rok)",
            12,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_30m = self._calculate_period_summary(
            "Po 30 miesiącach (koniec preferencyjnego ZUS)",
            30,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_60m = self._calculate_period_summary(
            "Po 60 miesiącach (5 lat)",
            60,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        return TaxFormResult(
            form_name="linear_tax",
            monthly_data=monthly_data_list,
            monthly_tax=monthly_tax_list,
            monthly_health_insurance=monthly_health_list,
            monthly_net_income=monthly_net_list,
            summary_6_months=summary_6m,
            summary_12_months=summary_12m,
            summary_30_months=summary_30m,
            summary_60_months=summary_60m,
        )

    def calculate_lump_sum(self) -> TaxFormResult:
        """
        Oblicza scenariusz dla ryczałtu.

        Returns
        -------
        TaxFormResult
            Kompletny wynik dla ryczałtu.

        Notes
        -----
        Dla ryczałtu:
        - Koszty obniżają dochód brutto (przychód - koszty = dochód)
        - Podatek płacony bezpośrednio od przychodu (nie od dochodu)
        - Składka zdrowotna stała miesięcznie
        """
        zus_list = self._calculate_zus_for_months()

        monthly_data_list = []
        monthly_tax_list = []
        monthly_health_list = []
        monthly_net_list = []

        for i, month_date in enumerate(self.months):
            # Przychody ryczałtowe dla tego miesiąca
            if i < len(self.lump_sum_revenues):
                revenue_by_rate = self.lump_sum_revenues[i]
            else:
                revenue_by_rate = {}

            total_revenue = sum(revenue_by_rate.values())
            costs = self._calculate_monthly_costs(i)  # Koszty obniżają dochód brutto
            income = total_revenue - costs  # Dochód = przychód - koszty
            zus = zus_list[i]

            # Podatek ryczałtowy (od przychodu, nie od dochodu)
            tax = calculate_monthly_tax_lump_sum(revenue_by_rate)

            # Składka zdrowotna stała dla ryczałtu
            health = calculate_health_insurance_monthly_lump_sum()

            # Dochód netto (koszty już odjęte w income)
            net_income = income - zus - tax - health

            monthly_data_list.append(
                MonthlyData(
                    month=format_month(month_date),
                    revenue=total_revenue,
                    costs=costs,
                    income=income,
                    zus=zus,
                )
            )
            monthly_tax_list.append(tax)
            monthly_health_list.append(health)
            monthly_net_list.append(net_income)

        # Podsumowania dla kluczowych okresów
        summary_6m = self._calculate_period_summary(
            "Po 6 miesiącach (koniec ulgi ZUS)",
            6,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_12m = self._calculate_period_summary(
            "Po 12 miesiącach (pierwszy rok)",
            12,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_30m = self._calculate_period_summary(
            "Po 30 miesiącach (koniec preferencyjnego ZUS)",
            30,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        summary_60m = self._calculate_period_summary(
            "Po 60 miesiącach (5 lat)",
            60,
            monthly_data_list,
            monthly_tax_list,
            monthly_health_list,
            monthly_net_list,
        )

        return TaxFormResult(
            form_name="lump_sum",
            monthly_data=monthly_data_list,
            monthly_tax=monthly_tax_list,
            monthly_health_insurance=monthly_health_list,
            monthly_net_income=monthly_net_list,
            summary_6_months=summary_6m,
            summary_12_months=summary_12m,
            summary_30_months=summary_30m,
            summary_60_months=summary_60m,
        )

    def compare_all_forms(self) -> ComparisonResult:
        """
        Porównuje wszystkie formy opodatkowania.

        Returns
        -------
        ComparisonResult
            Porównanie wszystkich form z wskazaniem najkorzystniejszej.

        Notes
        -----
        Najkorzystniejsza forma to ta z najwyższym total_net_income
        (wyłącznie wynik matematyczny).
        """
        tax_scale = self.calculate_tax_scale()
        linear_tax = self.calculate_linear_tax()
        lump_sum = self.calculate_lump_sum()

        # Określ najkorzystniejszą formę (po 60 miesiącach)
        net_incomes = {
            "tax_scale": tax_scale.summary_60_months.net_income,
            "linear_tax": linear_tax.summary_60_months.net_income,
            "lump_sum": lump_sum.summary_60_months.net_income,
        }

        best_form = max(net_incomes, key=net_incomes.get)

        return ComparisonResult(
            tax_scale=tax_scale,
            linear_tax=linear_tax,
            lump_sum=lump_sum,
            best_form=best_form,
        )
