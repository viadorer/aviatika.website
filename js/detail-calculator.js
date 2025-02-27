// Konstantní parametry
const DETAIL_MORTGAGE_YEARS = 30;
const DETAIL_INTEREST_RATE = 4.6;
const DETAIL_DOWN_PAYMENT_PERCENT = 20;
const DETAIL_OCCUPANCY_DAYS = 182; // 50% roční obsazenost
const DETAIL_OPERATING_COSTS_PERCENT = 35; // 35% provozní náklady
const DETAIL_ANNUAL_APPRECIATION = 5; // 5% roční zhodnocení nemovitosti

// Pomocná funkce pro formátování měny
function formatCurrency(value) {
    return value.toLocaleString('cs-CZ') + ' Kč';
}

function calculateDetailedInvestment(apartmentPrice, pricePerNight) {
    // Vlastní zdroje a hypotéka
    const downPayment = Math.round(apartmentPrice * (DETAIL_DOWN_PAYMENT_PERCENT / 100));
    const mortgageAmount = apartmentPrice - downPayment;
    
    // Výpočet měsíční splátky
    const monthlyRate = DETAIL_INTEREST_RATE / 12 / 100;
    const numberOfPayments = DETAIL_MORTGAGE_YEARS * 12;
    const monthlyPayment = Math.round(
        mortgageAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / 
        (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
    );
    const annualMortgage = monthlyPayment * 12;

    // Výpočet jistiny hypotéky
    const annualPrincipalPayment = Math.round(mortgageAmount / DETAIL_MORTGAGE_YEARS);

    // Výpočet příjmů
    const annualIncome = pricePerNight * DETAIL_OCCUPANCY_DAYS;
    const monthlyIncome = Math.round(annualIncome / 12);
    
    // Výpočet nákladů a cash flow
    const annualOperatingCosts = Math.round(annualIncome * (DETAIL_OPERATING_COSTS_PERCENT / 100));
    const monthlyOperatingCosts = Math.round(annualOperatingCosts / 12);
    const netAnnualIncome = annualIncome - annualOperatingCosts;
    const annualAppreciation = Math.round(apartmentPrice * (DETAIL_ANNUAL_APPRECIATION / 100));
    const annualCashFlow = netAnnualIncome - annualMortgage + annualAppreciation + annualPrincipalPayment;
    const monthlyCashFlow = Math.round(annualCashFlow / 12);

    // Výpočet návratnosti investice
    const roi = annualCashFlow > 0 ? Math.round(downPayment / annualCashFlow * 10) / 10 : 99.9;

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

function updateDetailedCalculation() {
    console.log('Updating detailed calculation');
    
    // Získání hodnot ze vstupních polí
    const apartmentPrice = parseInt(document.getElementById('detail-apartment-price').value) || 3200000;
    const pricePerNight = parseInt(document.getElementById('detail-price-per-night-input').value) || 1500;
    
    // Získání hodnoty ročního zhodnocení z inputu
    const annualAppreciationInput = document.getElementById('detail-annual-appreciation-input');
    let annualAppreciationRate = DETAIL_ANNUAL_APPRECIATION;
    
    if (annualAppreciationInput) {
        annualAppreciationRate = parseFloat(annualAppreciationInput.value) || DETAIL_ANNUAL_APPRECIATION;
        console.log(`Použité roční zhodnocení: ${annualAppreciationRate}%`);
    }
    
    console.log(`Input values: apartmentPrice=${apartmentPrice}, pricePerNight=${pricePerNight}, annualAppreciation=${annualAppreciationRate}%`);
    
    // Výpočet investice
    const result = calculateDetailedInvestment(apartmentPrice, pricePerNight);
    
    // Přepsání hodnoty zhodnocení nemovitosti podle vstupu
    result.annualAppreciation = Math.round(apartmentPrice * (annualAppreciationRate / 100));
    
    // Přepočet cash flow s novým zhodnocením
    result.annualCashFlow = result.netAnnualIncome - result.annualMortgage + result.annualAppreciation + result.annualPrincipalPayment;
    result.monthlyCashFlow = Math.round(result.annualCashFlow / 12);
    result.roi = result.annualCashFlow > 0 ? Math.round(result.downPayment / result.annualCashFlow * 10) / 10 : 99.9;
    
    console.log('Calculation result:', result);
    
    // Aktualizace hodnot v HTML
    try {
        // Základní údaje
        document.getElementById('detail-price-value').textContent = formatCurrency(result.apartmentPrice);
        document.getElementById('detail-down-payment').textContent = formatCurrency(result.downPayment);
        document.getElementById('detail-mortgage-amount').textContent = formatCurrency(result.mortgageAmount);
        document.getElementById('detail-monthly-payment').textContent = formatCurrency(result.monthlyPayment);
        
        // Příjmy z pronájmu
        document.getElementById('detail-price-per-night').textContent = formatCurrency(result.pricePerNight);
        document.getElementById('detail-annual-income').textContent = formatCurrency(result.annualIncome);
        document.getElementById('detail-operating-costs').textContent = formatCurrency(result.annualOperatingCosts);
        document.getElementById('detail-net-income').textContent = formatCurrency(result.netAnnualIncome);
        
        // Finanční toky
        document.getElementById('detail-annual-mortgage').textContent = formatCurrency(result.annualMortgage);
        document.getElementById('detail-annual-appreciation').textContent = annualAppreciationRate + '%';
        document.getElementById('detail-annual-appreciation-value').textContent = formatCurrency(result.annualAppreciation);
        document.getElementById('detail-annual-mortgage-repayment').textContent = formatCurrency(result.annualPrincipalPayment);
        document.getElementById('detail-annual-cash-flow').textContent = formatCurrency(result.annualCashFlow);
        document.getElementById('detail-monthly-cash-flow').textContent = formatCurrency(result.monthlyCashFlow);
        document.getElementById('detail-roi').textContent = result.roi.toLocaleString() + ' let';
    } catch (error) {
        console.error('Chyba při aktualizaci hodnot v HTML:', error);
    }
}

// Inicializace při načtení stránky
document.addEventListener('DOMContentLoaded', () => {
    console.log('Detail calculator loaded');
    
    // Počáteční kalkulace
    updateDetailedCalculation();
    
    // Přidání event listenerů pro vstupní pole
    const detailApartmentPriceInput = document.getElementById('detail-apartment-price');
    const detailPricePerNightInput = document.getElementById('detail-price-per-night-input');
    const detailAnnualAppreciationInput = document.getElementById('detail-annual-appreciation-input');
    
    if (detailApartmentPriceInput) {
        detailApartmentPriceInput.addEventListener('input', updateDetailedCalculation);
    }
    
    if (detailPricePerNightInput) {
        detailPricePerNightInput.addEventListener('input', updateDetailedCalculation);
    }
    
    if (detailAnnualAppreciationInput) {
        detailAnnualAppreciationInput.addEventListener('input', updateDetailedCalculation);
    }
});

// Záložní inicializace pro případ, že DOMContentLoaded už proběhl
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log('Document already loaded, initializing detail calculator');
    setTimeout(() => {
        // Inicializace výpočtu
        updateDetailedCalculation();
        
        // Přidání event listenerů pro vstupy
        const inputs = [
            'detail-apartment-price',
            'detail-price-per-night-input',
            'detail-annual-appreciation-input'
        ];
        
        inputs.forEach(id => {
            const input = document.getElementById(id);
            if (input) {
                input.addEventListener('input', updateDetailedCalculation);
            }
        });
    }, 100);
}
