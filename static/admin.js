async function buscarUsuario() {
    const tipo = document.getElementById('tipoBusqueda').value;
    const valor = document.getElementById('valorBusqueda').value;

    let url = '';
    if (tipo === 'correo') {
        url = `/buscar/${valor}`;
    } else if (tipo === 'id') {
        url = `/usuario/${valor}`;
    }

    try {
        const res = await fetch(url);
        if (!res.ok) throw new Error("Usuario no encontrado");

        const usuario = await res.json();
        document.getElementById('resultado').innerHTML = `
            <p><strong>ID:</strong> ${usuario.id}</p>
            <p><strong>Nombre:</strong> ${usuario.nombre}</p>
            <p><strong>Correo:</strong> ${usuario.correo}</p>
        `;
    } catch (err) {
        document.getElementById('resultado').innerHTML = `<p style="color:red;">${err.message}</p>`;
    }
}
