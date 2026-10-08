(function () {
    const marcador = document.getElementById("abrir-modal");
    if (marcador) {
        const modal = document.getElementById(marcador.dataset.modal);
        if (modal) {
            bootstrap.Modal.getOrCreateInstance(modal).show();
        }
    }

    document.querySelectorAll("form[data-confirmar]").forEach(function (formulario) {
        formulario.addEventListener("submit", function (evento) {
            if (!window.confirm(formulario.dataset.confirmar)) {
                evento.preventDefault();
            }
        });
    });

    document.querySelectorAll(".modal").forEach(function (modal) {
        modal.addEventListener("shown.bs.modal", function () {
            const campo = modal.querySelector("textarea, input:not([type=hidden])");
            if (campo) {
                campo.focus();
            }
        });
    });
})();
