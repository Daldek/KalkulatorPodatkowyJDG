/**
 * Kalkulator Podatkowy JDG - Frontend
 *
 * Vanilla JavaScript - bez frameworków
 * Frontend tylko renderuje dane z API, nie wykonuje obliczeń
 */

// Konfiguracja
const API_BASE_URL = 'http://localhost:8000';

// Globalne zmienne
let structureChart = null;
let monthlyChart = null;
let cumulativeChart = null;

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

    // Wykres struktury pierwszego miesiąca
    renderStructureChart(data);

    // Wykresy liniowe (miesięczny i skumulowany)
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
 * Renderuje wykres słupkowy struktury pierwszego miesiąca
 */
function renderStructureChart(data) {
    const ctx = document.getElementById('structureChart').getContext('2d');

    // Zniszcz poprzedni wykres jeśli istnieje
    if (structureChart) {
        structureChart.destroy();
    }

    // Pobierz dane z pierwszego miesiąca (indeks 0)
    const scale = {
        costs: parseFloat(data.tax_scale.monthly_costs[0]),
        tax: parseFloat(data.tax_scale.monthly_tax[0]),
        contributions: parseFloat(data.tax_scale.monthly_zus[0]) + parseFloat(data.tax_scale.monthly_health_insurance[0]),
        netIncome: parseFloat(data.tax_scale.monthly_net_income[0]),
    };

    const linear = {
        costs: parseFloat(data.linear_tax.monthly_costs[0]),
        tax: parseFloat(data.linear_tax.monthly_tax[0]),
        contributions: parseFloat(data.linear_tax.monthly_zus[0]) + parseFloat(data.linear_tax.monthly_health_insurance[0]),
        netIncome: parseFloat(data.linear_tax.monthly_net_income[0]),
    };

    const lumpSum = {
        costs: parseFloat(data.lump_sum.monthly_costs[0]),
        tax: parseFloat(data.lump_sum.monthly_tax[0]),
        contributions: parseFloat(data.lump_sum.monthly_zus[0]) + parseFloat(data.lump_sum.monthly_health_insurance[0]),
        netIncome: parseFloat(data.lump_sum.monthly_net_income[0]),
    };

    // Labels to kategorie (koszty, podatek, składki, dochód netto)
    const labels = ['Koszty uzyskania przychodu', 'Podatek', 'Składki (ZUS + zdrowotna)', 'Dochód netto'];

    // Datasets to formy opodatkowania (skala, liniowy, ryczałt)
    structureChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Skala podatkowa',
                    data: [scale.costs, scale.tax, scale.contributions, scale.netIncome],
                    backgroundColor: '#3b82f6',
                    borderColor: '#2563eb',
                    borderWidth: 1,
                },
                {
                    label: 'Podatek liniowy',
                    data: [linear.costs, linear.tax, linear.contributions, linear.netIncome],
                    backgroundColor: '#8b5cf6',
                    borderColor: '#7c3aed',
                    borderWidth: 1,
                },
                {
                    label: 'Ryczałt',
                    data: [lumpSum.costs, lumpSum.tax, lumpSum.contributions, lumpSum.netIncome],
                    backgroundColor: '#10b981',
                    borderColor: '#059669',
                    borderWidth: 1,
                },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Struktura kosztów i dochodów - pierwszy miesiąc działalności',
                    font: {
                        size: 16,
                    },
                },
                subtitle: {
                    display: true,
                    text: 'Uwaga: W ryczałcie koszty nie wpływają na wysokość podatku',
                    font: {
                        size: 12,
                        style: 'italic',
                    },
                    color: '#64748b',
                    padding: {
                        bottom: 10,
                    },
                },
                legend: {
                    display: true,
                    position: 'top',
                },
                tooltip: {
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
                        text: 'Kategoria',
                    },
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Kwota (PLN)',
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
 * Renderuje wykresy porównawcze (miesięczny i skumulowany)
 */
