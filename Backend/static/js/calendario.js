// calendario.js - VERSIÓN CORREGIDA
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

  let current = new Date();

  // ====== FUNCIONES AUXILIARES ======
  const fmt = (d) => d.toISOString().slice(0, 10);
  
  function firstDayOfMonth(d) { 
    return new Date(d.getFullYear(), d.getMonth(), 1); 
  }
  
  function lastDayOfMonth(d) { 
    return new Date(d.getFullYear(), d.getMonth() + 1, 0); 
  }
  
  function mondayOfWeek(d) { 
    const t = new Date(d);
    const day = t.getDay();
    const diff = t.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(t.setDate(diff));
  }
  
  function sundayOfWeek(d) {
    const t = new Date(d);
    const day = t.getDay();
    const diff = t.getDate() + (7 - day) - (day === 0 ? 7 : 0);
    return new Date(t.setDate(diff));
  }

  function monthLabel(d) {
    return d.toLocaleDateString('es-CL', { month: 'long', year: 'numeric' })
            .replace(/^\w/, c => c.toUpperCase());
  }

  // ====== GESTIÓN DE EVENTOS ======
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
          <button class="edit btn-light">Editar</button>
          <button class="del btn-danger">Eliminar</button>
        </div>
      </li>`;
  }

  function toggleEmpty(hasItems) { 
    if (empty) empty.hidden = hasItems; 
  }

  async function loadEvents(query = '') {
    if (!ul) return;
    
    try {
      const res = await fetch(`/api/eventos/${query}`);
      if (!res.ok) throw new Error('Error al cargar eventos');
      
      const data = await res.json();
      const items = (data.results || []);
      ul.innerHTML = items.map(liTemplate).join('');
      toggleEmpty(items.length > 0);
    } catch (error) {
      console.error('Error loading events:', error);
      ul.innerHTML = '<li class="error">Error al cargar eventos</li>';
      toggleEmpty(false);
    }
  }

  // Crear evento
  const formNuevo = document.getElementById('form-nuevo');
  if (formNuevo) {
    formNuevo.addEventListener('submit', async (ev) => {
      ev.preventDefault();
      
      const titulo = document.getElementById('titulo').value.trim();
      const fechaInput = document.getElementById('fecha').value;
      const descripcion = document.getElementById('desc').value.trim();

      if (!titulo || !fechaInput) {
        alert('Título y fecha son obligatorios.');
        return;
      }

      const payload = {
        titulo: titulo,
        fecha: fechaInput,
        descripcion: descripcion,
        color: '#3A8DFF',
        todo_el_dia: true
      };

      try {
        const res = await fetch('/api/eventos/', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json', 
            'X-CSRFToken': csrftoken 
          },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          formNuevo.reset();
          await loadEvents();
          await loadMonth();
          // Actualizar próximos eventos en el dashboard
          if (window.updateProximosEventos) {
            window.updateProximosEventos();
          }
        } else {
          const errorText = await res.text();
          alert(`Error: ${errorText}`);
        }
      } catch (error) {
        console.error('Error creating event:', error);
        alert('Error al crear el evento');
      }
    });
  }

  // ====== CALENDARIO MENSUAL ======
  async function loadMonth() {
    if (!monthGrid) return;
    
    const start = mondayOfWeek(firstDayOfMonth(current));
    const end = sundayOfWeek(lastDayOfMonth(current));

    try {
      const res = await fetch(`/api/eventos/?start=${fmt(start)}&end=${fmt(end)}`);
      if (!res.ok) throw new Error('Error al cargar mes');
      
      const data = await res.json();
      const eventsMap = new Map();
      
      for (const e of (data.results || [])) {
        const key = e.fecha;
        if (!eventsMap.has(key)) eventsMap.set(key, []);
        eventsMap.get(key).push(e);
      }

      if (monthLabelEl) monthLabelEl.textContent = monthLabel(current);

      // Mantener encabezados y limpiar días
      while (monthGrid.children.length > 7) {
        monthGrid.removeChild(monthGrid.lastChild);
      }

      const today = new Date().toDateString();
      
      // Generar días del calendario
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        const cell = document.createElement('div');
        cell.className = 'day' + (d.getMonth() !== current.getMonth() ? ' out' : '');
        
        if (d.toDateString() === today) {
          cell.classList.add('today');
        }

        const dateHead = document.createElement('div');
        dateHead.className = 'date';
        dateHead.textContent = d.getDate();
        cell.appendChild(dateHead);

        const dateStr = fmt(d);
        const dayEvents = eventsMap.get(dateStr) || [];

        dayEvents.forEach(ev => {
          const eventElement = document.createElement('div');
          eventElement.className = 'event-pill';
          eventElement.innerHTML = `
            <span class="dot" style="background:${ev.color || '#3A8DFF'}"></span>
            ${ev.titulo}
          `;
          eventElement.title = ev.descripcion || ev.titulo;
          
          // Solo permitir edición si el usuario tiene permisos
          eventElement.addEventListener('click', () => {
            if (confirm(`¿Editar evento: ${ev.titulo}?`)) {
              const nuevoTitulo = prompt('Nuevo título:', ev.titulo);
              if (nuevoTitulo && nuevoTitulo.trim()) {
                updateEvent(ev.id, { ...ev, titulo: nuevoTitulo.trim() });
              }
            }
          });
          
          cell.appendChild(eventElement);
        });

        monthGrid.appendChild(cell);
      }
    } catch (error) {
      console.error('Error loading month:', error);
      monthGrid.innerHTML += '<div class="error">Error al cargar calendario</div>';
    }
  }

  async function updateEvent(id, payload) {
    try {
      const res = await fetch(`/api/eventos/${id}/`, {
        method: 'PUT',
        headers: { 
          'Content-Type': 'application/json', 
          'X-CSRFToken': csrftoken 
        },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        await loadMonth();
        await loadEvents();
      } else {
        alert('Error al actualizar evento');
      }
    } catch (error) {
      console.error('Error updating event:', error);
      alert('Error al actualizar evento');
    }
  }

  // Eliminar evento desde la lista
  if (ul) {
    ul.addEventListener('click', async (ev) => {
      const li = ev.target.closest('.item');
      if (!li) return;
      
      const id = li.dataset.id;
      const eventTitle = li.querySelector('strong').textContent;

      if (ev.target.classList.contains('del')) {
        if (!confirm(`¿Eliminar el evento "${eventTitle}"?`)) return;
        
        try {
          const res = await fetch(`/api/eventos/${id}/`, {
            method: 'DELETE', 
            headers: { 'X-CSRFToken': csrftoken }
          });
          
          if (res.ok) {
            li.remove();
            toggleEmpty(ul.children.length > 0);
            await loadMonth();
          } else {
            alert('Error al eliminar evento');
          }
        } catch (error) {
          console.error('Error deleting event:', error);
          alert('Error al eliminar evento');
        }
      }

      if (ev.target.classList.contains('edit')) {
        const currentTitle = li.querySelector('strong').textContent;
        const currentDate = li.querySelector('.date').textContent;
        const currentDesc = li.querySelector('.desc')?.textContent || '';
        
        const nuevoTitulo = prompt('Nuevo título:', currentTitle);
        if (!nuevoTitulo) return;
        
        const nuevaFecha = prompt('Nueva fecha (YYYY-MM-DD):', currentDate);
        if (!nuevaFecha) return;
        
        const nuevaDesc = prompt('Nueva descripción:', currentDesc);
        
        await updateEvent(id, {
          titulo: nuevoTitulo,
          fecha: nuevaFecha,
          descripcion: nuevaDesc
        });
      }
    });
  }

  // ====== NAVEGACIÓN Y VISTAS ======
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
    loadEvents();
  }

  // Event listeners
  tabMes?.addEventListener('click', showMes);
  tabLista?.addEventListener('click', showLista);
  prevBtn?.addEventListener('click', () => { 
    current.setMonth(current.getMonth() - 1); 
    loadMonth(); 
  });
  nextBtn?.addEventListener('click', () => { 
    current.setMonth(current.getMonth() + 1); 
    loadMonth(); 
  });
  todayBtn?.addEventListener('click', () => { 
    current = new Date(); 
    loadMonth(); 
  });

  // ====== INICIALIZACIÓN ======
  document.addEventListener('DOMContentLoaded', () => {
    const fecha = document.getElementById('fecha');
    if (fecha) {
      fecha.valueAsDate = new Date();
      fecha.min = new Date().toISOString().split('T')[0];
    }
    showMes();
    loadEvents();
  });

})();