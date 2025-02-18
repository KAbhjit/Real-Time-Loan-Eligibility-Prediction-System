// app.js
function submitForm() {
    const formData = new FormData(document.getElementById("loanForm"));
    const data = Object.fromEntries(formData);

    fetch("/predict_eligibility", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            document.getElementById("eligibilityResult").innerText = "Error: " + result.error;
        } else {
            document.getElementById("eligibilityResult").innerText = 
                result.eligibility ? "Eligible" : "Not Eligible";
        }
    })
    .catch(error => {
        document.getElementById("eligibilityResult").innerText = "An error occurred: " + error;
    });

    fetch("/recommend_loan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.error) {
            document.getElementById("recommendationResult").innerText = "Error: " + result.error;
        } else {
            document.getElementById("recommendationResult").innerText = result.recommendation;
        }
    })
    .catch(error => {
        document.getElementById("recommendationResult").innerText = "An error occurred: " + error;
    });
}
