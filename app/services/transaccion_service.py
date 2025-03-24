from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from app.services.libro_service import LibroService

class TransaccionService:
    """
    Servicio para gestionar operaciones relacionadas con las transacciones.
    Este servicio implementa la lógica que reemplaza los triggers de la base de datos
    para mantener la integridad de la información entre inventario y caja.
    """
    
    @staticmethod
    def get_transaccion(db: Session, id_transaccion: int):
        """
        Obtiene una transacción por su ID
        
        Parámetros:
        - db: Sesión de la base de datos
        - id_transaccion: ID de la transacción
        
        Retorna:
        - Transacción encontrada o None si no existe
        """
        return db.query(models.Transaccion).filter(models.Transaccion.id_transaccion == id_transaccion).first()
    
    @staticmethod
    def get_transacciones(db: Session, skip: int = 0, limit: int = 100):
        """
        Obtiene una lista de transacciones con paginación
        
        Parámetros:
        - db: Sesión de la base de datos
        - skip: Número de registros a omitir (para paginación)
        - limit: Número máximo de registros a devolver
        
        Retorna:
        - Lista de transacciones
        """
        return db.query(models.Transaccion).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_transacciones_by_libro(db: Session, ISBN: str):
        """
        Obtiene las transacciones de un libro específico
        
        Parámetros:
        - db: Sesión de la base de datos
        - ISBN: Identificador único del libro
        
        Retorna:
        - Lista de transacciones del libro
        """
        return db.query(models.Transaccion).filter(models.Transaccion.ISBN == ISBN).all()
    
    @staticmethod
    def get_ultimo_saldo_caja(db: Session):
        """
        Obtiene el último saldo registrado en caja
        
        Parámetros:
        - db: Sesión de la base de datos
        
        Retorna:
        - Último saldo registrado o 0 si no hay registros
        """
        ultimo_movimiento = db.query(models.Caja).order_by(models.Caja.id_movimiento.desc()).first()
        if not ultimo_movimiento:
            return 0
        return ultimo_movimiento.saldo_actual
    
    @staticmethod
    def create_transaccion(db: Session, transaccion: schemas.TransaccionCreate) -> models.Transaccion:
        """
        Crea una nueva transacción (venta o abastecimiento).
        Este método reemplaza los triggers de BD manejando la lógica de actualización
        de inventario y caja en una sola transacción.
        
        Args:
            db (Session): Sesión de base de datos
            transaccion (schemas.TransaccionCreate): Datos de la transacción a crear
            
        Returns:
            models.Transaccion: La transacción creada
            
        Raises:
            HTTPException: Si hay errores de validación o falla la operación
        """
        # Verificar que existe el libro
        libro = db.query(models.Libro).filter(models.Libro.isbn == transaccion.isbn).first()
        if not libro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un libro con el ISBN {transaccion.isbn}"
            )
        
        # Validar la transacción según su tipo
        if transaccion.tipo_transaccion == 1:  # VENTA
            # Verificar que hay suficiente stock
            if libro.cantidad_actual < transaccion.cantidad:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente. Disponible: {libro.cantidad_actual}, Solicitado: {transaccion.cantidad}"
                )
        
        # Procesar la transacción dentro de una sola transacción de BD
        try:
            # 1. Crear el registro de transacción
            db_transaccion = models.Transaccion(
                isbn=transaccion.isbn,
                tipo_transaccion=transaccion.tipo_transaccion,
                cantidad=transaccion.cantidad,
                precio_venta=transaccion.precio_venta or libro.precio_venta,
                precio_compra=transaccion.precio_compra or libro.precio_compra,
                fecha_transaccion=datetime.now()
            )
            
            db.add(db_transaccion)
            db.flush()  # Obtener el ID generado pero sin commit todavía
            
            # 2. Actualizar el inventario
            if transaccion.tipo_transaccion == 1:  # VENTA
                # Actualizar inventario: restar unidades
                libro.cantidad_actual -= transaccion.cantidad
                
                # Calcular el monto de la venta
                monto_venta = transaccion.cantidad * libro.precio_venta
                
                # 3. Obtener el saldo actual de caja
                ultimo_movimiento = db.query(models.Caja).order_by(
                    models.Caja.id_movimiento.desc()
                ).first()
                
                saldo_actual = 0
                if ultimo_movimiento:
                    saldo_actual = ultimo_movimiento.saldo_actual
                
                # 4. Registrar ingreso en caja
                db_movimiento = models.Caja(
                    tipo_movimiento="INGRESO",
                    monto=monto_venta,
                    saldo_actual=saldo_actual + monto_venta,
                    id_transaccion=db_transaccion.id_transaccion,
                    fecha_movimiento=datetime.now()
                )
                
                db.add(db_movimiento)
                
            elif transaccion.tipo_transaccion == 2:  # ABASTECIMIENTO
                # Actualizar inventario: sumar unidades
                libro.cantidad_actual += transaccion.cantidad
                
                # Calcular el monto del abastecimiento
                monto_abastecimiento = transaccion.cantidad * libro.precio_compra
                
                # 3. Obtener el saldo actual de caja
                ultimo_movimiento = db.query(models.Caja).order_by(
                    models.Caja.id_movimiento.desc()
                ).first()
                
                saldo_actual = 0
                if ultimo_movimiento:
                    saldo_actual = ultimo_movimiento.saldo_actual
                
                # Validar que hay suficiente saldo en caja
                if monto_abastecimiento > saldo_actual:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Saldo insuficiente en caja. Disponible: {saldo_actual}, Requerido: {monto_abastecimiento}"
                    )
                
                # 4. Registrar egreso en caja
                db_movimiento = models.Caja(
                    tipo_movimiento="EGRESO",
                    monto=monto_abastecimiento,
                    saldo_actual=saldo_actual - monto_abastecimiento,
                    id_transaccion=db_transaccion.id_transaccion,
                    fecha_movimiento=datetime.now()
                )
                
                db.add(db_movimiento)
                
            # Confirmar todos los cambios
            db.commit()
            db.refresh(db_transaccion)
            
            return db_transaccion
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al procesar la transacción: {str(e)}"
            )
    
    @staticmethod
    def get_transacciones_por_libro(db: Session, isbn: str, skip: int = 0, limit: int = 100) -> List[models.Transaccion]:
        """
        Obtiene la lista de transacciones de un libro específico.
        
        Args:
            db (Session): Sesión de base de datos
            isbn (str): ISBN del libro
            skip (int): Número de registros a omitir
            limit (int): Número máximo de registros a retornar
            
        Returns:
            List[models.Transaccion]: Lista de transacciones del libro
            
        Raises:
            HTTPException: Si el libro no existe
        """
        # Verificar que existe el libro
        libro = LibroService.get_libro(db, isbn)
        
        return db.query(models.Transaccion).filter(
            models.Transaccion.isbn == isbn
        ).order_by(
            models.Transaccion.fecha_transaccion.desc()
        ).offset(skip).limit(limit).all() 