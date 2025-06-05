function toggleComentarios(documentoId) {
    const contenedor = document.getElementById(`comentarios-${documentoId}`);
    if (contenedor.style.display === "none" || contenedor.style.display === "") {
        contenedor.style.display = "block";
        cargarComentarios(documentoId);
    } else {
        contenedor.style.display = "none";
    }
}

async function cargarComentarios(documentoId) {
    try {
        const response = await fetch(`/api/documentos/${documentoId}/comentarios`);
        const comentarios = await response.json();
        const lista = document.getElementById(`comentarios-list-${documentoId}`);
        lista.innerHTML = ''; // Limpiar antes de recargar

        if (comentarios.length === 0) {
            lista.innerHTML = '<p>No hay comentarios aún.</p>';
        } else {
            comentarios.forEach(comentario => {
                const div = document.createElement('div');
                div.classList.add('comentario-item');

                let botones = '';
                if (comentario.es_autor) {
                    botones = `
                        <button class="editar-btn" data-id="${comentario.id_comentario}" data-doc="${documentoId}">✏️</button>
                        <button class="eliminar-btn" data-id="${comentario.id_comentario}" data-doc="${documentoId}">🗑️</button>
                    `;
                }

                div.innerHTML = `
                    <div class="comentario-header">
                        <strong>${comentario.autor}</strong> - ${comentario.fecha}
                        ${botones}
                    </div>
                    <div class="comentario-contenido" data-id="${comentario.id_comentario}">
                        ${comentario.contenido}
                    </div>
                    <hr>
                `;
                lista.appendChild(div);
            });

            // Agregar listeners para editar comentarios
            lista.querySelectorAll('.editar-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idComentario = btn.getAttribute('data-id');
                    const docId = btn.getAttribute('data-doc');
                    iniciarEdicionComentario(idComentario, docId);
                });
            });

            // Agregar listeners para eliminar comentarios
            lista.querySelectorAll('.eliminar-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idComentario = btn.getAttribute('data-id');
                    const docId = btn.getAttribute('data-doc');
                    eliminarComentario(idComentario, docId);
                });
            });
        }
    } catch (err) {
        console.error("Error al cargar comentarios:", err);
    }
}

async function agregarComentario(event, documentoId) {
    event.preventDefault();
    const form = event.target;
    const textarea = form.querySelector('textarea');
    const contenido = textarea.value.trim();
    if (!contenido) return;

    const formData = new FormData();
    formData.append('contenido', contenido);

    try {
        const response = await fetch(`/api/documentos/${documentoId}/comentarios`, {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            textarea.value = '';
            cargarComentarios(documentoId);
        } else {
            const error = await response.json();
            alert(error.error || 'Error al enviar el comentario');
        }
    } catch (err) {
        console.error("Error al agregar comentario:", err);
    }
}

async function eliminarComentario(idComentario, documentoId) {
    if (!confirm("¿Deseas eliminar este comentario?")) return;

    try {
        const response = await fetch(`/api/comentarios/${idComentario}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            cargarComentarios(documentoId);
        } else {
            const error = await response.json();
            alert(error.error || 'No se pudo eliminar el comentario');
        }
    } catch (err) {
        console.error("Error al eliminar comentario:", err);
    }
}

function iniciarEdicionComentario(idComentario, documentoId) {
    const divContenido = document.querySelector(`.comentario-contenido[data-id="${idComentario}"]`);
    const contenidoActual = divContenido.innerText;

    const textarea = document.createElement('textarea');
    textarea.value = contenidoActual;
    textarea.rows = 3;

    const guardarBtn = document.createElement('button');
    guardarBtn.innerText = '💾 Guardar';
    guardarBtn.classList.add('guardar-edicion-btn');
    guardarBtn.onclick = () => guardarEdicionComentario(idComentario, documentoId, textarea.value);

    // Limpiar y reemplazar contenido
    divContenido.innerHTML = '';
    divContenido.appendChild(textarea);
    divContenido.appendChild(guardarBtn);
}

async function guardarEdicionComentario(idComentario, documentoId, nuevoContenido) {
    const formData = new FormData();
    formData.append('contenido', nuevoContenido);

    try {
        const response = await fetch(`/api/comentarios/${idComentario}`, {
            method: 'PUT',
            body: formData
        });

        if (response.ok) {
            cargarComentarios(documentoId);
        } else {
            const error = await response.json();
            alert(error.error || 'No se pudo editar el comentario');
        }
    } catch (err) {
        console.error("Error al editar comentario:", err);
    }
}

// Agregar eventos al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.toggle-comments-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const documentoId = btn.getAttribute('data-id');
            toggleComentarios(documentoId);
        });
    });

    document.querySelectorAll('.comentario-form').forEach(form => {
        form.addEventListener('submit', event => {
            const documentoId = form.getAttribute('data-id');
            agregarComentario(event, documentoId);
        });
    });
});
