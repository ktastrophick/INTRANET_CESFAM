// Dropdown
const userToggle = document.getElementById('userDropdownToggle');
const dropdown = document.getElementById('userDropdown');

if (userToggle && dropdown) {
    userToggle.addEventListener('click', (e) => {
    e.stopPropagation();
    const isActive = dropdown.classList.toggle('active');
    userToggle.setAttribute('aria-expanded', isActive ? 'true' : 'false');
    });

  // Cerrar si se hace clic fuera
    document.addEventListener('click', (e) => {
        if (!userToggle.contains(e.target)) dropdown.classList.remove('active');
    });
}

// Menú móvil
const toggleBtn = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobile-menu');
if (toggleBtn && mobileMenu) {
    toggleBtn.addEventListener('click', () => {
        const nowActive = mobileMenu.classList.toggle('active');
        mobileMenu.setAttribute('aria-hidden', nowActive ? 'false' : 'true');
    });
}

// Enlaces activos por URL (fallback si no se usan url_names)
(function markActiveLinks(){
    const current = window.location.pathname.replace(/\/+$/, '');
    document.querySelectorAll('.main-nav a, .mobile-menu a').forEach(a=>{
        const href = a.getAttribute('href') || '';
        if (href && current && href === current) a.classList.add('active');
    });
})();
