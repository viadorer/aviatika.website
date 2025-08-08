// Projektová kalkulačka (celý projekt)
// Výchozí parametry (lze upravit ve formuláři)
const PROJECT_DEFAULT_YEARS = 30;
const PROJECT_DEFAULT_INTEREST_RATE = 4.6; // % p.a.
const PROJECT_DEFAULT_DOWN_PAYMENT_PERCENT = 20; // % vlastních zdrojů
const PROJECT_DEFAULT_UNIT_COUNT = 20; // orientační počet pronajímaných jednotek (lze upravit)
const PROJECT_DEFAULT_OCCUPANCY_DAYS = 182; // ~50% roční obsazenost
const PROJECT_DEFAULT_OPERATING_COSTS_PERCENT = 35; // % provozní náklady z tržeb
const PROJECT_DEFAULT_ANNUAL_APPRECIATION = 5; // % roční zhodnocení

// Pomocná funkce pro formátování měny
function formatCurrency(value) {
    return value.toLocaleString('cs-CZ') + ' Kč';
}

function calculateProjectInvestment(params) {
    const {
        projectPrice,
        capex,
        unitCount,
        adr,
        occupancyDays,
        opexPercent,
        downPaymentPercent,
        interestRate,
        years,
        appreciationPercent
    } = params;

    const totalInvestment = projectPrice + capex;

    // Vlastní zdroje a úvěr
    const downPayment = Math.round(totalInvestment * (downPaymentPercent / 100));
    const mortgageAmount = totalInvestment - downPayment;

    // Měsíční splátka
    const monthlyRate = interestRate / 12 / 100;
    const numberOfPayments = years * 12;
    const monthlyPayment = mortgageAmount > 0 && interestRate > 0
        ? Math.round(
            mortgageAmount *
            (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) /
            (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
          )
        : 0;
    const annualMortgage = monthlyPayment * 12;

    // Jistina (přibližně rovnoměrně)
    const annualPrincipalPayment = years > 0 ? Math.round(mortgageAmount / years) : 0;

    // Příjmy z provozu
    const annualIncome = Math.round(unitCount * adr * occupancyDays);
    const annualOperatingCosts = Math.round(annualIncome * (opexPercent / 100));
    const netAnnualIncome = annualIncome - annualOperatingCosts;

    // Zhodnocení (na celou investici)
    const annualAppreciation = Math.round(totalInvestment * (appreciationPercent / 100));

    // Cash flow
    const annualCashFlow = netAnnualIncome - annualMortgage + annualAppreciation + annualPrincipalPayment;
    const monthlyCashFlow = Math.round(annualCashFlow / 12);

    // ROI na vlastní zdroje (roky)
    const roi = annualCashFlow > 0 ? Math.round((downPayment / annualCashFlow) * 10) / 10 : 99.9;

    return {
        totalInvestment,
        downPayment,
        mortgageAmount,
        monthlyPayment,
        annualMortgage,
        annualIncome,
        annualOperatingCosts,
        netAnnualIncome,
        annualAppreciation,
        annualPrincipalPayment,
        annualCashFlow,
        monthlyCashFlow,
        roi
    };
}

function updateProjectCalculation() {
    console.log('Updating project calculation');

    // Získání hodnot ze vstupních polí
    const projectPrice = parseInt(document.getElementById('project-price').value) || 9900000;
    const capex = parseInt(document.getElementById('project-capex').value) || 0;
    const unitCount = parseInt(document.getElementById('project-unit-count').value) || PROJECT_DEFAULT_UNIT_COUNT;
    const adr = parseInt(document.getElementById('project-adr').value) || 1500;
    const occupancyDays = parseInt(document.getElementById('project-occupancy-days').value) || PROJECT_DEFAULT_OCCUPANCY_DAYS;
    const opexPercent = parseFloat(document.getElementById('project-opex-percent').value) || PROJECT_DEFAULT_OPERATING_COSTS_PERCENT;
    const downPaymentPercent = parseFloat(document.getElementById('project-down-payment-percent').value) || PROJECT_DEFAULT_DOWN_PAYMENT_PERCENT;
    const interestRate = parseFloat(document.getElementById('project-interest-rate').value) || PROJECT_DEFAULT_INTEREST_RATE;
    const years = parseInt(document.getElementById('project-years').value) || PROJECT_DEFAULT_YEARS;
    const appreciationPercent = parseFloat(document.getElementById('project-appreciation-percent').value) || PROJECT_DEFAULT_ANNUAL_APPRECIATION;

    const result = calculateProjectInvestment({
        projectPrice,
        capex,
        unitCount,
        adr,
        occupancyDays,
        opexPercent,
        downPaymentPercent,
        interestRate,
        years,
        appreciationPercent
    });

    console.log('Calculation result:', result);

    // Aktualizace hodnot v HTML
    try {
        // Základní údaje
        document.getElementById('project-total-investment').textContent = formatCurrency(result.totalInvestment);
        document.getElementById('project-down-payment').textContent = formatCurrency(result.downPayment);
        document.getElementById('project-mortgage-amount').textContent = formatCurrency(result.mortgageAmount);
        document.getElementById('project-monthly-payment').textContent = formatCurrency(result.monthlyPayment);

        // Příjmy z provozu
        document.getElementById('project-annual-income').textContent = formatCurrency(result.annualIncome);
        document.getElementById('project-operating-costs').textContent = formatCurrency(result.annualOperatingCosts);
        document.getElementById('project-net-income').textContent = formatCurrency(result.netAnnualIncome);

        // Finanční toky
        document.getElementById('project-annual-mortgage').textContent = formatCurrency(result.annualMortgage);
        document.getElementById('project-annual-appreciation').textContent = document.getElementById('project-appreciation-percent').value + '%';
        document.getElementById('project-annual-appreciation-value').textContent = formatCurrency(result.annualAppreciation);
        document.getElementById('project-annual-principal').textContent = formatCurrency(result.annualPrincipalPayment);
        document.getElementById('project-annual-cash-flow').textContent = formatCurrency(result.annualCashFlow);
        document.getElementById('project-monthly-cash-flow').textContent = formatCurrency(result.monthlyCashFlow);
        document.getElementById('project-roi').textContent = result.roi.toLocaleString() + ' let';
    } catch (error) {
        console.error('Chyba při aktualizaci hodnot v HTML:', error);
    }
}

// Inicializace při načtení stránky
document.addEventListener('DOMContentLoaded', () => {
    console.log('Project calculator loaded');

    // Počáteční kalkulace
    updateProjectCalculation();

    // Přidání event listenerů pro vstupní pole
    const inputs = [
        'project-price',
        'project-capex',
        'project-unit-count',
        'project-adr',
        'project-occupancy-days',
        'project-opex-percent',
        'project-down-payment-percent',
        'project-interest-rate',
        'project-years',
        'project-appreciation-percent'
    ];

    inputs.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener('input', updateProjectCalculation);
    });
});

// Záložní inicializace pro případ, že DOMContentLoaded už proběhl
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document already loaded, initializing project calculator');
    setTimeout(() => {
        updateProjectCalculation();

        const inputs = [
            'project-price',
            'project-capex',
            'project-unit-count',
            'project-adr',
            'project-occupancy-days',
            'project-opex-percent',
            'project-down-payment-percent',
            'project-interest-rate',
            'project-years',
            'project-appreciation-percent'
        ];

        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', updateProjectCalculation);
            }
        });
    }, 100);
}
