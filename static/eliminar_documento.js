document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-eliminar').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            if (confirm('¿Estás seguro de que deseas eliminar este documento?')) {
                fetch(`/api/documentos/${id}`, { method: 'DELETE' })
                    .then(res => res.json())
                    .then(data => {
                        if (data.mensaje) {
                            this.closest('.document-item, .card').remove();
                            alert(data.mensaje);
                        } else {
                            alert(data.error || 'No se pudo eliminar el documento.');
                        }
                    });
            }
        });
    });
});
