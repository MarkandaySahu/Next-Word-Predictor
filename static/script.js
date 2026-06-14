const textInput = document.getElementById('text-input');
const suggestionsBox = document.getElementById('suggestions');

// Send data to FastAPI backend
async function getPredictions(currentText) {
    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: currentText })
        });
        const data = await response.json();
        updateUI(data.predictions);
    } catch (error) {
        console.error("Error connecting to backend predictor:", error);
    }
}

// Generate pill buttons dynamically
function updateUI(predictions) {
    suggestionsBox.innerHTML = '';
    
    predictions.forEach(word => {
        const button = document.createElement('button');
        button.className = 'word-btn';
        button.textContent = word;
        
        button.addEventListener('click', () => {
            let currentText = textInput.value;
            
            // If the text box isn't empty and doesn't already end with a space, add one
            if (currentText.length > 0 && !currentText.endsWith(' ')) {
                currentText += ' ';
            }
            
            // Append the clicked word followed by a space
            textInput.value = currentText + word + ' ';
            
            textInput.focus();
            getPredictions(textInput.value);
        });
        
        suggestionsBox.appendChild(button);
    });
}

// Listen for typing input changes
textInput.addEventListener('input', (e) => {
    const text = e.target.value;
    if (text.length > 0) {
        getPredictions(text);
    } else {
        suggestionsBox.innerHTML = '';
    }
});

// uvicorn main:app --reload