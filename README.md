# Sistema de Gestión para Tienda de Libros

Sistema de gestión para una tienda de libros implementado como una arquitectura de microservicios con FastAPI y HTML/JavaScript.

## Características

- Gestión de Inventario (Libros)
- Gestión de Transacciones (Ventas y Abastecimientos)
- Control de Caja (Ingresos y Egresos)
- Integridad de datos mediante lógica de negocio (reemplazo de triggers)
- Interfaz web responsive

## Arquitectura

Este proyecto implementa una arquitectura de microservicios, donde:

- **Backend**: Servicios independientes que encapsulan la lógica de negocio
  - Servicio de Libros
  - Servicio de Transacciones
  - Servicio de Caja

- **Frontend**: Páginas HTML con JavaScript que consumen la API REST
  - Libros
  - Transacciones
  - Caja

- **API REST**: Endpoints para cada entidad del sistema
  - `/api/libros`
  - `/api/transacciones`
  - `/api/caja`

Para más detalles sobre la arquitectura, consulta el archivo [ARQUITECTURA.md](ARQUITECTURA.md) que contiene información detallada sobre los componentes, el flujo de datos y el reemplazo de triggers con lógica de aplicación.

## Tecnologías utilizadas

- **Backend**: 
  - FastAPI (Framework web)
  - SQLAlchemy (ORM)
  - Pydantic (Validación de datos)
  - Jinja2 (Plantillas HTML)

- **Frontend**:
  - HTML5
  - CSS3 (Bootstrap 5)
  - JavaScript (Vanilla)

## Requerimientos

- Python 3.8+
- pip

## Instalación local

1. Clonar el repositorio
```
git clone <url-del-repositorio>
cd tienda-libros
```

2. Crear un entorno virtual
```
python -m venv venv
# En Windows
venv\Scripts\activate
# En Unix/MacOS
source venv/bin/activate
```

3. Instalar dependencias
```
pip install -r requirements.txt
```

4. Ejecutar el servidor
```
uvicorn app.main:app --reload
```

5. Acceder a la aplicación
- Interfaz web: http://localhost:8000
- Documentación API: http://localhost:8000/docs

## Desarrollo

Para información detallada sobre el proceso de desarrollo, la estructura del proyecto y los cambios realizados, consulta el archivo [DESARROLLO.md](DESARROLLO.md).

## Despliegue en Render

Este proyecto está diseñado para ser desplegado fácilmente en [Render](https://render.com/), un servicio de hosting moderno.

### Pasos para el despliegue

1. Crear una cuenta en Render (https://render.com/)

2. Crear un nuevo servicio web:
   - Desde el dashboard, haga clic en "New" y seleccione "Web Service"
   - Conecte su repositorio de GitHub/GitLab
   - Seleccione el repositorio de este proyecto

3. Configure el servicio:
   - **Nombre**: `tienda-libros` (o el nombre que prefiera)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: Render usará automáticamente el comando definido en `Procfile`
   - **Plan**: Free (para pruebas) o un plan de pago para producción

4. Configurar variables de entorno (opcional):
   - `DATABASE_URL`: URL de la base de datos (por defecto usa SQLite)

5. Hacer clic en "Create Web Service"

### Notas importantes sobre Render

- **Procfile**: El archivo `Procfile` contiene el comando para iniciar la aplicación en producción:
  ```
  web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}
  ```

- **Base de datos**: La versión gratuita de Render utiliza almacenamiento efímero, lo que significa que la base de datos SQLite se restablecerá periódicamente. Para producción, configure una base de datos externa como PostgreSQL.

- **Migración de Database con Triggers**: Este proyecto implementa la lógica de integridad referencial y actualización de datos a nivel de aplicación mediante servicios, lo que elimina la necesidad de triggers de base de datos y facilita el despliegue en servicios cloud.

## Estructura del proyecto

```
tienda_libros_api/
├── app/
│   ├── models/        # Modelos de la base de datos
│   ├── routers/       # Rutas de la API
│   ├── schemas/       # Esquemas de validación (Pydantic)
│   ├── services/      # Servicios con lógica de negocio
│   ├── static/        # Archivos estáticos (CSS, JS)
│   │   ├── css/       # Estilos CSS
│   │   └── js/        # Scripts JavaScript
│   ├── templates/     # Plantillas HTML para la interfaz web
│   ├── database.py    # Configuración de la base de datos
│   ├── dependencies.py # Dependencias para inyección
│   └── main.py        # Punto de entrada de la aplicación
├── .env               # Variables de entorno (no incluir en el control de versiones)
├── ARQUITECTURA.md    # Descripción detallada de la arquitectura
├── DESARROLLO.md      # Documentación del desarrollo y cambios
├── requirements.txt   # Dependencias del proyecto
└── README.md          # Documentación principal
```

## Contribución

Para contribuir al proyecto:

1. Haga un fork del repositorio
2. Cree una rama para su característica (`git checkout -b feature/nueva-caracteristica`)
3. Realice sus cambios y haga commit (`git commit -am 'Agregar nueva característica'`)
4. Haga push a la rama (`git push origin feature/nueva-caracteristica`)
5. Cree un nuevo Pull Request

## Licencia

[MIT](https://choosealicense.com/licenses/mit/) 