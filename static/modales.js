// static/modales.js

// --- Modal Subir Documento ---
const uploadModal = document.getElementById('uploadModal');
const openUploadBtn = document.getElementById('openUploadModal');
const closeUploadBtn = document.getElementById('closeUploadModal');

if (openUploadBtn && uploadModal) {
    openUploadBtn.onclick = function() {
        uploadModal.style.display = "block";
        if (typeof loadSemestres === "function") loadSemestres(); // Carga semestres si existe la función
    }
}
if (closeUploadBtn && uploadModal) {
    closeUploadBtn.onclick = function() {
        uploadModal.style.display = "none";
    }
}

// --- Modal Crear Materia ---
const crearMateriaModal = document.getElementById('modalCrearMateria');
const openCrearMateriaBtn = document.querySelector('.admin-button-crear');
const closeCrearMateriaBtn = document.getElementById('closeCrearMateria');

if (openCrearMateriaBtn && crearMateriaModal) {
    openCrearMateriaBtn.onclick = function(e) {
        e.preventDefault();
        crearMateriaModal.style.display = "block";
    }
}
if (closeCrearMateriaBtn && crearMateriaModal) {
    closeCrearMateriaBtn.onclick = function() {
        crearMateriaModal.style.display = "none";
    }
}

// --- Cerrar modales al hacer clic fuera ---
window.onclick = function(event) {
    if (event.target === uploadModal) {
        uploadModal.style.display = "none";
    }
    if (event.target === crearMateriaModal) {
        crearMateriaModal.style.display = "none";
    }
}