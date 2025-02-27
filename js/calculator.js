// Konstantní parametry
const MORTGAGE_YEARS = 30;
const INTEREST_RATE = 4.6;
const DOWN_PAYMENT_PERCENT = 20;
const OCCUPANCY_DAYS = 182; // 50% roční obsazenost
const OPERATING_COSTS_PERCENT = 35; // 35% provozní náklady
const ANNUAL_APPRECIATION = 3.5; // Roční zhodnocení nemovitosti

function calculateInvestment(apartmentPrice, pricePerNight) {
    // Vlastní zdroje a hypotéka
    const downPayment = Math.round(apartmentPrice * (DOWN_PAYMENT_PERCENT / 100));
    const mortgageAmount = apartmentPrice - downPayment;
    
    // Výpočet měsíční splátky
    const monthlyRate = INTEREST_RATE / 12 / 100;
    const numberOfPayments = MORTGAGE_YEARS * 12;
    const monthlyPayment = Math.round(
        mortgageAmount * 
        (monthlyRate * Math.pow(1 + monthlyRate, numberOfPayments)) / 
        (Math.pow(1 + monthlyRate, numberOfPayments) - 1)
    );
    const annualMortgage = monthlyPayment * 12;

    // Výpočet jistiny hypotéky
    const annualPrincipalPayment = Math.round(mortgageAmount / MORTGAGE_YEARS);

    // Výpočet příjmů
    const annualIncome = pricePerNight * OCCUPANCY_DAYS;
    const monthlyIncome = Math.round(annualIncome / 12);
    
    // Výpočet nákladů a cash flow
    const annualOperatingCosts = Math.round(annualIncome * (OPERATING_COSTS_PERCENT / 100));
    const monthlyOperatingCosts = Math.round(annualOperatingCosts / 12);
    const netAnnualIncome = annualIncome - annualOperatingCosts;
    const annualAppreciation = Math.round(apartmentPrice * (ANNUAL_APPRECIATION / 100));
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

// Funkce pro aktualizaci výpočtu
function updateCalculation() {
    console.log('Updating investment calculation (calculator.js)');
    
    // Tato funkce je nyní prázdná, protože hlavní kalkulačka 
    // je obsluhována v main-calculator.js
}

// Funkce pro inicializaci kalkulačky
function initializeCalculator() {
    console.log('Initializing calculator (calculator.js)');
    
    // Tato funkce je nyní prázdná, protože hlavní kalkulačka 
    // je obsluhována v main-calculator.js
}

// Inicializace při načtení stránky
document.addEventListener('DOMContentLoaded', () => {
    console.log('Calculator.js loaded - pouze pro kompatibilitu');
    // Neprovádíme žádnou inicializaci, protože hlavní kalkulačka 
    // je obsluhována v main-calculator.js
});
