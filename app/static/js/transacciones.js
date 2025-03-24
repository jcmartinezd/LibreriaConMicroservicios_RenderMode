/**
 * Funcionalidad específica para la gestión de transacciones
 */

// Variables globales
let libros = [];
let transacciones = [];
let libroSeleccionado = null;

// Función para cargar los libros (para el selector)
async function cargarLibros() {
    try {
        // Realizar petición a la API
        libros = await fetchApi('/api/libros');
        
        // Actualizar el selector de libros
        actualizarSelectorLibros(libros);
    } catch (error) {
        console.error('Error al cargar libros:', error);
        mostrarAlerta('Error al cargar el catálogo de libros', 'danger');
    }
}

// Función para actualizar el selector de libros
function actualizarSelectorLibros(libros) {
    const selector = document.querySelector('#isbn');
    
    if (!libros || libros.length === 0) {
        selector.innerHTML = `<option value="">No hay libros disponibles</option>`;
        return;
    }
    
    // Opción por defecto
    selector.innerHTML = `<option value="">Seleccione un libro</option>`;
    
    // Agregar opciones de libros
    libros.forEach(libro => {
        const option = document.createElement('option');
        option.value = libro.isbn;
        option.textContent = `${libro.isbn} - ${libro.titulo}`;
        selector.appendChild(option);
    });
}

// Función para mostrar información del libro seleccionado
function mostrarInfoLibro() {
    const isbn = document.querySelector('#isbn').value;
    const infoContainer = document.querySelector('#infoLibro');
    const tipoTransaccion = document.querySelector('#tipo_transaccion').value;
    
    if (!isbn) {
        infoContainer.innerHTML = `<p class="text-muted">Seleccione un libro para ver su información</p>`;
        libroSeleccionado = null;
        return;
    }
    
    // Buscar el libro en la lista
    libroSeleccionado = libros.find(l => l.isbn === isbn);
    
    if (!libroSeleccionado) {
        infoContainer.innerHTML = `<p class="text-danger">Libro no encontrado</p>`;
        return;
    }
    
    // Mostrar información del libro
    infoContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">${libroSeleccionado.titulo}</h5>
                <p class="card-text">
                    <strong>ISBN:</strong> ${libroSeleccionado.isbn}<br>
                    <strong>Precio de compra:</strong> ${formatoMoneda(libroSeleccionado.precio_compra)}<br>
                    <strong>Precio de venta:</strong> ${formatoMoneda(libroSeleccionado.precio_venta)}<br>
                    <strong>Stock actual:</strong> 
                    <span class="${libroSeleccionado.cantidad_actual < 5 ? 'text-danger' : 'text-success'}">
                        ${libroSeleccionado.cantidad_actual} unidades
                    </span>
                </p>
            </div>
        </div>
    `;
    
    // Actualizar mensaje de alerta según el tipo de transacción
    const alertInfo = document.querySelector('#alertInfo');
    
    if (tipoTransaccion === '1') { // Venta
        if (libroSeleccionado.cantidad_actual <= 0) {
            alertInfo.innerHTML = `
                <div class="alert alert-danger">
                    No hay unidades disponibles para vender.
                </div>
            `;
        } else {
            alertInfo.innerHTML = `
                <div class="alert alert-info">
                    Al registrar esta venta, se disminuirá el inventario y se registrará un ingreso en caja.
                </div>
            `;
        }
    } else if (tipoTransaccion === '2') { // Abastecimiento
        alertInfo.innerHTML = `
            <div class="alert alert-info">
                Al registrar este abastecimiento, se aumentará el inventario y se registrará un egreso en caja.
            </div>
        `;
    } else {
        alertInfo.innerHTML = '';
    }
}

// Función para cargar transacciones
async function cargarTransacciones() {
    try {
        // Mostrar spinner de carga
        document.querySelector('#tablaTransacciones tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </td>
            </tr>
        `;

        // Realizar petición a la API
        transacciones = await fetchApi('/api/transacciones');
        
        // Actualizar la tabla
        actualizarTablaTransacciones(transacciones);
    } catch (error) {
        console.error('Error al cargar transacciones:', error);
        document.querySelector('#tablaTransacciones tbody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    Error al cargar las transacciones. Intente nuevamente.
                </td>
            </tr>
        `;
    }
}

// Función para actualizar la tabla de transacciones
function actualizarTablaTransacciones(transacciones) {
    const tbody = document.querySelector('#tablaTransacciones tbody');
    
    if (!transacciones || transacciones.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    No hay transacciones registradas. Registre una nueva.
                </td>
            </tr>
        `;
        return;
    }
    
    // Generar filas de la tabla
    tbody.innerHTML = transacciones.map(transaccion => `
        <tr class="transaction-item ${transaccion.tipo_transaccion === 1 ? 'sale' : 'restock'}">
            <td>${transaccion.id_transaccion}</td>
            <td>${transaccion.isbn}</td>
            <td>${transaccion.titulo_libro || 'N/A'}</td>
            <td>${transaccion.tipo_transaccion === 1 ? 'Venta' : 'Abastecimiento'}</td>
            <td>${transaccion.cantidad}</td>
            <td>${formatoMoneda(transaccion.tipo_transaccion === 1 ? 
                (transaccion.cantidad * transaccion.precio_venta) : 
                (transaccion.cantidad * transaccion.precio_compra))}</td>
            <td>${formatoFecha(transaccion.fecha_transaccion)}</td>
        </tr>
    `).join('');
}

