document.addEventListener("DOMContentLoaded", function () {
    const botonesEliminar = document.querySelectorAll(".btn-eliminar");

    botonesEliminar.forEach((btn) => {
        btn.addEventListener("click", function () {
            const idDocumento = btn.getAttribute("data-id");

            if (confirm("¿Estás seguro de que quieres eliminar este documento?")) {
                fetch(`/api/documentos/${idDocumento}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest",
                    },
                    credentials: "include", // para enviar cookies de sesión
                })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        alert("Error: " + data.error);
                    } else {
                        alert("Documento eliminado con éxito");
                        // Opcional: recargar la página o eliminar visualmente el documento
                        location.reload();
                    }
                })
                .catch(error => {
                    console.error("Error al eliminar:", error);
                    alert("Hubo un error al intentar eliminar el documento.");
                });
            }
        });
    });
});
