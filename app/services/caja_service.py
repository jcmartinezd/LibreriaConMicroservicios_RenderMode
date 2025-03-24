from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional, Dict

class CajaService:
    """
    Servicio para gestionar las operaciones de caja.
    Implementa la lógica de negocio relacionada con los movimientos financieros.
    """
    
    @staticmethod
    def get_movimiento(db: Session, id_movimiento: int) -> Optional[models.Caja]:
        """
        Obtiene un movimiento por su ID.
        
        Args:
            db (Session): Sesión de base de datos
            id_movimiento (int): ID del movimiento a buscar
            
        Returns:
            Optional[models.Caja]: El movimiento encontrado o None
            
        Raises:
            HTTPException: Si el movimiento no existe
        """
        db_movimiento = db.query(models.Caja).filter(
            models.Caja.id_movimiento == id_movimiento
        ).first()
        
        if not db_movimiento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un movimiento con el ID {id_movimiento}"
            )
            
        return db_movimiento
    
    @staticmethod
    def get_movimientos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Caja]:
        """
        Obtiene la lista de movimientos de caja con paginación.
        
        Args:
            db (Session): Sesión de base de datos
            skip (int): Número de registros a omitir
            limit (int): Número máximo de registros a retornar
            
        Returns:
            List[models.Caja]: Lista de movimientos
        """
        return db.query(models.Caja).order_by(
            models.Caja.fecha_movimiento.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_saldo_actual(db: Session) -> Dict[str, float]:
        """
        Obtiene el saldo actual de caja.
        
        Args:
            db (Session): Sesión de base de datos
            
        Returns:
            Dict[str, float]: Saldo actual formateado como diccionario
        """
        # Obtener el último movimiento para conocer el saldo actual
        ultimo_movimiento = db.query(models.Caja).order_by(
            models.Caja.id_movimiento.desc()
        ).first()
        
        saldo = 0
        if ultimo_movimiento:
            saldo = ultimo_movimiento.saldo_actual
        
        return {"saldo": saldo}
    
    @staticmethod
    def create_movimiento(db: Session, movimiento: schemas.CajaCreate) -> models.Caja:
        """
        Crea un nuevo movimiento de caja manual.
        
        Args:
            db (Session): Sesión de base de datos
            movimiento (schemas.CajaCreate): Datos del movimiento a crear
            
        Returns:
            models.Caja: El movimiento creado
            
        Raises:
            HTTPException: Si hay errores de validación o falla la operación
        """
        # Validaciones básicas
        if movimiento.monto <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto debe ser mayor que cero"
            )
        
        # Obtener el saldo actual
        ultimo_movimiento = db.query(models.Caja).order_by(
            models.Caja.id_movimiento.desc()
        ).first()
        
        saldo_actual = 0
        if ultimo_movimiento:
            saldo_actual = ultimo_movimiento.saldo_actual
        
        # Validar saldo suficiente en caso de egreso
        if movimiento.tipo_movimiento == "EGRESO" and movimiento.monto > saldo_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Saldo insuficiente. Disponible: {saldo_actual}, Solicitado: {movimiento.monto}"
            )
        
        # Calcular nuevo saldo
        nuevo_saldo = saldo_actual
        if movimiento.tipo_movimiento == "INGRESO":
            nuevo_saldo += movimiento.monto
        else:
            nuevo_saldo -= movimiento.monto
        
        # Crear el movimiento
        db_movimiento = models.Caja(
            tipo_movimiento=movimiento.tipo_movimiento,
            monto=movimiento.monto,
            saldo_actual=nuevo_saldo,
            descripcion=movimiento.descripcion,
            fecha_movimiento=datetime.now()
        )
        
        try:
            db.add(db_movimiento)
            db.commit()
            db.refresh(db_movimiento)
            return db_movimiento
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al registrar el movimiento: {str(e)}"
            ) 