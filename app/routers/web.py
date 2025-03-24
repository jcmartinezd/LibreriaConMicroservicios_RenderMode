from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Definir la ubicación de las plantillas
templates_path = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter(
    prefix="",
    tags=["web"],
)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Renderiza la página principal
    
    Este endpoint sirve la página principal del sistema con una descripción
    general y acceso a todas las funcionalidades.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/libros", response_class=HTMLResponse)
async def libros_page(request: Request):
    """
    Renderiza la página de gestión de libros
    
    Esta interfaz permite realizar operaciones CRUD sobre el inventario de libros.
    Los datos se cargan dinámicamente mediante llamadas a la API REST.
    """
    return templates.TemplateResponse("libros.html", {"request": request})

@router.get("/transacciones", response_class=HTMLResponse)
async def transacciones_page(request: Request):
    """
    Renderiza la página de gestión de transacciones
    
    Esta interfaz permite registrar ventas y abastecimientos, así como
    ver el historial de transacciones con varios filtros.
    """
    return templates.TemplateResponse("transacciones.html", {"request": request})

@router.get("/caja", response_class=HTMLResponse)
async def caja_page(request: Request):
    """
    Renderiza la página de gestión de caja
    
    Esta interfaz muestra el saldo actual, ingresos, egresos y el historial
    de movimientos. También permite registrar movimientos manuales.
    """
    return templates.TemplateResponse("caja.html", {"request": request}) 