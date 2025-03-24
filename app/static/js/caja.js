/**
 * Funcionalidad específica para la gestión de caja
 */

// Variables globales
let movimientos = [];
let saldoActual = 0;
let totalIngresos = 0;
let totalEgresos = 0;

// Función para cargar el saldo actual
async function cargarSaldo() {
    try {
        // Realizar petición a la API
        const respuesta = await fetchApi('/api/caja/saldo');
        saldoActual = respuesta.saldo || 0;
        
        // Actualizar el saldo en la UI
        document.querySelector('#saldoActual').textContent = formatoMoneda(saldoActual);
    } catch (error) {
        console.error('Error al cargar saldo:', error);
        mostrarAlerta('Error al cargar el saldo actual', 'danger');
    }
}

// Función para cargar los movimientos
async function cargarMovimientos() {
    try {
        // Mostrar spinner de carga
        document.querySelector('#tablaMovimientos tbody').innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                </td>
            </tr>
        `;

        // Realizar petición a la API
        movimientos = await fetchApi('/api/caja');
        
        // Calcular totales
        calcularTotales(movimientos);
        
        // Actualizar la tabla
        actualizarTablaMovimientos(movimientos);
    } catch (error) {
        console.error('Error al cargar movimientos:', error);
        document.querySelector('#tablaMovimientos tbody').innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-danger">
                    Error al cargar los movimientos. Intente nuevamente.
                </td>
            </tr>
        `;
    }
}

// Función para calcular totales
function calcularTotales(movimientos) {
    totalIngresos = 0;
    totalEgresos = 0;
    
    movimientos.forEach(movimiento => {
        if (movimiento.tipo_movimiento === 'INGRESO') {
            totalIngresos += movimiento.monto;
        } else {
            totalEgresos += movimiento.monto;
        }
    });
    
    // Actualizar UI
    document.querySelector('#totalIngresos').textContent = formatoMoneda(totalIngresos);
    document.querySelector('#totalEgresos').textContent = formatoMoneda(totalEgresos);
    document.querySelector('#resultado').textContent = formatoMoneda(totalIngresos - totalEgresos);
}

// Función para actualizar la tabla de movimientos
function actualizarTablaMovimientos(movimientos) {
    const tbody = document.querySelector('#tablaMovimientos tbody');
    
    if (!movimientos || movimientos.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">
                    No hay movimientos registrados.
                </td>
            </tr>
        `;
        return;
    }
    
    // Generar filas de la tabla
    tbody.innerHTML = movimientos.map(movimiento => `
        <tr>
            <td>${movimiento.id_movimiento}</td>
            <td>${formatoFecha(movimiento.fecha_movimiento)}</td>
            <td class="${movimiento.tipo_movimiento === 'INGRESO' ? 'text-success' : 'text-danger'}">
                ${movimiento.tipo_movimiento}
            </td>
            <td>${formatoMoneda(movimiento.monto)}</td>
            <td>${formatoMoneda(movimiento.saldo_actual)}</td>
            <td>${movimiento.id_transaccion || 'Manual'}</td>
            <td>${movimiento.descripcion || '-'}</td>
        </tr>
    `).join('');
}

// Función para preparar el modal de movimiento
function prepararMovimiento(tipo) {
    // Configurar el modal según el tipo
    const titulo = document.querySelector('#modalMovimientoLabel');
    const tipoInput = document.querySelector('#tipo_movimiento');
    const btnGuardar = document.querySelector('#btnGuardarMovimiento');
    
    if (tipo === 'INGRESO') {
        titulo.textContent = 'Registrar Ingreso';
        tipoInput.value = 'INGRESO';
        btnGuardar.classList.remove('btn-danger');
        btnGuardar.classList.add('btn-success');
        btnGuardar.textContent = 'Registrar Ingreso';
    } else {
        titulo.textContent = 'Registrar Egreso';
        tipoInput.value = 'EGRESO';
        btnGuardar.classList.remove('btn-success');
        btnGuardar.classList.add('btn-danger');
        btnGuardar.textContent = 'Registrar Egreso';
    }
    
    // Limpiar formulario
    resetearFormulario(document.querySelector('#formMovimiento'));
    
    // Mostrar el modal
    const modalMovimiento = new bootstrap.Modal(document.querySelector('#modalMovimiento'));
    modalMovimiento.show();
}

// Función para guardar un movimiento
async function guardarMovimiento(event) {
    event.preventDefault();
    
    const form = event.target;
    
    // Validar el formulario
    if (!validarFormulario(form)) {
        return;
    }
    
    // Validaciones adicionales
    const tipo = form.tipo_movimiento.value;
    const monto = parseFloat(form.monto.value);
    
    if (tipo === 'EGRESO' && monto > saldoActual) {
        mostrarAlerta('No hay suficiente saldo para este egreso', 'danger');
        return;
    }
    
    // Obtener datos del formulario
    const movimientoData = {
        tipo_movimiento: tipo,
        monto: monto,
        descripcion: form.descripcion.value || (tipo === 'INGRESO' ? 'Ingreso manual' : 'Egreso manual')
    };
    
    try {
        // Crear nuevo movimiento
        const response = await fetchApi(
            '/api/caja',
            crearOpcionesFetch('POST', movimientoData)
        );
        
        // Cerrar el modal
        const modalMovimiento = bootstrap.Modal.getInstance(document.querySelector('#modalMovimiento'));
        modalMovimiento.hide();
        
        // Mostrar mensaje de éxito
        mostrarAlerta(
            tipo === 'INGRESO' 
                ? 'Ingreso registrado correctamente' 
                : 'Egreso registrado correctamente', 
            'success'
        );
        
        // Recargar datos
        await Promise.all([cargarSaldo(), cargarMovimientos()]);
    } catch (error) {
        console.error('Error al registrar movimiento:', error);
    }
}

// Inicializar cuando el DOM está cargado
document.addEventListener('DOMContentLoaded', () => {
    // Cargar datos iniciales
    cargarSaldo();
    cargarMovimientos();
    
    // Configurar listeners de eventos
    const formMovimiento = document.querySelector('#formMovimiento');
    if (formMovimiento) {
        formMovimiento.addEventListener('submit', guardarMovimiento);
    }
    
    const btnIngreso = document.querySelector('#btnIngreso');
    if (btnIngreso) {
        btnIngreso.addEventListener('click', () => prepararMovimiento('INGRESO'));
    }
    
    const btnEgreso = document.querySelector('#btnEgreso');
    if (btnEgreso) {
        btnEgreso.addEventListener('click', () => prepararMovimiento('EGRESO'));
    }
}); 