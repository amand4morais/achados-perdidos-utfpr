(function () {
    const TAMANHO_MAXIMO = 5 * 1024 * 1024;
    const TIPOS_ACEITOS = ["image/jpeg", "image/png"];

    document.querySelectorAll("input[type=file][accept]").forEach(function (campoFoto) {
        const avisoFoto = document.getElementById("aviso-" + campoFoto.id);
        if (!avisoFoto) {
            return;
        }
        campoFoto.addEventListener("change", function () {
            avisoFoto.textContent = "";
            campoFoto.classList.remove("is-invalid");
            const arquivo = campoFoto.files[0];
            if (!arquivo) {
                return;
            }
            let problema = "";
            if (!TIPOS_ACEITOS.includes(arquivo.type)) {
                problema = "Envie uma imagem no formato JPG ou PNG.";
            } else if (arquivo.size > TAMANHO_MAXIMO) {
                problema = "A imagem deve ter no máximo 5 MB.";
            }
            if (problema) {
                avisoFoto.textContent = problema;
                campoFoto.classList.add("is-invalid");
                campoFoto.value = "";
            }
        });
    });

    const botaoLocalizacao = document.getElementById("botao-localizacao");
    const campoLocal = document.getElementById("id_local");
    const avisoLocalizacao = document.getElementById("aviso-localizacao");

    if (!botaoLocalizacao || !campoLocal || !("geolocation" in navigator)) {
        return;
    }

    botaoLocalizacao.hidden = false;

    botaoLocalizacao.addEventListener("click", function () {
        botaoLocalizacao.disabled = true;
        avisoLocalizacao.textContent = "Buscando sua localização...";

        navigator.geolocation.getCurrentPosition(
            function (posicao) {
                const latitude = posicao.coords.latitude.toFixed(5);
                const longitude = posicao.coords.longitude.toFixed(5);
                const coordenadas = "Lat " + latitude + ", Long " + longitude;
                const textoAtual = campoLocal.value.trim();
                const novoTexto = textoAtual ? textoAtual + " (" + coordenadas + ")" : coordenadas;
                campoLocal.value = novoTexto.slice(0, 200);
                avisoLocalizacao.textContent = "Localização adicionada ao campo.";
                botaoLocalizacao.disabled = false;
            },
            function () {
                avisoLocalizacao.textContent = "Não foi possível obter sua localização. Preencha o local manualmente.";
                botaoLocalizacao.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
})();
