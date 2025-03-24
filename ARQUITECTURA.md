# Arquitectura de Microservicios - Tienda de Libros

## Visión General

Este proyecto implementa una arquitectura de microservicios para una tienda de libros, donde cada funcionalidad principal está encapsulada en servicios independientes que se comunican a través de APIs REST.

La característica más importante de esta arquitectura es que reemplaza los triggers de base de datos con lógica de aplicación en servicios, lo que facilita el despliegue en plataformas cloud como Render.

## Componentes Principales

### 1. Capa de Servicios

Cada dominio de negocio está implementado como un servicio independiente con responsabilidades claramente definidas:

#### LibroService
- Gestión del catálogo de libros
- Validación de existencias
- Verificación de reglas de negocio (precio venta ≥ precio compra)

#### TransaccionService
- Procesamiento de ventas y abastecimientos
- **Reemplazo de triggers**: Actualiza inventario y caja en una sola transacción
- Validación de stock disponible

#### CajaService
- Control de movimientos financieros
- Gestión del saldo
- Validación de reglas de negocio (evitar saldo negativo)

### 2. Capa de API

Routers FastAPI que exponen los endpoints para cada entidad:

- `/api/libros`: CRUD para libros
- `/api/transacciones`: Registro y consulta de transacciones
- `/api/caja`: Gestión de movimientos y consulta de saldo

### 3. Capa de Modelos

Define las entidades y sus relaciones usando SQLAlchemy:

- **Libro**: Catálogo de productos
- **TipoTransaccion**: Tipos de operaciones (venta, abastecimiento)
- **Transaccion**: Registro de operaciones
- **Caja**: Movimientos financieros

### 4. Capa de Esquemas

Define los contratos de datos usando Pydantic:

- Validación de entrada
- Documentación de la API
- Transformación de datos

### 5. Capa de Presentación

Implementa la interfaz de usuario utilizando:

- HTML con Bootstrap para el diseño
- JavaScript para la interactividad
- Plantillas Jinja2 para la renderización

## Reemplazo de Triggers de Base de Datos

Una característica importante de esta arquitectura es la implementación de la lógica que tradicionalmente se maneja con triggers directamente en el código de aplicación.

### En la Base de Datos Original

```sql
-- Trigger para ventas
CREATE TRIGGER trg_Venta_Transaccion
ON Transacciones
AFTER INSERT
AS
BEGIN
    -- Lógica para actualizar inventario y caja
    UPDATE Libros
    SET cantidad_actual = cantidad_actual - @cantidad
    WHERE ISBN = @ISBN;
    
    INSERT INTO Caja (tipo_movimiento, monto, saldo_actual, id_transaccion)
    SELECT 'INGRESO', @cantidad*@precio_venta, 
    (SELECT TOP 1 saldo_actual FROM Caja ORDER BY id_movimiento DESC) + 
    (@cantidad*@precio_venta), inserted.id_transaccion 
    FROM inserted;
END;
```

### En la Arquitectura de Microservicios

```python
# TransaccionService.create_transaccion
# Reemplaza el trigger de base de datos con lógica de aplicación
if transaccion.tipo_transaccion == 1:  # VENTA
    # Actualizar inventario: restar unidades
    libro.cantidad_actual -= transaccion.cantidad
    
    # Calcular el monto de la venta
    monto_venta = transaccion.cantidad * libro.precio_venta
    
    # Registrar ingreso en caja
    db_movimiento = models.Caja(
        tipo_movimiento="INGRESO",
        monto=monto_venta,
        saldo_actual=saldo_actual + monto_venta,
        id_transaccion=db_transaccion.id_transaccion,
        fecha_movimiento=datetime.now()
    )
```

## Ventajas de esta Arquitectura

1. **Portabilidad**: Funciona en cualquier plataforma, incluso aquellas que no soportan triggers de base de datos.

2. **Testabilidad**: La lógica de negocio puede probarse independientemente de la base de datos.

3. **Separación de Responsabilidades**: Cada servicio tiene una responsabilidad clara.

4. **Mantenibilidad**: Los cambios en un servicio no afectan a otros.

5. **Visibilidad**: Toda la lógica está en código de aplicación, no oculta en la base de datos.

6. **Facilidad de Despliegue**: Especialmente en plataformas como Render que pueden tener limitaciones con triggers.

## Flujo de Datos

### Ejemplo: Proceso de Venta

1. La interfaz web en `/transacciones` recoge los datos de la venta.

2. Se envía una solicitud POST a `/api/transacciones`.

3. El router `transacciones.py` valida los datos y llama a `TransaccionService.create_transaccion()`.

4. `TransaccionService` valida reglas de negocio (stock disponible, etc).

5. En una sola transacción de base de datos:
   - Se crea el registro de transacción
   - Se actualiza el inventario (reduce stock)
   - Se registra el movimiento en caja (aumenta saldo)

6. Se devuelve el resultado al cliente.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                        Interfaz Web                          │
│  ┌──────────┐      ┌───────────────┐      ┌──────────────┐  │
│  │  Libros  │      │ Transacciones │      │     Caja     │  │
│  └────┬─────┘      └───────┬───────┘      └──────┬───────┘  │
└───────┼─────────────────────┼──────────────────────┼────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                          API REST                            │
│  ┌──────────┐      ┌───────────────┐      ┌──────────────┐  │
│  │ /libros  │      │/transacciones │      │    /caja     │  │
│  └────┬─────┘      └───────┬───────┘      └──────┬───────┘  │
└───────┼─────────────────────┼──────────────────────┼────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      Capa de Servicios                       │
│  ┌──────────┐      ┌───────────────┐      ┌──────────────┐  │
│  │  Libro   │      │  Transaccion  │      │     Caja     │  │
│  │ Service  │◄────►│    Service    │◄────►│   Service    │  │
│  └────┬─────┘      └───────┬───────┘      └──────┬───────┘  │
└───────┼─────────────────────┼──────────────────────┼────────┘
         │                     │                      │
         ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Capa de Datos (ORM)                      │
│  ┌──────────┐      ┌───────────────┐      ┌──────────────┐  │
│  │  Libro   │◄────►│  Transaccion  │◄────►│    Caja      │  │
│  │  Modelo  │      │    Modelo     │      │   Modelo     │  │
│  └──────────┘      └───────────────┘      └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                      ┌───────────────┐
                      │  Base de Datos│
                      │    SQLite     │
                      └───────────────┘
```

## Consideraciones para el Despliegue en Render

1. **Database URL**: Configurar `DATABASE_URL` en variables de entorno para usar una base de datos externa en producción.

2. **Persistencia**: Para evitar pérdida de datos en el plan gratuito, considerar el uso de bases de datos administradas.

3. **Escalabilidad**: Esta arquitectura puede escalarse horizontalmente agregando más instancias.

4. **Configuración Recomendada**:
   - Web Service: Para la API y la interfaz web
   - PostgreSQL: Para la base de datos en producción
   - Plan adecuado: Según tráfico esperado 