
document.addEventListener("DOMContentLoaded", () => {
    cargarComunicados();

    const btnAbrir = document.getElementById("btn-abrir-comunicado");
    const modal = document.getElementById("modal-comunicado");
    const btnCerrar = document.getElementById("btn-cerrar-modal");
    const btnCancelar = document.getElementById("btn-cancelar");
    const form = document.getElementById("form-comunicado");

    // --- MODAL ---
    if (btnAbrir && modal) {
        btnAbrir.addEventListener("click", () => {
            modal.classList.remove("is-hidden");
        });
    }

    [btnCerrar, btnCancelar].forEach(btn => {
        btn?.addEventListener("click", () => {
            modal.classList.add("is-hidden");
        });
    });

    modal?.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.classList.add("is-hidden");
        }
    });

    // --- FORMULARIO ---
    form?.addEventListener("submit", function (e) {
        e.preventDefault();

        const id = document.getElementById("id_aviso").value;
        const formData = new FormData(this);

        const url = id
            ? `/comunicados/editar/${id}/`
            : `/comunicados/crear/`;

        fetch(url, {
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
                document.getElementById("id_aviso").value = "";
                document.getElementById("modal-title").innerText = "Nuevo comunicado";
                modal.classList.add("is-hidden");
                cargarComunicados();
            }
        });
    });

});

// --- LISTADO ---
function cargarComunicados() {
    fetch("/comunicados/listar/")
        .then(resp => resp.json())
        .then(data => {
            const lista = document.getElementById("lista-comunicados");
            const empty = document.getElementById("comunicados-empty");

            lista.innerHTML = "";

            if (!data.length) {
                empty.hidden = false;
                return;
            }

            empty.hidden = true;

            data.forEach(c => {
                const li = document.createElement("li");
                li.className = "comunicado-card fade-in";
                li.id = `aviso-${c.id}`;

                li.innerHTML = `
                    <div class="comunicado-header">
                        <h4>${c.titulo}</h4>

                        ${c.editable ? `
                        <div class="acciones">
                            <button class="btn-edit" data-id="${c.id}">
                                <i class="fa-solid fa-pen"></i>
                            </button>
                            <button class="btn-delete" data-id="${c.id}">
                                <i class="fa-solid fa-trash"></i>
                            </button>
                        </div>` : ""}
                    </div>

                    <p>${c.descripcion}</p>
                    <small>Publicado por ${c.usuario} — ${c.fecha}</small>
                `;

                lista.appendChild(li);
            });

            // 👇 scroll por hash
            const hash = window.location.hash;
            if (hash) {
                const target = document.querySelector(hash);
                if (target) {
                    const offset = 200;
                    const pos = target.getBoundingClientRect().top + window.pageYOffset - offset;

                    window.scrollTo({ top: pos, behavior: "smooth" });

                    target.classList.add("highlight");
                    setTimeout(() => target.classList.remove("highlight"), 2000);
                }
            }
        })
        .catch(err => console.error("Error cargando comunicados:", err));
}


document.addEventListener("click", e => {
    const editBtn = e.target.closest(".btn-edit");
    if (!editBtn) return;

    const card = editBtn.closest(".comunicado-card");

    document.getElementById("id_aviso").value = editBtn.dataset.id;
    document.querySelector("[name=titulo]").value = card.querySelector("h4").innerText;
    document.querySelector("[name=descripcion]").value = card.querySelector("p").innerText;

    document.getElementById("modal-title").innerText = "Editar comunicado";
    document.getElementById("modal-comunicado").classList.remove("is-hidden");
});

document.addEventListener("click", e => {
    const delBtn = e.target.closest(".btn-delete");
    if (!delBtn) return;

    if (!confirm("¿Eliminar este comunicado?")) return;

    fetch(`/comunicados/eliminar/${delBtn.dataset.id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
    }).then(() => cargarComunicados());
});
