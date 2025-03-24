from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from fastapi import HTTPException, status

def get_transaccion(db: Session, id_transaccion: int):
    return db.query(models.Transaccion).filter(models.Transaccion.id_transaccion == id_transaccion).first()

def get_transacciones(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Transaccion).offset(skip).limit(limit).all()

def get_transacciones_by_libro(db: Session, ISBN: str):
    return db.query(models.Transaccion).filter(models.Transaccion.ISBN == ISBN).all()

def create_transaccion(db: Session, transaccion: schemas.TransaccionCreate):
    # Verificar que el libro existe
    libro = db.query(models.Libro).filter(models.Libro.ISBN == transaccion.ISBN).first()
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
        
    # Verificar que el tipo de transacción es válido
    tipo = db.query(models.TipoTransaccion).filter(models.TipoTransaccion.id_tipo == transaccion.tipo_transaccion).first()
    if not tipo:
        raise HTTPException(status_code=404, detail="Tipo de transacción no válido")
    
    # Verificar stock si es una venta
    if transaccion.tipo_transaccion == 1 and libro.cantidad_actual < transaccion.cantidad:
        raise HTTPException(status_code=400, detail="No hay suficiente stock disponible")
    
    # Crear la transacción
    db_transaccion = models.Transaccion(
        ISBN=transaccion.ISBN,
        tipo_transaccion=transaccion.tipo_transaccion,
        cantidad=transaccion.cantidad
    )
    
    db.add(db_transaccion)
    db.commit()
    db.refresh(db_transaccion)
    
    # Nota: No se actualizan manualmente el inventario y la caja aquí 
    # porque asumimos que los triggers de la base de datos lo harán
    
    return db_transaccion