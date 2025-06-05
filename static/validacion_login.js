document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const emailField = document.getElementById("correo");
    const passwordField = document.getElementById("password");

    const emailError = document.getElementById("correo-error");
    const passwordError = document.getElementById("password-error");

    function validarCorreo(correo) {
        return correo.endsWith("@uab.edu.bo");
    }

    function validarPassword(password) {
        return /^(?=.*[0-9\W]).{8,}$/.test(password);
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

    emailField.addEventListener("input", () => {
        validarCorreo(emailField.value)
            ? limpiarError(emailField, emailError)
            : mostrarError(emailField, emailError, "El correo debe terminar en @uab.edu.bo");
    });

    passwordField.addEventListener("input", () => {
        validarPassword(passwordField.value)
            ? limpiarError(passwordField, passwordError)
            : mostrarError(passwordField, passwordError, "Debe tener al menos 8 caracteres y un número o símbolo.");
    });

    form.addEventListener("submit", function (e) {
        let isValid = true;

        if (!validarCorreo(emailField.value)) {
            mostrarError(emailField, emailError, "El correo debe terminar en @uab.edu.bo");
            isValid = false;
        }

        if (!validarPassword(passwordField.value)) {
            mostrarError(passwordField, passwordError, "Debe tener al menos 8 caracteres y un número o símbolo.");
            isValid = false;
        }

        const contenedor = form.closest(".login-container");
        contenedor.classList.remove("form-success");

        if (!isValid) {
            e.preventDefault();
        } else {
            e.preventDefault();
            contenedor.classList.add("form-success");
            setTimeout(() => form.submit(), 300);
        }
    });

    // Mostrar/ocultar campo de token de administrador
    function mostrarToken() {
        const checkbox = document.getElementById('modo_admin');
        const tokenDiv = document.getElementById('token_container');
        if (checkbox && tokenDiv) {
            tokenDiv.style.display = checkbox.checked ? 'block' : 'none';
        }
    }

    mostrarToken();

    const checkbox = document.getElementById('modo_admin');
    if (checkbox) {
        checkbox.addEventListener("change", mostrarToken);
    }
});