// Función para registrar una nueva transacción
async function registrarTransaccion(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Validar el formulario
    if (!validarFormulario(form)) {
        return;
    }
    
    // Validaciones adicionales
    const tipoTransaccion = parseInt(form.tipo_transaccion.value);
    const cantidad = parseInt(form.cantidad.value);
    
    if (tipoTransaccion === 1 && libroSeleccionado && cantidad > libroSeleccionado.cantidad_actual) {
        mostrarAlerta(`No hay suficiente stock disponible. Máximo: ${libroSeleccionado.cantidad_actual} unidades`, 'danger');
        return;
    }
    
    // Obtener datos del formulario
    const transaccionData = {
        isbn: form.isbn.value,
        tipo_transaccion: tipoTransaccion,
        cantidad: cantidad,
        precio_venta: libroSeleccionado ? libroSeleccionado.precio_venta : 0,
        precio_compra: libroSeleccionado ? libroSeleccionado.precio_compra : 0
    };
    
    try {
        // Crear nueva transacción
        const response = await fetchApi(
            '/api/transacciones',
            crearOpcionesFetch('POST', transaccionData)
        );
        
        // Mostrar mensaje de éxito
        mostrarAlerta(
            tipoTransaccion === 1 
                ? 'Venta registrada correctamente' 
                : 'Abastecimiento registrado correctamente', 
            'success'
        );
        
        // Recargar libros y transacciones
        await Promise.all([cargarLibros(), cargarTransacciones()]);
        
        // Limpiar formulario
        resetearFormulario(form);
        document.querySelector('#infoLibro').innerHTML = '';
        document.querySelector('#alertInfo').innerHTML = '';
    } catch (error) {
        console.error('Error al registrar transacción:', error);
    }
}

// Función para filtrar transacciones
async function filtrarTransacciones() {
    const isbnFiltro = document.querySelector('#isbnFiltro').value;
    const tipoFiltro = document.querySelector('#tipoFiltro').value;
    
    try {
        let url = '/api/transacciones';
        const params = [];
        
        // Construir la URL con parámetros de filtro
        if (isbnFiltro) {
            url = `/api/transacciones/libro/${isbnFiltro}`;
        }
        
        if (tipoFiltro) {
            params.push(`tipo_transaccion=${tipoFiltro}`);
        }
        
        if (params.length > 0) {
            url += `?${params.join('&')}`;
        }
        
        // Realizar petición a la API
        const transaccionesFiltradas = await fetchApi(url);
        
        // Actualizar la tabla
        actualizarTablaTransacciones(transaccionesFiltradas);
    } catch (error) {
        console.error('Error al filtrar transacciones:', error);
        mostrarAlerta('Error al aplicar filtros', 'danger');
    }
}

// Función para limpiar filtros
async function limpiarFiltros() {
    document.querySelector('#isbnFiltro').value = '';
    document.querySelector('#tipoFiltro').value = '';
    await cargarTransacciones();
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', () => {
    // Cargar datos iniciales
    cargarLibros();
    cargarTransacciones();
    
    // Configurar listeners de eventos
    const formTransaccion = document.querySelector('#formTransaccion');
    if (formTransaccion) {
        formTransaccion.addEventListener('submit', registrarTransaccion);
    }
    
    const selectorLibro = document.querySelector('#isbn');
    if (selectorLibro) {
        selectorLibro.addEventListener('change', mostrarInfoLibro);
    }
    
    const selectorTipo = document.querySelector('#tipo_transaccion');
    if (selectorTipo) {
        selectorTipo.addEventListener('change', mostrarInfoLibro);
    }
    
    const btnFiltrar = document.querySelector('#btnFiltrar');
    if (btnFiltrar) {
        btnFiltrar.addEventListener('click', filtrarTransacciones);
    }
    
    const btnLimpiarFiltros = document.querySelector('#btnLimpiarFiltros');
    if (btnLimpiarFiltros) {
        btnLimpiarFiltros.addEventListener('click', limpiarFiltros);
    }
}); 