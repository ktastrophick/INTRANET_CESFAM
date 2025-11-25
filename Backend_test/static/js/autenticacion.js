    // Mostrar/ocultar contraseña
    document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.toggle-password');
    const passwordInput = document.querySelector('#id_password');
    const toggleIcon = document.querySelector('#toggleIcon');
    
    if (toggleBtn && passwordInput) {
        toggleBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Cambiar icono
        if (type === 'text') {
            toggleIcon.classList.remove('fa-eye');
            toggleIcon.classList.add('fa-eye-slash');
        } else {
            toggleIcon.classList.remove('fa-eye-slash');
            toggleIcon.classList.add('fa-eye');
        }
        });
    }

    // Manejar checkbox "Mantener sesión"
    const rememberCheckbox = document.querySelector('#rememberCheckbox');
    const sessionExpInput = document.querySelector('#sessionExp');
    
    if (rememberCheckbox && sessionExpInput) {
        rememberCheckbox.addEventListener('change', function() {
        sessionExpInput.value = this.checked ? 'keep' : '';
        });
    }
    });
