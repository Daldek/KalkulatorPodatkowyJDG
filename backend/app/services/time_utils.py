"""
Narzędzia do obsługi czasu i miesięcy.

Moduł pomocniczy dla obliczeń miesięcznych i rocznych.
"""

from datetime import date
from dateutil.relativedelta import relativedelta


def generate_months(base_month: str, count: int) -> list[date]:
    """
    Generuje listę kolejnych miesięcy od miesiąca bazowego.

    Parameters
    ----------
    base_month : str
        Miesiąc bazowy w formacie 'YYYY-MM'.
    count : int
        Liczba miesięcy do wygenerowania.

    Returns
    -------
    list[date]
        Lista obiektów date reprezentujących pierwsze dni kolejnych miesięcy.

    Examples
    --------
    >>> generate_months('2025-01', 3)
    [date(2025, 1, 1), date(2025, 2, 1), date(2025, 3, 1)]

    Notes
    -----
    Każdy miesiąc jest reprezentowany przez pierwszy dzień tego miesiąca.
    """
    year, month = map(int, base_month.split("-"))
    start_date = date(year, month, 1)

    months = []
    for i in range(count):
        month_date = start_date + relativedelta(months=i)
        months.append(month_date)

    return months


def format_month(month_date: date) -> str:
    """
    Formatuje datę miesiąca do formatu 'YYYY-MM'.

    Parameters
    ----------
    month_date : date
        Data miesiąca.

    Returns
    -------
    str
        Miesiąc w formacie 'YYYY-MM'.

    Examples
    --------
    >>> format_month(date(2025, 3, 1))
    '2025-03'
    """
    return month_date.strftime("%Y-%m")


def month_to_date(month_str: str) -> date:
    """
    Konwertuje string miesiąca do obiektu date.

    Parameters
    ----------
    month_str : str
        Miesiąc w formacie 'YYYY-MM'.

    Returns
    -------
    date
        Obiekt date reprezentujący pierwszy dzień miesiąca.

    Examples
    --------
    >>> month_to_date('2025-03')
    date(2025, 3, 1)
    """
    year, month = map(int, month_str.split("-"))
    return date(year, month, 1)


def get_year_from_month(month_date: date) -> int:
    """
    Zwraca rok dla danego miesiąca.

    Parameters
    ----------
    month_date : date
        Data miesiąca.

    Returns
    -------
    int
        Rok.
    """
    return month_date.year


def group_months_by_year(months: list[date]) -> dict[int, list[date]]:
    """
    Grupuje miesiące według lat.

    Parameters
    ----------
    months : list[date]
        Lista miesięcy.

    Returns
    -------
    dict[int, list[date]]
        Słownik: {rok: [lista_miesięcy_w_tym_roku]}.

    Notes
    -----
    Funkcja pomocnicza do agregacji rocznej.
    """
    years_dict: dict[int, list[date]] = {}

    for month in months:
        year = month.year
        if year not in years_dict:
            years_dict[year] = []
        years_dict[year].append(month)

    return years_dict
