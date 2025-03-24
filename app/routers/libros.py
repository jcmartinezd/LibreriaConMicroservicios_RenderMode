from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db
from ..schemas import schemas
from ..services import LibroService

router = APIRouter(
    prefix="/api/libros",
    tags=["libros"],
    responses={404: {"description": "No encontrado"}},
)

@router.post("/", response_model=schemas.Libro, status_code=status.HTTP_201_CREATED)
def create_libro(libro: schemas.LibroCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo libro en el inventario
    
    Esta operación registra un nuevo libro con su ISBN, título, precios y cantidad inicial.
    
    Retorna:
    - El libro creado con todos sus datos
    
    Errores:
    - 400: Si ya existe un libro con ese ISBN
    """
    return LibroService.create_libro(db=db, libro=libro)

@router.get("/", response_model=List[schemas.Libro])
def read_libros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene la lista de libros en el inventario
    
    Esta operación devuelve todos los libros registrados con paginación
    
    Parámetros:
    - skip: Número de registros a omitir (opcional, predeterminado: 0)
    - limit: Número máximo de registros a devolver (opcional, predeterminado: 100)
    
    Retorna:
    - Lista de libros con todos sus datos
    """
    return LibroService.get_libros(db, skip=skip, limit=limit)

@router.get("/{isbn}", response_model=schemas.Libro)
def read_libro(isbn: str, db: Session = Depends(get_db)):
    """
    Obtiene un libro específico por su ISBN
    
    Esta operación busca y devuelve un libro según su identificador único
    
    Parámetros:
    - isbn: Identificador único del libro (ISBN)
    
    Retorna:
    - El libro encontrado con todos sus datos
    
    Errores:
    - 404: Si no se encuentra un libro con ese ISBN
    """
    db_libro = LibroService.get_libro(db, ISBN=isbn)
    if db_libro is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return db_libro

@router.put("/{isbn}", response_model=schemas.Libro)
def update_libro(isbn: str, libro: schemas.LibroCreate, db: Session = Depends(get_db)):
    """
    Actualiza los datos de un libro existente
    
    Esta operación modifica los datos de un libro según su ISBN.
    Nota: No se puede modificar la cantidad directamente, debe hacerse mediante transacciones.
    
    Parámetros:
    - isbn: Identificador único del libro (ISBN)
    - libro: Nuevos datos del libro
    
    Retorna:
    - El libro actualizado con todos sus datos
    
    Errores:
    - 404: Si no se encuentra un libro con ese ISBN
    """
    return LibroService.update_libro(db=db, ISBN=isbn, libro=libro)

@router.delete("/{isbn}", response_model=dict)
def delete_libro(isbn: str, db: Session = Depends(get_db)):
    """
    Elimina un libro del inventario
    
    Esta operación elimina permanentemente un libro y todas sus transacciones asociadas
    
    Parámetros:
    - isbn: Identificador único del libro (ISBN)
    
    Retorna:
    - Mensaje de confirmación
    
    Errores:
    - 404: Si no se encuentra un libro con ese ISBN
    """
    LibroService.delete_libro(db=db, ISBN=isbn)
    return {"mensaje": "Libro eliminado correctamente"}