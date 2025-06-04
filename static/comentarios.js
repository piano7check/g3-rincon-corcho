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
                div.innerHTML = `
                    <div class="comentario-header">
                        <strong>${comentario.autor}</strong> - ${comentario.fecha}
                        ${comentario.es_autor ? `<button class="eliminar-btn" data-id="${comentario.id_comentario}" data-doc="${documentoId}">🗑️</button>` : ''}
                    </div>
                    <div class="comentario-contenido">
                        ${comentario.contenido}
                    </div>
                    <hr>
                `;
                lista.appendChild(div);
            });

            // Agregar listener para eliminar comentarios a los botones creados dinámicamente
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

// Aquí agregamos los event listeners a todos los botones y formularios, después de que cargue el DOM
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
