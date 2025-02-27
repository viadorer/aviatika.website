// Konstantní parametry pro hlavní investiční kalkulačku
const MAIN_MORTGAGE_YEARS = 30;
const MAIN_INTEREST_RATE = 4.6;
const MAIN_DOWN_PAYMENT_PERCENT = 20;
const MAIN_OCCUPANCY_DAYS = 182; // 50% roční obsazenost
const MAIN_OPERATING_COSTS_PERCENT = 35; // 35% provozní náklady
const MAIN_ANNUAL_APPRECIATION = 3.5; // 3.5% roční zhodnocení nemovitosti

// Funkce pro formátování čísla jako měny
function formatCurrency(value) {
    return value.toLocaleString('cs-CZ') + ' Kč';
}

function calculateMainInvestment(apartmentPrice, pricePerNight) {
    console.log(`Calculating main investment: price=${apartmentPrice}, pricePerNight=${pricePerNight}`);
    
    // Vlastní zdroje a hypotéka
    const downPayment = Math.round(apartmentPrice * (MAIN_DOWN_PAYMENT_PERCENT / 100));
    const mortgageAmount = apartmentPrice - downPayment;
    
    // Výpočet měsíční splátky
    const monthlyRate = MAIN_INTEREST_RATE / 12 / 100;
    const numberOfPayments = MAIN_MORTGAGE_YEARS * 12;
    const monthlyPayment = Math.round(
        mortgageAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / 
        (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
    );
    const annualMortgage = monthlyPayment * 12;

    // Výpočet jistiny hypotéky
    const annualPrincipalPayment = Math.round(mortgageAmount / MAIN_MORTGAGE_YEARS);

    // Výpočet příjmů
    const annualIncome = pricePerNight * MAIN_OCCUPANCY_DAYS;
    const monthlyIncome = Math.round(annualIncome / 12);
    
    // Výpočet nákladů a cash flow
    const annualOperatingCosts = Math.round(annualIncome * (MAIN_OPERATING_COSTS_PERCENT / 100));
    const monthlyOperatingCosts = Math.round(annualOperatingCosts / 12);
    const netAnnualIncome = annualIncome - annualOperatingCosts;
    const annualAppreciation = Math.round(apartmentPrice * (MAIN_ANNUAL_APPRECIATION / 100));
    const annualCashFlow = netAnnualIncome - annualMortgage + annualAppreciation + annualPrincipalPayment;
    const monthlyCashFlow = Math.round(annualCashFlow / 12);

    // Výpočet návratnosti investice
    const roi = annualCashFlow > 0 ? Math.round(downPayment / annualCashFlow * 10) / 10 : 99.9;

    console.log('Main calculation result:', {
        apartmentPrice,
        downPayment,
        mortgageAmount,
        monthlyPayment,
        annualMortgage,
        pricePerNight,
        annualIncome,
        annualOperatingCosts,
        netAnnualIncome,
        annualAppreciation,
        annualPrincipalPayment,
        annualCashFlow,
        monthlyCashFlow,
        roi
    });

    return {
        apartmentPrice,
        downPayment,
        mortgageAmount,
        monthlyPayment,
        annualMortgage,
        pricePerNight,
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

function updateMainCalculation() {
    console.log('Updating main calculation');
    
    // Získání hodnot ze vstupních polí
    const apartmentPrice = parseInt(document.getElementById('main-apartment-price')?.value) || 3200000;
    const pricePerNight = parseInt(document.getElementById('main-price-per-night')?.value) || 1500;
    
    console.log(`Input values: apartmentPrice=${apartmentPrice}, pricePerNight=${pricePerNight}`);
    
    const result = calculateMainInvestment(apartmentPrice, pricePerNight);
    
    console.log('Calculation result:', result);
    
    // Aktualizace hodnot v HTML - upraveno pro hlavní kalkulačku
    document.getElementById('main-price-value').textContent = formatCurrency(result.apartmentPrice);
    document.getElementById('main-down-payment-value').textContent = formatCurrency(result.downPayment);
    document.getElementById('main-monthly-payment-value').textContent = formatCurrency(result.monthlyPayment);
    document.getElementById('main-annual-appreciation-value').textContent = MAIN_ANNUAL_APPRECIATION + '%';
    document.getElementById('main-annual-income-value').textContent = formatCurrency(result.annualIncome);
    document.getElementById('main-cash-flow-value').textContent = formatCurrency(result.monthlyCashFlow);
    document.getElementById('main-annual-mortgage-repayment-value').textContent = formatCurrency(result.annualPrincipalPayment);
}

// Přidáme globální funkci pro ruční spuštění výpočtu
window.recalculateMainInvestment = function() {
    console.log('Manual recalculation triggered');
    updateMainCalculation();
};

// Inicializace při načtení stránky
document.addEventListener('DOMContentLoaded', () => {
    console.log('Main calculator loaded');
    
    // Inicializace výpočtu
    updateMainCalculation();
    
    // Přidání event listenerů pro vstupy
    const apartmentPriceInput = document.getElementById('main-apartment-price');
    const pricePerNightInput = document.getElementById('main-price-per-night');
    
    if (apartmentPriceInput) {
        apartmentPriceInput.addEventListener('input', () => {
            console.log(`Apartment price changed: ${apartmentPriceInput.value}`);
            updateMainCalculation();
        });
    }
    
    if (pricePerNightInput) {
        pricePerNightInput.addEventListener('input', () => {
            console.log(`Price per night changed: ${pricePerNightInput.value}`);
            updateMainCalculation();
        });
    }
});

// Záložní inicializace pro případ, že DOMContentLoaded už proběhl
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document already loaded, initializing main calculator');
    setTimeout(() => {
        // Inicializace výpočtu
        updateMainCalculation();
        
        // Přidání event listenerů pro vstupy
        const apartmentPriceInput = document.getElementById('main-apartment-price');
        const pricePerNightInput = document.getElementById('main-price-per-night');
        
        if (apartmentPriceInput) {
            apartmentPriceInput.addEventListener('input', () => {
                console.log(`Apartment price changed: ${apartmentPriceInput.value}`);
                updateMainCalculation();
            });
        }
        
        if (pricePerNightInput) {
            pricePerNightInput.addEventListener('input', () => {
                console.log(`Price per night changed: ${pricePerNightInput.value}`);
                updateMainCalculation();
            });
        }
    }, 500);
}

// Spustíme výpočet i po načtení okna
window.addEventListener('load', () => {
    console.log('Window loaded, running main calculator');
    setTimeout(updateMainCalculation, 100);
});
