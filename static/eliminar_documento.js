async function eliminarDocumento(idDocumento) {
    const confirmacion = confirm("¿Estás seguro de que deseas eliminar este documento?");
    if (!confirmacion) return;

    try {
        const respuesta = await fetch(`/api/documentos/${idDocumento}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const datos = await respuesta.json();

        if (respuesta.ok) {
            alert(datos.mensaje || "Documento eliminado correctamente.");
            // Recarga la página para reflejar el cambio
            location.reload();
        } else {
            alert(datos.error || "Ocurrió un error al eliminar el documento.");
        }
    } catch (error) {
        console.error("Error eliminando documento:", error);
        alert("Error de red o del servidor.");
    }
}
