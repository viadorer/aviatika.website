// Debug helper script
console.log('Debug helper script loaded');

// Funkce pro kontrolu existence elementů
function checkAllElements() {
    console.log('Debug helper: Checking all elements with IDs');
    
    // Najdeme všechny elementy s ID
    const elementsWithId = document.querySelectorAll('[id]');
    console.log(`Found ${elementsWithId.length} elements with IDs`);
    
    // Vypíšeme je
    elementsWithId.forEach(el => {
        console.log(`Element ID: ${el.id}, tagName: ${el.tagName}, textContent: ${el.textContent.substring(0, 20)}${el.textContent.length > 20 ? '...' : ''}`);
    });
}

// Funkce pro kontrolu načtených skriptů
function checkLoadedScripts() {
    console.log('Debug helper: Checking loaded scripts');
    
    const scripts = document.querySelectorAll('script');
    console.log(`Found ${scripts.length} script elements`);
    
    scripts.forEach((script, index) => {
        console.log(`Script ${index + 1}: src=${script.src || 'inline'}, type=${script.type || 'text/javascript'}`);
    });
}

// Kontrola po načtení stránky
window.addEventListener('load', function() {
    console.log('Debug helper: Window load event fired');
    
    // Počkáme 2 sekundy a pak zkontrolujeme elementy
    setTimeout(function() {
        checkAllElements();
        checkLoadedScripts();
        
        // Zkusíme ručně spustit výpočet
        console.log('Debug helper: Attempting to manually trigger calculation');
        
        // Zkusíme najít a zavolat všechny funkce pro aktualizaci kalkulaček
        if (typeof updateMainCalculation === 'function') {
            console.log('Debug helper: Calling updateMainCalculation');
            updateMainCalculation();
        }
        
        if (typeof updateCalculation === 'function') {
            console.log('Debug helper: Calling updateCalculation');
            updateCalculation();
        }
        
        if (typeof updateDetailedCalculation === 'function') {
            console.log('Debug helper: Calling updateDetailedCalculation');
            updateDetailedCalculation();
        }
    }, 2000);
});
