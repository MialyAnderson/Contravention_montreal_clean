document.addEventListener('DOMContentLoaded', function() {
    const btnAdmin = document.getElementById("btn-admin");
    const btnUser = document.getElementById("btn-user");
    const formAdmin = document.getElementById("form-admin");
    const formUser = document.getElementById("form-user");

    btnAdmin.addEventListener("click", () => {
        formAdmin.classList.add("active");
        formUser.classList.remove("active");
        btnAdmin.classList.add("active");
        btnUser.classList.remove("active");
    });

    btnUser.addEventListener("click", () => {
        formUser.classList.add("active");
        formAdmin.classList.remove("active");
        btnUser.classList.add("active");
        btnAdmin.classList.remove("active");
    });

    const toggleAdminPassword = document.getElementById('toggleAdminPassword');
    const adminPassword = document.getElementById('password');
    
    if (toggleAdminPassword && adminPassword) {
        toggleAdminPassword.addEventListener('click', function() {
            const type = adminPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            adminPassword.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
    
    const toggleUserPassword = document.getElementById('toggleUserPassword');
    const userPassword = document.getElementById('password_user');
    
    if (toggleUserPassword && userPassword) {
        toggleUserPassword.addEventListener('click', function() {
            const type = userPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            userPassword.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
    
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('inscription') === 'ok') {
        document.getElementById('inscription-success').style.display = 'block';
        btnUser.click(); 
    }
});