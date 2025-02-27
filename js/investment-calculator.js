// Funkce pro přepočet investice na hlavní stránce
function recalculateMainInvestment() {
    // Získání hodnot z inputů
    const apartmentPrice = parseFloat(document.getElementById('main-apartment-price').value);
    const annualRentalIncome = parseFloat(document.getElementById('main-price-per-night').value);
    
    // Výpočet hodnot
    const downPayment = apartmentPrice * 0.2; // 20% akontace
    const loanAmount = apartmentPrice - downPayment;
    const annualInterestRate = 0.046; // 4.6%
    const loanTermYears = 30;
    
    // Výpočet měsíční splátky
    const monthlyInterestRate = annualInterestRate / 12;
    const numberOfPayments = loanTermYears * 12;
    const monthlyPayment = loanAmount * (monthlyInterestRate * Math.pow(1 + monthlyInterestRate, numberOfPayments)) / (Math.pow(1 + monthlyInterestRate, numberOfPayments) - 1);
    
    // Roční zhodnocení nemovitosti
    const annualAppreciationRate = 0.035; // 3.5%
    
    // Měsíční příjem z pronájmu
    const monthlyRentalIncome = annualRentalIncome / 12;
    
    // Měsíční cash flow
    const monthlyCashFlow = monthlyRentalIncome - monthlyPayment;
    
    // Roční splátka jistiny hypotéky
    const annualMortgageRepayment = monthlyPayment * 12;
    
    // Formátování výsledků
    document.getElementById('main-price-value').textContent = formatCurrency(apartmentPrice) + ' Kč';
    document.getElementById('main-down-payment-value').textContent = formatCurrency(downPayment) + ' Kč';
    document.getElementById('main-monthly-payment-value').textContent = formatCurrency(monthlyPayment) + ' Kč';
    document.getElementById('main-annual-appreciation-value').textContent = (annualAppreciationRate * 100).toFixed(1) + '%';
    document.getElementById('main-annual-income-value').textContent = formatCurrency(annualRentalIncome) + ' Kč';
    document.getElementById('main-cash-flow-value').textContent = formatCurrency(monthlyCashFlow) + ' Kč';
    document.getElementById('main-annual-mortgage-repayment-value').textContent = formatCurrency(annualMortgageRepayment) + ' Kč';
}

// Pomocná funkce pro formátování měny
function formatCurrency(value) {
    return Math.round(value).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
}

// Přidání funkce do globálního objektu window
window.recalculateMainInvestment = recalculateMainInvestment;

// Inicializace kalkulačky po načtení stránky
document.addEventListener('DOMContentLoaded', function() {
    // Inicializace kalkulačky na hlavní stránce
    if (document.getElementById('main-apartment-price')) {
        recalculateMainInvestment();
        
        // Přidání event listenerů pro automatický přepočet
        document.getElementById('main-apartment-price').addEventListener('input', recalculateMainInvestment);
        document.getElementById('main-price-per-night').addEventListener('input', recalculateMainInvestment);
    }
});
