from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import List, Optional

from app.models import models
from app.schemas import schemas

class LibroService:
    """
    Servicio para gestionar las operaciones de libros.
    Implementa la lógica de negocio relacionada con el inventario.
    """
    
    @staticmethod
    def create_libro(db: Session, libro: schemas.LibroCreate) -> models.Libro:
        """
        Crea un nuevo libro en el inventario.
        
        Args:
            db (Session): Sesión de base de datos
            libro (schemas.LibroCreate): Datos del libro a crear
            
        Returns:
            models.Libro: El libro creado
            
        Raises:
            HTTPException: Si el ISBN ya existe o si hay un error de validación
        """
        # Verificar si ya existe un libro con ese ISBN
        db_libro = db.query(models.Libro).filter(models.Libro.isbn == libro.isbn).first()
        if db_libro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un libro con el ISBN {libro.isbn}"
            )
        
        # Validaciones de negocio
        if libro.precio_venta < libro.precio_compra:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio de venta no puede ser menor al precio de compra"
            )
        
        if libro.cantidad_actual < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad inicial no puede ser negativa"
            )
        
        # Crear el libro
        db_libro = models.Libro(
            isbn=libro.isbn,
            titulo=libro.titulo,
            precio_compra=libro.precio_compra,
            precio_venta=libro.precio_venta,
            cantidad_actual=libro.cantidad_actual,
            fecha_creacion=datetime.now()
        )
        
        db.add(db_libro)
        db.commit()
        db.refresh(db_libro)
        
        return db_libro
    
    @staticmethod
    def get_libros(db: Session, skip: int = 0, limit: int = 100) -> List[models.Libro]:
        """
        Obtiene la lista de libros con paginación.
        
        Args:
            db (Session): Sesión de base de datos
            skip (int): Número de registros a omitir
            limit (int): Número máximo de registros a retornar
            
        Returns:
            List[models.Libro]: Lista de libros
        """
        return db.query(models.Libro).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_libro(db: Session, isbn: str) -> Optional[models.Libro]:
        """
        Obtiene un libro por su ISBN.
        
        Args:
            db (Session): Sesión de base de datos
            isbn (str): ISBN del libro a buscar
            
        Returns:
            Optional[models.Libro]: El libro encontrado o None
            
        Raises:
            HTTPException: Si el libro no existe
        """
        db_libro = db.query(models.Libro).filter(models.Libro.isbn == isbn).first()
        if not db_libro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un libro con el ISBN {isbn}"
            )
        return db_libro
    
    @staticmethod
    def update_libro(db: Session, isbn: str, libro: schemas.LibroUpdate) -> models.Libro:
        """
        Actualiza los datos de un libro.
        
        Args:
            db (Session): Sesión de base de datos
            isbn (str): ISBN del libro a actualizar
            libro (schemas.LibroUpdate): Datos actualizados del libro
            
        Returns:
            models.Libro: El libro actualizado
            
        Raises:
            HTTPException: Si el libro no existe o hay un error de validación
        """
        db_libro = LibroService.get_libro(db, isbn)
        
        # Validaciones de negocio
        if libro.precio_venta < libro.precio_compra:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El precio de venta no puede ser menor al precio de compra"
            )
        
        if libro.cantidad_actual < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La cantidad no puede ser negativa"
            )
        
        # Actualizar datos
        db_libro.titulo = libro.titulo
        db_libro.precio_compra = libro.precio_compra
        db_libro.precio_venta = libro.precio_venta
        db_libro.cantidad_actual = libro.cantidad_actual
        db_libro.fecha_actualizacion = datetime.now()
        
        db.commit()
        db.refresh(db_libro)
        
        return db_libro
    
    @staticmethod
    def delete_libro(db: Session, isbn: str) -> dict:
        """
        Elimina un libro del inventario.
        
        Args:
            db (Session): Sesión de base de datos
            isbn (str): ISBN del libro a eliminar
            
        Returns:
            dict: Mensaje de confirmación
            
        Raises:
            HTTPException: Si el libro no existe o no se puede eliminar
        """
        db_libro = LibroService.get_libro(db, isbn)
        
        # Verificar si el libro tiene transacciones asociadas
        transacciones = db.query(models.Transaccion).filter(models.Transaccion.isbn == isbn).first()
        if transacciones:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar el libro con ISBN {isbn} porque tiene transacciones asociadas"
            )
        
        db.delete(db_libro)
        db.commit()
        
        return {"message": f"Libro con ISBN {isbn} eliminado correctamente"} 