from sqlalchemy.orm import Session
from ..models import models
from ..schemas import schemas

def get_libro_by_isbn(db: Session, ISBN: str):
    return db.query(models.Libro).filter(models.Libro.ISBN == ISBN).first()

def get_libros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Libro).offset(skip).limit(limit).all()

def create_libro(db: Session, libro: schemas.LibroCreate):
    db_libro = models.Libro(
        ISBN=libro.ISBN,
        titulo=libro.titulo,
        precio_compra=libro.precio_compra,
        precio_venta=libro.precio_venta,
        cantidad_actual=libro.cantidad_actual
    )
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def update_libro(db: Session, ISBN: str, libro: schemas.LibroBase):
    db_libro = get_libro_by_isbn(db, ISBN=ISBN)
    for key, value in libro.dict().items():
        setattr(db_libro, key, value)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def delete_libro(db: Session, ISBN: str):
    db_libro = get_libro_by_isbn(db, ISBN=ISBN)
    db.delete(db_libro)
    db.commit()
    return db_libro