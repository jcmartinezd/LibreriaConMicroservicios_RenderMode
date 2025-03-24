# Desarrollo del Proyecto Tienda de Libros

## Cambios Realizados

### 1. Estructura de Microservicios

Se ha implementado una arquitectura de microservicios que reemplaza los triggers de base de datos con lógica de aplicación, facilitando el despliegue en plataformas cloud como Render.

### 2. Capa de Servicios

Se crearon tres servicios principales que encapsulan la lógica de negocio:

- **LibroService**: Gestiona el catálogo de libros y las validaciones de existencias.
- **TransaccionService**: Procesa ventas y abastecimientos, actualizando inventario y caja en una sola transacción.
- **CajaService**: Controla los movimientos financieros y gestiona el saldo.

### 3. APIs REST

Se actualizaron los routers para utilizar los servicios:

- `/api/libros`: CRUD para libros
- `/api/transacciones`: Registro y consulta de transacciones
- `/api/caja`: Gestión de movimientos y consulta de saldo

### 4. Interfaz Web

Se desarrolló una interfaz web completa utilizando HTML, CSS y JavaScript:

- Pantalla principal con información de la aplicación
- Gestión de inventario de libros
- Registro y consulta de transacciones
- Control de caja con registro de ingresos y egresos manuales

### 5. Activos Estáticos

Se crearon estilos CSS personalizados y funciones JavaScript para:

- Comunicación con las APIs
- Validación de formularios
- Mejora de la experiencia de usuario

## Archivos Creados/Modificados

### Estructura Principal

- `app/main.py` - Punto de entrada de la aplicación
- `app/database.py` - Configuración de la base de datos
- `app/dependencies.py` - Dependencias de la aplicación

### Modelos y Esquemas

- `app/models/models.py` - Definición de modelos SQLAlchemy
- `app/schemas/schemas.py` - Esquemas Pydantic para validación

### Servicios

- `app/services/__init__.py` - Inicializador del paquete de servicios
- `app/services/libro_service.py` - Servicio para libros
- `app/services/transaccion_service.py` - Servicio para transacciones
- `app/services/caja_service.py` - Servicio para caja

### Routers

- `app/routers/libros.py` - Router para libros
- `app/routers/transacciones.py` - Router para transacciones
- `app/routers/caja.py` - Router para caja
- `app/routers/web.py` - Router para las páginas web

### Plantillas

- `app/templates/index.html` - Página principal
- `app/templates/libros.html` - Gestión de libros
- `app/templates/transacciones.html` - Registro y consulta de transacciones
- `app/templates/caja.html` - Control de caja

### Estáticos

- `app/static/css/custom.css` - Estilos personalizados
- `app/static/js/app.js` - Funciones generales
- `app/static/js/libros.js` - JavaScript para libros
- `app/static/js/transacciones.js` - JavaScript para transacciones
- `app/static/js/caja.js` - JavaScript para caja

### Documentación

- `README.md` - Documentación principal
- `ARQUITECTURA.md` - Explicación de la arquitectura
- `DESARROLLO.md` - Este archivo

## Mejoras Implementadas

1. **Reemplazo de Triggers**: Los triggers de base de datos fueron reemplazados por lógica de aplicación en los servicios, lo que mejora la portabilidad y el despliegue en plataformas cloud.

2. **Validaciones Mejoradas**: Se implementaron validaciones de negocio en los servicios, como verificar que el precio de venta no sea menor al precio de compra o que haya suficiente stock para una venta.

3. **Transacciones Atómicas**: Las operaciones relacionadas con transacciones se realizan dentro de una transacción de base de datos para mantener la integridad.

4. **Interfaz Responsive**: La interfaz web utiliza Bootstrap para adaptarse a diferentes dispositivos.

5. **API REST Bien Documentada**: Todos los endpoints están documentados con docstrings detallados.

## Próximos Pasos

1. **Implementar pruebas unitarias**: Agregar pruebas para los servicios.

2. **Autenticación y autorización**: Implementar un sistema de usuarios.

3. **Reportes**: Añadir funcionalidad para generar reportes de ventas y stock.

4. **Mejoras de UX**: Mejorar la experiencia de usuario con mejores transiciones y feedback.

5. **Despliegue**: Configurar el despliegue automático en Render. 