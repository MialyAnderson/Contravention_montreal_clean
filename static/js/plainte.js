document.getElementById("formPlainte").addEventListener("submit", function(e) {
    e.preventDefault();
    const alertSuccess = document.getElementById("alertSuccess");
    const alertError = document.getElementById("alertError");
    alertSuccess.style.display = "none";
    alertError.style.display = "none";
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    const submitBtn = e.target.querySelector("button[type='submit']");
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Envoi en cours...';
    submitBtn.disabled = true;
    fetch("/demande-inspection", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(json => {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Envoyer la plainte';
        submitBtn.disabled = false;
        
        if (json.message) {
            alertSuccess.style.display = "block";
            alertSuccess.innerHTML = `<i class="fas fa-check-circle me-2"></i> ${json.message}`;
            setTimeout(function() {
                window.location.href = "/";
            }, 2000);
        } else if (json.error) {
            alertError.style.display = "block";
            alertError.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> ${json.error}`;
        }
    })
    .catch(err => {
        submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Envoyer la plainte';
        submitBtn.disabled = false;
        
        alertError.style.display = "block";
        alertError.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i> Erreur lors de l\'envoi de la plainte. Veuillez réessayer.';
    });
});