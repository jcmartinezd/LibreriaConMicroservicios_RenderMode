from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

# Esquemas para Libro
class LibroBase(BaseModel):
    titulo: str
    precio_compra: float = Field(..., gt=0)
    precio_venta: float = Field(..., gt=0)
    
    @validator('precio_venta')
    def precio_venta_mayor_que_compra(cls, v, values):
        if 'precio_compra' in values and v < values['precio_compra']:
            raise ValueError('El precio de venta debe ser mayor o igual al precio de compra')
        return v

class LibroCreate(LibroBase):
    ISBN: str
    cantidad_actual: int = 0

class Libro(LibroBase):
    ISBN: str
    cantidad_actual: int
    
    class Config:
        orm_mode = True

# Esquemas para Transacción
class TransaccionBase(BaseModel):
    ISBN: str
    tipo_transaccion: int
    cantidad: int = Field(..., gt=0)

class TransaccionCreate(TransaccionBase):
    pass

class Transaccion(TransaccionBase):
    id_transaccion: int
    fecha_transaccion: datetime
    
    class Config:
        orm_mode = True

# Esquemas para Caja
class CajaBase(BaseModel):
    tipo_movimiento: str
    monto: float
    saldo_actual: float

class CajaCreate(CajaBase):
    id_transaccion: Optional[int] = None

class Caja(CajaBase):
    id_movimiento: int
    fecha_movimiento: datetime
    id_transaccion: Optional[int] = None
    
    class Config:
        orm_mode = True