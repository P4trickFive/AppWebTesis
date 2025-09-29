import pandas as pd
from datetime import datetime
from models import Product, Sale
from sqlalchemy import func
from database import db

def get_sales_today():
    today = datetime.today().strftime('%Y-%m-%d')
    result = db.session.query(Sale, Product.nombre, Product.precio) \
               .join(Product, Sale.producto_id == Product.codigo) \
               .filter(Sale.fecha.startswith(today)) \
               .all()
    
    return result

def get_total_products():
    total_products = db.session.query(func.count()).filter(Product.estado == 1).scalar()
    return total_products

def get_low_stock_items():
    low_stock_threshold_min = 1  # Stock mínimo bajo (1 unidad)
    low_stock_threshold_max = 10  # Stock máximo bajo (10 unidades)
    
    # Consulta para contar productos con stock entre 1 y 10
    low_stock_count = db.session.query(func.count(Product.codigo)) \
                                .filter(Product.cantidad >= low_stock_threshold_min, Product.cantidad <= low_stock_threshold_max) \
                                .scalar()  # Total de productos con stock bajo

    return low_stock_count


def get_top_category():  #Categoria top - card
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Ventas por categoría y sumar las cantidades vendidas
    category_sales = db.session.query(Product.categoria, func.sum(Sale.cantidad)) \
        .join(Sale) \
        .filter(Sale.fecha >= start_of_month) \
        .group_by(Product.categoria) \
        .order_by(func.sum(Sale.cantidad).desc()) \
        .first()  

    # Retornar la categoría con más ventas o "N/A" si no hay ventas
    return category_sales[0] if category_sales else "N/A"


def get_top_categories():
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Ventas por categoría y sumar las cantidades vendidas
    categories_sales = db.session.query(Product.categoria, func.sum(Sale.cantidad)) \
        .join(Sale) \
        .filter(Sale.fecha >= start_of_month) \
        .group_by(Product.categoria) \
        .order_by(func.sum(Sale.cantidad).desc()) \
        .all()

    # Si no hay ventas, devolver una lista vacía
    if not categories_sales:
        return []

    return categories_sales



def get_total_sales():
    # Filtrar ventas del día
    sales_today = db.session.query(Sale).filter(Sale.fecha.like(f'{datetime.now().strftime("%Y-%m-%d")}%')).all()

    # Total de ventas producto
    total_sales = sum(sale.cantidad * sale.producto.precio for sale in sales_today)

    return total_sales if total_sales else 0

def get_critical_low_stock_items():
    critical_stock_threshold_min = 1  # Stock mínimo crítico (1 unidad)
    critical_stock_threshold_max = 3  # Stock máximo crítico (3 unidades)
    
    # Consulta para obtener productos con stock entre 1 y 3
    critical_items = db.session.query(Product.nombre, Product.cantidad) \
                               .filter(Product.cantidad >= critical_stock_threshold_min, Product.cantidad <= critical_stock_threshold_max) \
                               .all()  # productos con stock entre 1 y 3 unidades

    return critical_items