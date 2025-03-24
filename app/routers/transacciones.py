from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db
from ..schemas import schemas
from ..services import TransaccionService

router = APIRouter(
    prefix="/api/transacciones",
    tags=["transacciones"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=schemas.Transaccion, status_code=status.HTTP_201_CREATED)
def create_transaccion(transaccion: schemas.TransaccionCreate, db: Session = Depends(get_db)):
    """
    Registra una nueva transacción (venta o abastecimiento)
    
    Esta operación registra una transacción y actualiza automáticamente el inventario y la caja.
    
    Tipos de transacción:
    - 1: Venta (disminuye inventario, aumenta caja)
    - 2: Abastecimiento (aumenta inventario, disminuye caja)
    
    Parámetros en el body:
    - ISBN: Identificador del libro
    - tipo_transaccion: Tipo de transacción (1: Venta, 2: Abastecimiento)
    - cantidad: Número de unidades
    
    Retorna:
    - La transacción creada con todos sus datos
    
    Errores:
    - 404: Si no se encuentra el libro o el tipo de transacción
    - 400: Si no hay suficiente stock para una venta
    """
    return TransaccionService.create_transaccion(db=db, transaccion=transaccion)

@router.get("/", response_model=List[schemas.Transaccion])
def read_transacciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene la lista de transacciones
    
    Esta operación devuelve todas las transacciones registradas con paginación
    
    Parámetros:
    - skip: Número de registros a omitir (opcional, predeterminado: 0)
    - limit: Número máximo de registros a devolver (opcional, predeterminado: 100)
    
    Retorna:
    - Lista de transacciones con todos sus datos
    """
    return TransaccionService.get_transacciones(db, skip=skip, limit=limit)

@router.get("/{id_transaccion}", response_model=schemas.Transaccion)
def read_transaccion(id_transaccion: int, db: Session = Depends(get_db)):
    """
    Obtiene una transacción específica por su ID
    
    Esta operación busca y devuelve una transacción según su identificador único
    
    Parámetros:
    - id_transaccion: Identificador único de la transacción
    
    Retorna:
    - La transacción encontrada con todos sus datos
    
    Errores:
    - 404: Si no se encuentra una transacción con ese ID
    """
    db_transaccion = TransaccionService.get_transaccion(db, id_transaccion=id_transaccion)
    if db_transaccion is None:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    return db_transaccion

@router.get("/libro/{isbn}", response_model=List[schemas.Transaccion])
def read_transacciones_by_libro(isbn: str, db: Session = Depends(get_db)):
    """
    Obtiene las transacciones de un libro específico
    
    Esta operación devuelve todas las transacciones asociadas a un libro determinado
    
    Parámetros:
    - isbn: Identificador único del libro (ISBN)
    
    Retorna:
    - Lista de transacciones del libro
    """
    return TransaccionService.get_transacciones_by_libro(db, ISBN=isbn)