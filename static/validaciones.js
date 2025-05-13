document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const nameField = document.querySelector("input[name='nombre']");
    const emailField = document.querySelector("input[name='correo']");
    const passwordField = document.querySelector("input[name='password']");

    function validarNombre(nombre) {
        const regex = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/; 
        return regex.test(nombre);
    }

    function validarPassword(password) {
        const regex = /^(?=.*[0-9\W]).{8,}$/;
        return regex.test(password);
    }

    function validarCorreo(correo) {
        return correo.endsWith("@uab.edu.bo");
    }

    async function verificarCorreo(correo) {
        const response = await fetch(`/buscar/${correo}`);
        return response.ok; // Devuelve true si el correo existe, false si no
    }

    function mostrarError(input, mensaje) {
        // Verificar si ya existe un mensaje de error para evitar duplicados
        if (!input.parentNode.querySelector(".error-message")) {
            const errorSpan = document.createElement("span");
            errorSpan.classList.add("error-message");
            errorSpan.textContent = mensaje;

            // Insertar el mensaje de error justo después del campo
            input.parentNode.insertBefore(errorSpan, input.nextSibling);
        }
        input.classList.add("error"); // Agregar clase de error al campo
    }

    function limpiarErrores() {
        document.querySelectorAll(".error-message").forEach(el => el.remove());
        document.querySelectorAll("input.error").forEach(input => input.classList.remove("error")); // Quitar clase de error
    }

    // Validación en tiempo real para el campo de nombre
    nameField.addEventListener("input", function () {
        limpiarErrores();
        if (!validarNombre(nameField.value)) {
            mostrarError(nameField, "El nombre solo puede contener letras y espacios.");
        }
    });

    // Validación en tiempo real para el campo de correo
    emailField.addEventListener("input", function () {
        limpiarErrores();
        if (!validarCorreo(emailField.value)) {
            mostrarError(emailField, "El correo debe terminar en @uab.edu.bo");
        }
    });

    // Validación en tiempo real para el campo de contraseña
    passwordField.addEventListener("input", function () {
        limpiarErrores();
        if (!validarPassword(passwordField.value)) {
            mostrarError(passwordField, "La contraseña debe tener al menos 8 caracteres e incluir un número o símbolo.");
        }
    });

    // Validación al perder el foco en el campo de correo
    emailField.addEventListener("blur", async function () {
        limpiarErrores();
        if (!validarCorreo(emailField.value)) {
            mostrarError(emailField, "El correo debe terminar en @uab.edu.bo");
        } else {
            const correoExiste = await verificarCorreo(emailField.value);
            if (correoExiste) {
                mostrarError(emailField, "El correo ya está registrado");
            }
        }
    });

    // Validación al perder el foco en el campo de contraseña
    passwordField.addEventListener("blur", function () {
        limpiarErrores();
        if (!validarPassword(passwordField.value)) {
            mostrarError(passwordField, "La contraseña debe tener al menos 8 caracteres e incluir un número o símbolo.");
        }
    });

    // Validación al enviar el formulario
    form.addEventListener("submit", function (event) {
        limpiarErrores();
        let isValid = true;

        if (!validarNombre(nameField.value)) {
            mostrarError(nameField, "El nombre solo puede contener letras y espacios.");
            isValid = false;
        }

        if (!validarCorreo(emailField.value)) {
            mostrarError(emailField, "El correo debe terminar en @uab.edu.bo");
            isValid = false;
        }

        if (!validarPassword(passwordField.value)) {
            mostrarError(passwordField, "La contraseña debe tener al menos 8 caracteres e incluir un número o símbolo.");
            isValid = false;
        }

        if (!isValid) {
            event.preventDefault();
        }
    });
});
