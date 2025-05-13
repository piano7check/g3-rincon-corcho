// Muestra u oculta el menú lateral de navegación
function toggleMenu() {
    const menu = document.getElementById('menuDropdown');
    const menuIcon = document.querySelector('.fa-bars');

    menu.classList.toggle('show'); // Alterna visibilidad del menú
    menuIcon.classList.toggle('rotated'); // Gira el ícono al abrir

    // Cierra el menú de perfil si está abierto
    document.getElementById('profileDropdown').classList.remove('show');
}
// Muestra u oculta el menú del perfil de usuario
function toggleProfile() {
    const profile = document.getElementById('profileDropdown');
    const menu = document.getElementById('menuDropdown');
    const menuIcon = document.querySelector('.fa-bars');

    profile.classList.toggle('show');       // Alterna visibilidad del perfil
    menu.classList.remove('show');          // Cierra el menú lateral
    menuIcon.classList.remove('rotated');   // Restaura rotación del ícono
}

// Cierra menús al hacer clic fuera de ellos
window.onclick = function(e) {
    // Verifica si el clic no fue sobre el icono de menú ni dentro del menú desplegable
    if (!e.target.matches('.fa-bars') && !e.target.closest('#menuDropdown')) {
        // Si se hizo clic fuera del icono de menú y del menú, lo cierra
        document.getElementById('menuDropdown').classList.remove('show');
        document.querySelector('.fa-bars').classList.remove('rotated');
    }

    // Verifica si el clic no fue sobre el icono de perfil ni dentro del menú de perfil
    if (!e.target.matches('.fa-user') && !e.target.closest('#profileDropdown')) {
        // Si se hizo clic fuera del icono y del menú de perfil, lo cierra
        document.getElementById('profileDropdown').classList.remove('show');
    }
};