function renderChart(data) {
    const labels = data.tax_scale.months;

    // Wspólne definicje kolorów
    const colors = {
        scale: { border: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)' },
        linear: { border: '#8b5cf6', bg: 'rgba(139, 92, 246, 0.1)' },
        lumpSum: { border: '#10b981', bg: 'rgba(16, 185, 129, 0.1)' },
    };

    // Wspólne opcje wykresów
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
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
                ticks: {
                    callback: function (value) {
                        return formatCurrency(value);
                    },
                },
            },
        },
    };

    // Wykres 1: Miesięczny dochód netto
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    if (monthlyChart) {
        monthlyChart.destroy();
    }

    monthlyChart = new Chart(monthlyCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Skala podatkowa',
                    data: data.tax_scale.monthly_net_income,
                    borderColor: colors.scale.border,
                    backgroundColor: colors.scale.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
                {
                    label: 'Podatek liniowy',
                    data: data.linear_tax.monthly_net_income,
                    borderColor: colors.linear.border,
                    backgroundColor: colors.linear.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
                {
                    label: 'Ryczałt',
                    data: data.lump_sum.monthly_net_income,
                    borderColor: colors.lumpSum.border,
                    backgroundColor: colors.lumpSum.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
            ],
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    display: true,
                    text: 'Miesięczny dochód netto (PLN)',
                    font: {
                        size: 16,
                    },
                },
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Dochód netto (PLN)',
                    },
                },
            },
        },
    });

    // Wykres 2: Skumulowany dochód netto
    const cumulativeCtx = document.getElementById('cumulativeChart').getContext('2d');
    if (cumulativeChart) {
        cumulativeChart.destroy();
    }

    cumulativeChart = new Chart(cumulativeCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Skala podatkowa',
                    data: calculateCumulative(data.tax_scale.monthly_net_income),
                    borderColor: colors.scale.border,
                    backgroundColor: colors.scale.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
                {
                    label: 'Podatek liniowy',
                    data: calculateCumulative(data.linear_tax.monthly_net_income),
                    borderColor: colors.linear.border,
                    backgroundColor: colors.linear.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
                {
                    label: 'Ryczałt',
                    data: calculateCumulative(data.lump_sum.monthly_net_income),
                    borderColor: colors.lumpSum.border,
                    backgroundColor: colors.lumpSum.bg,
                    borderWidth: 2,
                    tension: 0.1,
                },
            ],
        },
        options: {
            ...commonOptions,
            plugins: {
                ...commonOptions.plugins,
                title: {
                    display: true,
                    text: 'Skumulowany dochód netto (PLN)',
                    font: {
                        size: 16,
                    },
                },
            },
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Skumulowany dochód netto (PLN)',
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

    const forms = [
        { name: 'Skala podatkowa', key: 'tax_scale', data: data.tax_scale },
        { name: 'Podatek liniowy', key: 'linear_tax', data: data.linear_tax },
        { name: 'Ryczałt', key: 'lump_sum', data: data.lump_sum },
    ];

    let html = '<div class="monthly-tables">';

    forms.forEach(form => {
        html += `
            <div class="monthly-table-section">
                <h4>${form.name}</h4>
                <table class="monthly-table">
                    <thead>
                        <tr>
                            <th>Miesiąc</th>
                            <th>Przychód</th>
                            <th>Koszty</th>
                            <th>Dochód</th>
                            <th>ZUS</th>
                            <th>Podatek</th>
                            <th>Składka zdrowotna</th>
                            <th>Dochód netto</th>
                        </tr>
                    </thead>
                    <tbody>
        `;

        for (let i = 0; i < form.data.months.length; i++) {
            html += `
                <tr>
                    <td>${form.data.months[i]}</td>
                    <td>${formatCurrency(form.data.monthly_revenue[i])}</td>
                    <td>${formatCurrency(form.data.monthly_costs[i])}</td>
                    <td>${formatCurrency(form.data.monthly_income[i])}</td>
                    <td>${formatCurrency(form.data.monthly_zus[i])}</td>
                    <td>${formatCurrency(form.data.monthly_tax[i])}</td>
                    <td>${formatCurrency(form.data.monthly_health_insurance[i])}</td>
                    <td><strong>${formatCurrency(form.data.monthly_net_income[i])}</strong></td>
                </tr>
            `;
        }

        html += `
                    </tbody>
                </table>
            </div>
        `;
    });

    html += '</div>';

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
