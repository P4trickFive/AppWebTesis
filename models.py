from database import db
from datetime import datetime
import pytz

LOCAL_TIMEZONE = pytz.timezone("America/Lima")

class Product(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(6), nullable=False, unique=True)
    nombre = db.Column(db.String, nullable=False)
    categoria = db.Column(db.String, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha_ingreso = db.Column(db.Date, nullable=False, default=lambda: datetime.now(LOCAL_TIMEZONE))
    estado = db.Column(db.Integer, nullable=False, default=1)  # 1 = Activo, 0 = Inactivo

    ventas = db.relationship('Sale', back_populates='producto')

    def generar_codigo(self):
        self.codigo = str(self.id).zfill(6)

    def actualizar_estado(self):
        """ Si el producto tiene stock, se activa. Si no, se inactiva. """
        self.estado = 1 if self.cantidad > 0 else 0


class Sale(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, default=lambda: datetime.now(LOCAL_TIMEZONE))

    producto = db.relationship('Product', back_populates="ventas")

    def __init__(self, producto_id, cantidad, fecha=None):
        self.producto_id = producto_id
        self.cantidad = cantidad
        self.fecha = fecha or datetime.now(LOCAL_TIMEZONE)