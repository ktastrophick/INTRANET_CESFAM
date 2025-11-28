document.addEventListener("DOMContentLoaded", cargarComunicados);

function cargarComunicados() {
    fetch("/comunicados/listar/")

        .then(resp => resp.json())
        .then(data => {
            const lista = document.getElementById("lista-comunicados");
            const empty = document.getElementById("comunicados-empty");

            lista.innerHTML = "";

            if (data.length === 0) {
                empty.hidden = false;
                return;
            }

            empty.hidden = true;

            data.forEach(c => {
                const li = document.createElement("li");
                li.className = "item";

                li.innerHTML = `
                    <div class="item-content">
                        <h4>${c.titulo}</h4>
                        <p>${c.descripcion}</p>
                        <small>Publicado por ${c.usuario} — ${c.fecha}</small>
                    </div>
                `;
                lista.appendChild(li);
            });
        });
}

document.getElementById("form-comunicado")?.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(this);

    fetch("/comunicados/crear/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: formData
    })
        .then(resp => resp.json())
        .then(data => {
            if (data.ok) {
                this.reset();
                cargarComunicados();
            } else {
                alert("Error al crear el comunicado");
            }
        });
});

