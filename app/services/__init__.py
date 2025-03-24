"""
Módulo de servicios para la aplicación Tienda de Libros.
Este módulo contiene las clases de servicio que implementan la lógica de negocio
y reemplazan los triggers de base de datos con lógica en la aplicación.
"""

from app.services.libro_service import LibroService
from app.services.transaccion_service import TransaccionService
from app.services.caja_service import CajaService 