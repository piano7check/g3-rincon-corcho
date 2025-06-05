document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("editar-form");

    const nombre = document.getElementById("nombre");
    const correo = document.getElementById("correo");
    const password = document.getElementById("password");

    const nombreError = document.getElementById("nombre-error");
    const correoError = document.getElementById("correo-error");
    const passwordError = document.getElementById("password-error");

    function validarNombre(valor) {
        return /^[a-zA-Z\s]+$/.test(valor);
    }

    function validarCorreo(valor) {
        return valor.endsWith("@uab.edu.bo");
    }

    function validarPassword(valor) {
        return valor === "" || /^(?=.*[0-9\W]).{8,}$/.test(valor);
    }

    function limpiarError(input, span) {
        input.classList.remove("error");
        input.classList.add("valid");
        span.textContent = "";
    }

    function mostrarError(input, span, mensaje) {
        input.classList.remove("valid");
        input.classList.add("error");
        span.textContent = mensaje;
    }

    nombre.addEventListener("input", () => {
        validarNombre(nombre.value)
            ? limpiarError(nombre, nombreError)
            : mostrarError(nombre, nombreError, "Solo letras y espacios.");
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
        let valido = true;

        if (!validarNombre(nombre.value)) {
            mostrarError(nombre, nombreError, "Solo letras y espacios.");
            valido = false;
        }

        if (!validarCorreo(correo.value)) {
            mostrarError(correo, correoError, "Debe terminar en @uab.edu.bo");
            valido = false;
        }

        if (!validarPassword(password.value)) {
            mostrarError(password, passwordError, "Mínimo 8 caracteres con símbolo o número.");
            valido = false;
        }

        if (!valido) {
            e.preventDefault();
        }
    });
});
