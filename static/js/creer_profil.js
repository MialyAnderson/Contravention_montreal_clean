document.addEventListener('DOMContentLoaded', function() {
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('mot_de_passe');
    
    togglePassword.addEventListener('click', function() {
        const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
        password.setAttribute('type', type);
        this.classList.toggle('fa-eye');
        this.classList.toggle('fa-eye-slash');
    });
    
    const passwordInput = document.getElementById('mot_de_passe');
    const strengthBar = document.getElementById('passwordStrength');
    const feedback = document.getElementById('passwordFeedback');
    
    passwordInput.addEventListener('input', function() {
        const value = passwordInput.value;
        let strength = 0;
        let message = '';
        
        if (value.length >= 8) strength += 1;
        if (value.match(/[A-Z]/)) strength += 1;
        if (value.match(/[0-9]/)) strength += 1;
        if (value.match(/[^A-Za-z0-9]/)) strength += 1;
        
        switch (strength) {
            case 0:
                strengthBar.style.width = '0%';
                message = 'Le mot de passe doit contenir au moins 8 caractères';
                feedback.className = 'form-text';
                break;
            case 1:
                strengthBar.style.width = '25%';
                message = 'Mot de passe faible';
                feedback.className = 'form-text weak';
                break;
            case 2:
                strengthBar.style.width = '50%';
                message = 'Mot de passe moyen';
                feedback.className = 'form-text medium';
                break;
            case 3:
                strengthBar.style.width = '75%';
                message = 'Mot de passe fort';
                feedback.className = 'form-text strong';
                break;
            case 4:
                strengthBar.style.width = '100%';
                message = 'Mot de passe très fort';
                feedback.className = 'form-text strong';
                break;
        }
        
        feedback.textContent = message;
    });
    
    document.getElementById("profilForm").addEventListener("submit", function(e) {
        e.preventDefault();
        
        const responseDiv = document.getElementById("reponse");
        responseDiv.style.display = 'block';
        responseDiv.innerHTML = '<i class="fas fa-circle-notch fa-spin me-2"></i> Traitement en cours...';
        responseDiv.className = 'alert alert-info mt-3 text-center fw-semibold';

        const select = document.getElementById("etablissements");
        const etablissements = Array.from(select.selectedOptions).map(option => option.value);

        const data = {
            nom_complet: document.getElementById("nom").value,
            email: document.getElementById("email").value,
            mot_de_passe: document.getElementById("mot_de_passe").value,
            etablissements_surveilles: etablissements
        };

        fetch("/api/creer-profil", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        })
        .then(res => res.json())
        .then(json => {
            if (json.message) {
                responseDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i> Compte créé avec succès! Redirection...';
                responseDiv.className = 'alert alert-success mt-3 text-center fw-semibold';
                setTimeout(() => {
                    window.location.href = "/connexion?inscription=ok";
                }, 1500);
            } else {
                responseDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> ${json.error || "Erreur inconnue"}`;
                responseDiv.className = 'alert alert-danger mt-3 text-center fw-semibold';
            }
        })
        .catch(() => {
            responseDiv.innerHTML = '<i class="fas fa-times-circle me-2"></i> Erreur de communication avec le serveur.';
            responseDiv.className = 'alert alert-danger mt-3 text-center fw-semibold';
        });
    });
});