/**
 * Funcionalidad específica para la gestión de libros
 */

// Variables globales
let libroEditando = null;
let libros = [];

// Función para cargar los libros
async function cargarLibros() {
    try {
        // Mostrar spinner de carga
        document.querySelector('#tablaLibros tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </td>
            </tr>
        `;

        // Realizar petición a la API
        libros = await fetchApi('/api/libros');
        
        // Actualizar la tabla
        actualizarTablaLibros(libros);
    } catch (error) {
        console.error('Error al cargar libros:', error);
        document.querySelector('#tablaLibros tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    Error al cargar los libros. Intente nuevamente.
                </td>
            </tr>
        `;
    }
}

// Función para actualizar la tabla de libros
function actualizarTablaLibros(libros) {
    const tbody = document.querySelector('#tablaLibros tbody');
    
    if (!libros || libros.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    No hay libros registrados. Agregue uno nuevo.
                </td>
            </tr>
        `;
        return;
    }
    
    // Generar filas de la tabla
    tbody.innerHTML = libros.map(libro => `
        <tr>
            <td>${libro.isbn}</td>
            <td>${libro.titulo}</td>
            <td>${formatoMoneda(libro.precio_compra)}</td>
            <td>${formatoMoneda(libro.precio_venta)}</td>
            <td>${libro.cantidad_actual}</td>
            <td class="text-end">
                <button class="btn btn-sm btn-outline-primary" onclick="editarLibro('${libro.isbn}')">
                    <i class="bi bi-pencil"></i> Editar
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="confirmarEliminarLibro('${libro.isbn}')">
                    <i class="bi bi-trash"></i> Eliminar
                </button>
            </td>
        </tr>
    `).join('');
}

// Función para preparar la creación de un nuevo libro
function nuevoLibro() {
    // Limpiar formulario y establecer modo
    resetearFormulario(document.querySelector('#formLibro'));
    libroEditando = null;
    
    // Habilitar el campo ISBN (en edición está deshabilitado)
    document.querySelector('#isbn').disabled = false;
    
    // Cambiar título y botón del formulario
    document.querySelector('#tituloFormulario').textContent = 'Registrar Nuevo Libro';
    document.querySelector('#btnGuardarLibro').textContent = 'Registrar Libro';
    
    // Mostrar el formulario
    document.querySelector('#colFormulario').classList.remove('d-none');
    document.querySelector('#formLibro').scrollIntoView({ behavior: 'smooth' });
}

// Función para editar un libro existente
async function editarLibro(isbn) {
    try {
        // Buscar el libro en la lista cargada
        const libro = libros.find(l => l.isbn === isbn);
        
        if (!libro) {
            // Si no está en la lista, obtenerlo de la API
            libro = await fetchApi(`/api/libros/${isbn}`);
        }
        
        // Guardar referencia del libro que se está editando
        libroEditando = libro;
        
        // Llenar el formulario con los datos del libro
        const form = document.querySelector('#formLibro');
        form.isbn.value = libro.isbn;
        form.isbn.disabled = true; // El ISBN no se puede modificar
        form.titulo.value = libro.titulo;
        form.precio_compra.value = libro.precio_compra;
        form.precio_venta.value = libro.precio_venta;
        form.cantidad_actual.value = libro.cantidad_actual;
        
        // Cambiar título y botón del formulario
        document.querySelector('#tituloFormulario').textContent = 'Editar Libro';
        document.querySelector('#btnGuardarLibro').textContent = 'Guardar Cambios';
        
        // Mostrar el formulario
        document.querySelector('#colFormulario').classList.remove('d-none');
        form.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('Error al cargar libro para editar:', error);
        mostrarAlerta('No se pudo cargar el libro para editar', 'danger');
    }
}

// Función para guardar un libro (crear o actualizar)
async function guardarLibro(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Validar el formulario
    if (!validarFormulario(form)) {
        return;
    }
    
    // Obtener datos del formulario
    const libroData = {
        isbn: form.isbn.value,
        titulo: form.titulo.value,
        precio_compra: parseFloat(form.precio_compra.value),
        precio_venta: parseFloat(form.precio_venta.value),
        cantidad_actual: parseInt(form.cantidad_actual.value)
    };
    
    try {
        let response;
        
        if (libroEditando) {
            // Actualizar libro existente
            response = await fetchApi(
                `/api/libros/${libroEditando.isbn}`,
                crearOpcionesFetch('PUT', libroData)
            );
            mostrarAlerta('Libro actualizado correctamente', 'success');
        } else {
            // Crear nuevo libro
            response = await fetchApi(
                '/api/libros',
                crearOpcionesFetch('POST', libroData)
            );
            mostrarAlerta('Libro registrado correctamente', 'success');
        }
        
        // Recargar la lista de libros
        await cargarLibros();
        
        // Ocultar el formulario
        document.querySelector('#colFormulario').classList.add('d-none');
        resetearFormulario(form);
    } catch (error) {
        console.error('Error al guardar libro:', error);
    }
}

// Función para confirmar eliminación
function confirmarEliminarLibro(isbn) {
    if (confirm(`¿Está seguro de eliminar el libro con ISBN ${isbn}?`)) {
        eliminarLibro(isbn);
    }
}

// Función para eliminar un libro
async function eliminarLibro(isbn) {
    try {
        await fetchApi(`/api/libros/${isbn}`, crearOpcionesFetch('DELETE'));
        
        mostrarAlerta('Libro eliminado correctamente', 'success');
        
        // Recargar la lista de libros
        await cargarLibros();
    } catch (error) {
        console.error('Error al eliminar libro:', error);
    }
}

// Función para cancelar la edición/creación
function cancelarEdicion() {
    document.querySelector('#colFormulario').classList.add('d-none');
    resetearFormulario(document.querySelector('#formLibro'));
    libroEditando = null;
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', () => {
    // Cargar libros iniciales
    cargarLibros();
    
    // Configurar listeners de eventos
    const formLibro = document.querySelector('#formLibro');
    if (formLibro) {
        formLibro.addEventListener('submit', guardarLibro);
    }
    
    const btnNuevoLibro = document.querySelector('#btnNuevoLibro');
    if (btnNuevoLibro) {
        btnNuevoLibro.addEventListener('click', nuevoLibro);
    }
    
    const btnCancelar = document.querySelector('#btnCancelar');
    if (btnCancelar) {
        btnCancelar.addEventListener('click', cancelarEdicion);
    }
}); 