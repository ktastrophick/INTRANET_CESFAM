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
                    modal.classList.add("is-hidden");
                } else {
                    alert("Error al crear el comunicado");
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

            if (data.length === 0) {
                empty.hidden = false;
                return;
            }

            empty.hidden = true;

            data.forEach(c => {
                const li = document.createElement("li");
                li.className = "comunicado-card fade-in";
                li.id = `aviso-${c.id}`;
                li.innerHTML = `
                    <h4>${c.titulo}</h4>
                    <p>${c.descripcion}</p>
                    <small>Publicado por ${c.usuario} — ${c.fecha}</small>
                `;
                lista.appendChild(li);
            });
            // 👇 SCROLL AL COMUNICADO SI VIENE DESDE EL INDEX
            const hash = window.location.hash;
            if (hash) {
                const target = document.querySelector(hash);
                if (target) {

                    const offset = 200; // espacio superior (ajústalo)
                    const elementPosition =
                        target.getBoundingClientRect().top + window.pageYOffset;
                    const offsetPosition = elementPosition - offset;

                    window.scrollTo({
                        top: offsetPosition,
                        behavior: "smooth"
                    });

                    target.classList.add("highlight");

                    setTimeout(() => {
                        target.classList.remove("highlight");
                    }, 2000);
                }
            }
        });
}
