/**
 * Funciones generales para la aplicación Tienda de Libros
 */

// Función para mostrar mensajes de alerta
function mostrarAlerta(mensaje, tipo = 'success', contenedor = '#alertContainer', duracion = 5000) {
    const alertContainer = document.querySelector(contenedor);
    if (!alertContainer) return;

    // Crear elemento de alerta
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${tipo} alert-dismissible fade show`;
    alertElement.role = 'alert';
    
    // Contenido del mensaje
    alertElement.innerHTML = `
        ${mensaje}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
    `;
    
    // Agregar al contenedor
    alertContainer.appendChild(alertElement);
    
    // Auto-eliminar después de 'duracion' milisegundos
    if (duracion > 0) {
        setTimeout(() => {
            alertElement.classList.remove('show');
            setTimeout(() => alertElement.remove(), 150);
        }, duracion);
    }
}

// Función para formatear números como moneda (COP)
function formatoMoneda(valor) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(valor);
}

// Función para formatear fechas
function formatoFecha(fechaStr) {
    const fecha = new Date(fechaStr);
    return new Intl.DateTimeFormat('es-CO', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(fecha);
}

// Función para validar entrada de formularios
function validarFormulario(formulario) {
    // Marcar el formulario como validado para que se muestren los mensajes de error
    formulario.classList.add('was-validated');
    
    // Verificar validez
    return formulario.checkValidity();
}

// Función para resetear un formulario
function resetearFormulario(formulario, borrarValidacion = true) {
    formulario.reset();
    if (borrarValidacion) {
        formulario.classList.remove('was-validated');
    }
}

// Función para realizar peticiones API con manejo de errores
async function fetchApi(url, opciones = {}) {
    try {
        const response = await fetch(url, opciones);
        
        // Si la respuesta no es ok (2xx)
        if (!response.ok) {
            const error = await response.json().catch(() => ({
                detail: `Error ${response.status}: ${response.statusText}`
            }));
            
            throw new Error(error.detail || 'Error desconocido en la petición');
        }
        
        // Si la respuesta está vacía
        if (response.status === 204) {
            return null;
        }
        
        // Devolver la respuesta JSON
        return await response.json();
    } catch (error) {
        console.error('Error en petición API:', error);
        mostrarAlerta(error.message, 'danger');
        throw error;
    }
}

// Crear opciones para fetch con método, headers y body
function crearOpcionesFetch(metodo, datos = null) {
    const opciones = {
        method: metodo,
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    };
    
    if (datos && (metodo === 'POST' || metodo === 'PUT' || metodo === 'PATCH')) {
        opciones.body = JSON.stringify(datos);
    }
    
    return opciones;
}

// Función para obtener parámetros de la URL
function obtenerParametroUrl(nombre) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(nombre);
}

// Función para activar el item de navegación actual
function activarNavItem() {
    const currentPath = window.location.pathname;
    const navItems = document.querySelectorAll('.nav-link');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        if (href === currentPath) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', () => {
    // Activar item de navegación
    activarNavItem();
    
    // Inicializar tooltips de Bootstrap si existen
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}); 