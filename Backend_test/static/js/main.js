// Dropdown de usuario
const userToggle = document.getElementById('userDropdownToggle');
const dropdown = document.getElementById('userDropdown');

if (userToggle && dropdown) {
    userToggle.addEventListener('click', (e) => {
        e.stopPropagation();
        const isActive = dropdown.classList.toggle('active');
        userToggle.setAttribute('aria-expanded', isActive ? 'true' : 'false');
    });

    // Cerrar si se hace clic fuera del dropdown
    document.addEventListener('click', (e) => {
        if (!userToggle.contains(e.target)) dropdown.classList.remove('active');
    });
}

// Marcar enlace activo según la URL
(function markActiveLinks() {
    const current = window.location.pathname.replace(/\/+$/, '');
    document.querySelectorAll('.main-nav a').forEach(a => {
        const href = a.getAttribute('href') || '';
        if (href && current && href === current) {
            a.classList.add('active');
        }
    });
})();
