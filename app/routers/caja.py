from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict

from ..dependencies import get_db
from ..schemas import schemas
from ..services import CajaService

router = APIRouter(
    prefix="/api/caja",
    tags=["caja"],
    responses={404: {"description": "No encontrado"}},
)

@router.get("/", response_model=List[schemas.Caja])
def read_movimientos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene la lista de movimientos de caja
    
    Esta operación devuelve todos los movimientos registrados con paginación
    
    Parámetros:
    - skip: Número de registros a omitir (opcional, predeterminado: 0)
    - limit: Número máximo de registros a devolver (opcional, predeterminado: 100)
    
    Retorna:
    - Lista de movimientos de caja con todos sus datos
    """
    return CajaService.get_movimientos(db, skip=skip, limit=limit)

@router.get("/saldo", response_model=Dict[str, float])
def read_saldo_actual(db: Session = Depends(get_db)):
    """
    Obtiene el saldo actual de caja
    
    Esta operación devuelve el saldo disponible en caja
    
    Retorna:
    - Objeto con el saldo actual
    """
    saldo = CajaService.get_saldo_actual(db)
    return {"saldo": saldo}

@router.get("/{id_movimiento}", response_model=schemas.Caja)
def read_movimiento(id_movimiento: int, db: Session = Depends(get_db)):
    """
    Obtiene un movimiento de caja específico por su ID
    
    Esta operación busca y devuelve un movimiento según su identificador único
    
    Parámetros:
    - id_movimiento: Identificador único del movimiento
    
    Retorna:
    - El movimiento encontrado con todos sus datos
    
    Errores:
    - 404: Si no se encuentra un movimiento con ese ID
    """
    db_movimiento = CajaService.get_movimiento(db, id_movimiento=id_movimiento)
    if db_movimiento is None:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return db_movimiento

@router.post("/", response_model=schemas.Caja, status_code=status.HTTP_201_CREATED)
def create_movimiento(movimiento: schemas.CajaCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo movimiento manual en caja
    
    Esta operación registra un ingreso o egreso manual no asociado a una transacción
    
    Parámetros en el body:
    - tipo_movimiento: Tipo de movimiento ("INGRESO" o "EGRESO")
    - monto: Cantidad de dinero
    - id_transaccion: ID de transacción relacionada (opcional)
    
    Retorna:
    - El movimiento creado con todos sus datos
    
    Errores:
    - 400: Si el tipo de movimiento no es válido o no hay saldo suficiente para un egreso
    """
    return CajaService.create_movimiento_manual(db=db, movimiento=movimiento) 