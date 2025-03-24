from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .database import engine
from . import models
from .models import models as models_file
from .routers import libros, transacciones, caja, web

# Crear las tablas en la base de datos
models_file.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Tienda de Libros API",
    description="API para gestionar una tienda de libros",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(web.router)  # Router para páginas web
app.include_router(libros.router)  # API de libros
app.include_router(transacciones.router)  # API de transacciones
app.include_router(caja.router)  # API de caja

@app.get("/api")
async def root():
    """
    Endpoint de bienvenida a la API
    
    Retorna un mensaje de bienvenida con información básica sobre la API.
    """
    return {
        "mensaje": "Bienvenido a la API de Tienda de Libros",
        "version": "1.0.0",
        "documentacion": "/docs",
        "endpoints": {
            "libros": "/api/libros",
            "transacciones": "/api/transacciones",
            "caja": "/api/caja"
        }
    }