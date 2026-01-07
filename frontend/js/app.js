/**
 * Kalkulator Podatkowy JDG - Frontend
 *
 * Vanilla JavaScript - bez frameworków
 * Frontend tylko renderuje dane z API, nie wykonuje obliczeń
 */

// Konfiguracja
const API_BASE_URL = 'http://localhost:8000';

// Globalne zmienne
let chart = null;

// Inicjalizacja aplikacji
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('taxForm');
    form.addEventListener('submit', handleFormSubmit);
});

/**
 * Obsługa wysłania formularza
 */
async function handleFormSubmit(event) {
    event.preventDefault();

    // Ukryj poprzednie wyniki i błędy
    hideElement('resultsSection');
    hideElement('errorMessage');
    showElement('loadingSpinner');

    try {
        // Pobierz dane z formularza
        const formData = collectFormData();

        // Przygotuj request
        const requestData = prepareRequestData(formData);

        // Wyślij request do API
        const response = await fetch(`${API_BASE_URL}/api/calculate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Błąd podczas obliczeń');
        }

        const data = await response.json();

        // Renderuj wyniki
        renderResults(data);

        // Pokaż sekcję wyników
        hideElement('loadingSpinner');
        showElement('resultsSection');

        // Scroll do wyników
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error('Error:', error);
        hideElement('loadingSpinner');
        showError(error.message);
    }
}

/**
 * Normalizuje separator dziesiętny (przecinek → kropka)
 */
function normalizeDecimal(value) {
    if (typeof value === 'string') {
        return value.replace(',', '.');
    }
    return value;
}

/**
 * Zbiera dane z formularza
 */
function collectFormData() {
    // Pobierz i znormalizuj wartości
    const monthlyRevenueRaw = normalizeDecimal(document.getElementById('monthlyRevenue').value);
    const monthlyCostsRaw = normalizeDecimal(document.getElementById('monthlyCosts').value);
    const lumpSumRateRaw = normalizeDecimal(document.getElementById('lumpSumRate').value);

    // Konwersja stawki ryczałtu z % na ułamek dziesiętny
    // Użytkownik wpisuje np. "5,5" lub "5.5" (procent)
    // Konwertujemy na 0.055 (ułamek)
    const lumpSumRatePercent = parseFloat(lumpSumRateRaw);
    const lumpSumRate = lumpSumRatePercent / 100;

    return {
        startDate: document.getElementById('startDate').value,
        monthlyRevenue: parseFloat(monthlyRevenueRaw),
        monthlyCosts: parseFloat(monthlyCostsRaw),
        lumpSumRate: lumpSumRate,
    };
}

/**
 * Przygotowuje dane do wysłania do API
 */
function prepareRequestData(formData) {
    // Miesiąc bazowy = miesiąc rozpoczęcia działalności (YYYY-MM)
    const startDate = new Date(formData.startDate);
    const baseMonth = `${startDate.getFullYear()}-${String(startDate.getMonth() + 1).padStart(2, '0')}`;

    // Utwórz 60 miesięcy z powtórzoną kwotą przychodu
    const monthlyRevenues = Array(60).fill(formData.monthlyRevenue);

    // Przygotuj przychody ryczałtowe
    const lumpSumRevenues = [];
    for (let i = 0; i < 60; i++) {
        lumpSumRevenues.push({
            month_index: i,
            revenues_by_rate: {
                [formData.lumpSumRate.toString()]: formData.monthlyRevenue,
            },
        });
    }

    return {
        base_month: baseMonth,
        business_start_date: formData.startDate,
        monthly_revenues: monthlyRevenues,
        monthly_costs_fixed: formData.monthlyCosts,
        one_time_costs: [],
        lump_sum_revenues: lumpSumRevenues,
    };
}

/**
 * Renderuje wszystkie wyniki
 */
function renderResults(data) {
    // Najkorzystniejsza forma
    renderBestForm(data);

    // Wykres
    renderChart(data);

    // 4 tabele podsumowań
    renderPeriodSummaryTable(data, 'summary_6_months', 'summary6mTableBody');
    renderPeriodSummaryTable(data, 'summary_12_months', 'summary12mTableBody');
    renderPeriodSummaryTable(data, 'summary_30_months', 'summary30mTableBody');
    renderPeriodSummaryTable(data, 'summary_60_months', 'summary60mTableBody');

    // Szczegóły miesięczne (opcjonalnie)
    renderMonthlyDetails(data);
}

/**
 * Wyświetla informację o najkorzystniejszej formie
 */
function renderBestForm(data) {
    const bestFormDiv = document.getElementById('bestFormInfo');
    bestFormDiv.innerHTML = `
        <strong>Wynik porównania:</strong> ${data.best_form_description}
    `;
}

/**
 * Oblicza skumulowane wartości z tablicy
 */
function calculateCumulative(values) {
    const cumulative = [];
    let sum = 0;
    for (const value of values) {
        sum += parseFloat(value);
        cumulative.push(sum);
    }
    return cumulative;
}

/**
 * Renderuje wykres porównawczy
 */
function renderChart(data) {
    const ctx = document.getElementById('comparisonChart').getContext('2d');

    // Zniszcz poprzedni wykres jeśli istnieje
    if (chart) {
        chart.destroy();
    }

    // Przygotuj dane - oblicz skumulowany dochód netto
    const labels = data.tax_scale.months;
    const datasets = [
        {
            label: 'Skala podatkowa',
            data: calculateCumulative(data.tax_scale.monthly_net_income),
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.1,
        },
        {
            label: 'Podatek liniowy',
            data: calculateCumulative(data.linear_tax.monthly_net_income),
            borderColor: '#8b5cf6',
            backgroundColor: 'rgba(139, 92, 246, 0.1)',
            borderWidth: 2,
            tension: 0.1,
        },
        {
            label: 'Ryczałt',
            data: calculateCumulative(data.lump_sum.monthly_net_income),
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 2,
            tension: 0.1,
        },
    ];

    // Utwórz wykres
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Skumulowany dochód netto (PLN)',
                    font: {
                        size: 16,
                    },
                },
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += formatCurrency(context.parsed.y);
                            return label;
                        },
                    },
                },
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Miesiąc',
                    },
                    ticks: {
                        maxTicksLimit: 12,
                    },
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Skumulowany dochód netto (PLN)',
                    },
                    ticks: {
                        callback: function (value) {
                            return formatCurrency(value);
                        },
                    },
                },
            },
        },
    });
}

/**
 * Renderuje tabelę podsumowania dla określonego okresu
 */
function renderPeriodSummaryTable(data, summaryKey, tbodyId) {
    const tbody = document.getElementById(tbodyId);
    tbody.innerHTML = '';

    const forms = [
        { name: 'Skala podatkowa', data: data.tax_scale[summaryKey] },
        { name: 'Podatek liniowy', data: data.linear_tax[summaryKey] },
        { name: 'Ryczałt', data: data.lump_sum[summaryKey] },
    ];

    // Znajdź najkorzystniejszą formę dla tego okresu
    let bestNetIncome = forms[0].data.net_income;
    let bestIndex = 0;
    forms.forEach((form, index) => {
        if (form.data.net_income > bestNetIncome) {
            bestNetIncome = form.data.net_income;
            bestIndex = index;
        }
    });

    forms.forEach((form, index) => {
        const row = document.createElement('tr');

        // Wyróżnij najkorzystniejszą formę dla tego okresu
        if (index === bestIndex) {
            row.style.backgroundColor = '#d1fae5';
            row.style.fontWeight = '600';
        }

        row.innerHTML = `
            <td>${form.name}</td>
            <td>${formatCurrency(form.data.revenue)}</td>
            <td>${formatCurrency(form.data.costs)}</td>
            <td>${formatCurrency(form.data.income)}</td>
            <td>${formatCurrency(form.data.zus)}</td>
            <td>${formatCurrency(form.data.tax)}</td>
            <td>${formatCurrency(form.data.health_insurance)}</td>
            <td>${formatCurrency(form.data.total_contributions)}</td>
            <td>${formatCurrency(form.data.total_burden)}</td>
            <td><strong>${formatCurrency(form.data.net_income)}</strong></td>
        `;

        tbody.appendChild(row);
    });
}

/**
 * Renderuje szczegóły miesięczne (uproszczone)
 */
function renderMonthlyDetails(data) {
    const monthlyDiv = document.getElementById('monthlyData');

    let html = '<p>Dane miesięczne zawierają 60 punktów danych dla każdej formy opodatkowania.</p>';
    html += '<p>Wykresy i tabele powyżej pokazują kompletne porównanie.</p>';

    monthlyDiv.innerHTML = html;
}

/**
 * Formatuje wartość jako walutę PLN
 */
function formatCurrency(value) {
    if (value === null || value === undefined) {
        return '-';
    }
    return new Intl.NumberFormat('pl-PL', {
        style: 'currency',
        currency: 'PLN',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value);
}

/**
 * Pokazuje element
 */
function showElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'block';
    }
}

/**
 * Ukrywa element
 */
function hideElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = 'none';
    }
}

/**
 * Pokazuje błąd
 */
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.textContent = `Błąd: ${message}`;
    errorDiv.style.display = 'block';

    // Scroll do błędu
    errorDiv.scrollIntoView({ behavior: 'smooth' });
}
