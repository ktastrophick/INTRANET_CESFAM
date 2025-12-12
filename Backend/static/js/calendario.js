<<<<<<< HEAD
//esto aun no se usa...ver despues.
=======

(() => {
  // ====== CSRF ======
  function getCookie(name) {
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  function getCsrf() {
    const c = getCookie('csrftoken');
    if (c) return c;
    const hidden = document.querySelector('input[name=csrfmiddlewaretoken]');
    return hidden ? hidden.value : '';
  }
  const csrftoken = getCsrf();

  // ====== Helpers ======
  const fmt = (d) => d.toISOString().slice(0, 10);
  function firstDayOfMonth(d) { return new Date(d.getFullYear(), d.getMonth(), 1); }
  function lastDayOfMonth(d) { return new Date(d.getFullYear(), d.getMonth() + 1, 0); }
  function mondayOfWeek(d) { const t = new Date(d), k = (t.getDay() || 7); if (k > 1) t.setDate(t.getDate() - (k - 1)); return t; }
  function sundayOfWeek(d) { const t = new Date(d), k = (t.getDay() || 7); if (k < 7) t.setDate(t.getDate() + (7 - k)); return t; }
  function monthLabel(d) {
    return d.toLocaleDateString('es-CL', { month: 'long', year: 'numeric' }).replace(/^\w/, c => c.toUpperCase());
  }

  // ====== ELEMENTOS ======
  const ul = document.getElementById('items');
  const empty = document.getElementById('empty');
  const monthGrid = document.getElementById('month-grid');
  const monthLabelEl = document.getElementById('month-label');
  const prevBtn = document.getElementById('prev-month');
  const nextBtn = document.getElementById('next-month');
  const todayBtn = document.getElementById('today-month');
  const tabMes = document.getElementById('tab-mes');
  const tabLista = document.getElementById('tab-lista');

  // ====== LISTA ======
  function liTemplate(e) {
    return `
      <li class="item" data-id="${e.id}">
        <div class="left">
          <span class="badge" style="background:${e.color || '#3A8DFF'}"></span>
          <div class="meta">
            <strong>${e.titulo}</strong>
            <span class="date">${e.fecha}</span>
            ${e.descripcion ? `<div class="desc">${e.descripcion}</div>` : ''}
          </div>
        </div>
        <div class="actions">
          <button class="edit">Editar</button>
          <button class="del danger">Eliminar</button>
        </div>
      </li>`;
  }

  function toggleEmpty(hasItems) { if (empty) empty.hidden = hasItems; }

  async function load(query = '') {
    if (!ul) return;
    const res = await fetch(`/api/eventos/${query}`);
    const data = await res.json();
    const items = (data.results || []);
    ul.innerHTML = items.map(liTemplate).join('');
    toggleEmpty(items.length > 0);
  }

  // Crear
  const formNuevo = document.getElementById('form-nuevo');
  if (formNuevo) {
    formNuevo.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      const rawDate = document.getElementById('fecha').value;
      const iso = rawDate ? new Date(rawDate).toISOString().slice(0, 10) : '';
      const payload = {
        titulo: document.getElementById('titulo').value.trim(),
        fecha: iso,
        color: document.getElementById('color')?.value || '#3A8DFF',
        descripcion: document.getElementById('desc').value || ''
      };
      if (!payload.titulo || !payload.fecha) return alert('Completa título y fecha.');
      const res = await fetch('/api/eventos/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
        body: JSON.stringify(payload)
      });
      if (res.ok) { ev.target.reset(); await load(); await loadMonth(); }
      else alert(await res.text());
    });
  }

  // Editar / Eliminar
  if (ul) {
    ul.addEventListener('click', async ev => {
      const li = ev.target.closest('.item'); if (!li) return;
      const id = li.dataset.id;

      if (ev.target.classList.contains('del')) {
        if (!confirm('¿Eliminar este evento?')) return;
        const res = await fetch(`/api/eventos/${id}/`, { method: 'DELETE', headers: { 'X-CSRFToken': csrftoken } });
        if (res.ok) { li.remove(); toggleEmpty(ul.children.length > 0); await loadMonth(); }
        else alert(await res.text());
      }

      if (ev.target.classList.contains('edit')) {
        const currentTitle = li.querySelector('strong').textContent;
        const currentDate = li.querySelector('.date').textContent;
        const titulo = prompt('Nuevo título:', currentTitle); if (!titulo) return;
        const fecha = prompt('Nueva fecha (YYYY-MM-DD):', currentDate); if (!fecha) return;
        const res = await fetch(`/api/eventos/${id}/`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
          body: JSON.stringify({ titulo, fecha })
        });
        if (res.ok) { load(); loadMonth(); } else alert(await res.text());
      }
    });
  }

  // Filtros lista
  const btnFiltrar = document.getElementById('btn-filtrar');
  const btnLimpiar = document.getElementById('btn-limpiar');
  if (btnFiltrar) {
    btnFiltrar.addEventListener('click', () => {
      const s = document.getElementById('filtro-start').value;
      const e = document.getElementById('filtro-end').value;
      const q = (s || e) ? `?${s ? `start=${s}` : ''}${s && e ? '&' : ''}${e ? `end=${e}` : ''}` : '';
      load(q);
    });
  }
  if (tabLista) {
    tabLista.addEventListener('click', () => {
      document.querySelector('.event-list-container')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  }
  if (btnLimpiar) {
    btnLimpiar.addEventListener('click', () => {
      document.getElementById('filtro-start').value = '';
      document.getElementById('filtro-end').value = '';
      load();
    });
  }

  // ====== MES ======
  let current = new Date();

  async function loadMonth() {
    if (!monthGrid) return;
    const start = mondayOfWeek(firstDayOfMonth(current));
    const end = sundayOfWeek(lastDayOfMonth(current));

    const res = await fetch(`/api/eventos/?start=${fmt(start)}&end=${fmt(end)}`);
    const data = await res.json();
    const map = new Map();
    for (const e of (data.results || [])) { const k = e.fecha; if (!map.has(k)) map.set(k, []); map.get(k).push(e); }

    if (monthLabelEl) monthLabelEl.textContent = monthLabel(current);

    // Mantén los 7 encabezados (dow)
    while (monthGrid.children.length > 7) monthGrid.removeChild(monthGrid.lastChild);

    const endCopy = new Date(end);
    for (let d = new Date(start); d <= endCopy; d.setDate(d.getDate() + 1)) {
      const cell = document.createElement('div');
      cell.className = 'day' + (d.getMonth() !== current.getMonth() ? ' out' : '');
      const dateStr = fmt(d);

      // Marca el día de hoy
      if (d.toDateString() === new Date().toDateString()) {
        cell.classList.add('today');
      }

      const head = document.createElement('div');
      head.className = 'date';
      head.textContent = d.getDate();
      cell.appendChild(head);

      for (const ev of (map.get(dateStr) || [])) {
        const a = document.createElement('a');
        a.className = 'event-pill';
        a.title = ev.descripcion || '';
        a.innerHTML = `<span class="dot" style="background:${ev.color || '#3A8DFF'}"></span>${ev.titulo}`;
        a.href = 'javascript:void(0)';
        a.addEventListener('click', () => {
          const nuevoTitulo = prompt('Editar título:', ev.titulo);
          if (!nuevoTitulo) return;
          fetch(`/api/eventos/${ev.id}/`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
            body: JSON.stringify({ titulo: nuevoTitulo, fecha: ev.fecha })
          }).then(loadMonth);
        });
        cell.appendChild(a);
      }
      monthGrid.appendChild(cell);
    }
  }

  function showMes() {
    tabMes?.classList.add('active');
    tabLista?.classList.remove('active');
    if (monthGrid) monthGrid.hidden = false;
    const mc = document.getElementById('month-controls');
    if (mc) mc.style.display = 'flex';
    loadMonth();
  }
  function showLista() {
    tabLista?.classList.add('active');
    tabMes?.classList.remove('active');
    if (monthGrid) monthGrid.hidden = true;
    const mc = document.getElementById('month-controls');
    if (mc) mc.style.display = 'none';
    load();
  }

  tabMes?.addEventListener('click', showMes);
  tabLista?.addEventListener('click', showLista);
  prevBtn?.addEventListener('click', () => { current = new Date(current.getFullYear(), current.getMonth() - 1, 1); loadMonth(); });
  nextBtn?.addEventListener('click', () => { current = new Date(current.getFullYear(), current.getMonth() + 1, 1); loadMonth(); });
  todayBtn?.addEventListener('click', () => { current = new Date(); loadMonth(); });

  // ====== ARRANQUE ======
  document.addEventListener('DOMContentLoaded', () => {
    const fecha = document.getElementById('fecha');
    if (fecha) fecha.valueAsDate = new Date();
    showMes();  // vista por defecto
    load();     // y carga la lista para sincronizar
  });
})();
>>>>>>> 0327cec497f69a6d9b0db1adf549f97a6c10ff9e
