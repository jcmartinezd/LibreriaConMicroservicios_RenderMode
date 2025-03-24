from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from ..database import Base

class Libro(Base):
    __tablename__ = "libros"
    
    ISBN = Column(String(13), primary_key=True, index=True)
    titulo = Column(String(255), nullable=False)
    precio_compra = Column(Float, nullable=False)
    precio_venta = Column(Float, nullable=False)
    cantidad_actual = Column(Integer, default=0, nullable=False)
    
    transacciones = relationship("Transaccion", back_populates="libro")
    
    __table_args__ = (
        CheckConstraint('precio_venta >= precio_compra', name='chk_precios'),
        CheckConstraint('cantidad_actual >= 0', name='chk_cantidad'),
    )

class TipoTransaccion(Base):
    __tablename__ = "tipos_transaccion"
    
    id_tipo = Column(Integer, primary_key=True)
    nombre = Column(String(20), nullable=False)
    
    transacciones = relationship("Transaccion", back_populates="tipo")
    
    __table_args__ = (
        CheckConstraint("nombre IN ('VENTA', 'ABASTECIMIENTO')", name='chk_tipo'),
    )

class Transaccion(Base):
    __tablename__ = "transacciones"
    
    id_transaccion = Column(Integer, primary_key=True, index=True)
    ISBN = Column(String(13), ForeignKey("libros.ISBN", ondelete="CASCADE"), nullable=False)
    tipo_transaccion = Column(Integer, ForeignKey("tipos_transaccion.id_tipo"), nullable=False)
    fecha_transaccion = Column(DateTime, default=func.now(), nullable=False)
    cantidad = Column(Integer, nullable=False)
    
    libro = relationship("Libro", back_populates="transacciones")
    tipo = relationship("TipoTransaccion", back_populates="transacciones")
    movimientos_caja = relationship("Caja", back_populates="transaccion")
    
    __table_args__ = (
        CheckConstraint('cantidad > 0', name='chk_cantidad_transaccion'),
    )

class Caja(Base):
    __tablename__ = "caja"
    
    id_movimiento = Column(Integer, primary_key=True, index=True)
    fecha_movimiento = Column(DateTime, default=func.now(), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)
    monto = Column(Float, nullable=False)
    saldo_actual = Column(Float, nullable=False)
    id_transaccion = Column(Integer, ForeignKey("transacciones.id_transaccion"), nullable=True)
    
    transaccion = relationship("Transaccion", back_populates="movimientos_caja")
    
    __table_args__ = (
        CheckConstraint("tipo_movimiento IN ('INGRESO', 'EGRESO')", name='chk_tipo_movimiento'),
    )