document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registro-form");
    const name = document.getElementById("nombre");
    const correo = document.getElementById("correo");
    const password = document.getElementById("password");

    const nameError = document.getElementById("nombre-error");
    const correoError = document.getElementById("correo-error");
    const passwordError = document.getElementById("password-error");

    function validarNombre(valor) {
        return /^[a-zA-Z\s]+$/.test(valor);
    }

    function validarCorreo(valor) {
        return valor.endsWith("@uab.edu.bo");
    }

    function validarPassword(valor) {
        return /^(?=.*[0-9\W]).{8,}$/.test(valor);
    }

    function limpiarError(input, span) {
        input.classList.remove("error");
        input.classList.add("valid"); // Agrega esta línea
        span.textContent = "";
    }

    function mostrarError(input, span, mensaje) {
        input.classList.remove("valid"); // Asegúrate de quitar el verde si antes era válido
        input.classList.add("error");
    span.textContent = mensaje;
    }
    
    name.addEventListener("input", () => {
        validarNombre(name.value)
            ? limpiarError(name, nameError)
            : mostrarError(name, nameError, "Solo letras y espacios.");
    });

    correo.addEventListener("input", () => {
        validarCorreo(correo.value)
            ? limpiarError(correo, correoError)
            : mostrarError(correo, correoError, "Debe terminar en @uab.edu.bo");
    });

    password.addEventListener("input", () => {
        validarPassword(password.value)
            ? limpiarError(password, passwordError)
            : mostrarError(password, passwordError, "Mínimo 8 caracteres con símbolo o número.");
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault(); // detenemos siempre para controlar

        let valido = true;
        const contenedor = form.closest(".form-container");
        contenedor.classList.remove("form-success");

        if (!validarNombre(name.value)) {
            mostrarError(name, nameError, "Solo letras y espacios.");
            valido = false;
        } else {
            limpiarError(name, nameError);
        }

        if (!validarCorreo(correo.value)) {
            mostrarError(correo, correoError, "Debe terminar en @uab.edu.bo");
            valido = false;
        } else {
            limpiarError(correo, correoError);
        }

        if (!validarPassword(password.value)) {
            mostrarError(password, passwordError, "Mínimo 8 caracteres con símbolo o número.");
            valido = false;
        } else {
            limpiarError(password, passwordError);
        }

        if (valido) {
            contenedor.classList.add("form-success");
            setTimeout(() => form.submit(), 300);
        }
    });

// Validación al perder el foco en el campo de nombre
    name.addEventListener("blur", async function () {
        if (!validarNombre(name.value)) {
            mostrarError(name, nameError, "Solo letras y espacios.");
        } else {
            const nombreExiste = await verificarNombre(name.value);
            if (nombreExiste) {
                mostrarError(name, nameError, "El nombre ya está registrado, ingrese otro.");
            } else {
                limpiarError(name, nameError);
            }
        }
    });
});

// Función para verificar si el nombre ya existe en la base de datos
async function verificarNombre(nombre) {
    const response = await fetch(`/buscar_nombre/${encodeURIComponent(nombre)}`);
    return response.ok; // true si el nombre existe
}
