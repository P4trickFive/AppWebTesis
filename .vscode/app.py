from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import init_db, db
from ml_utils import get_total_products, get_low_stock_items, get_top_category, get_total_sales, get_critical_low_stock_items, get_top_categories
from datetime import datetime, timedelta
from models import Product, Sale
from models import LOCAL_TIMEZONE



app = Flask(__name__)

# Inicio
init_db(app)

@app.teardown_appcontext
def shutdown_session(_=None):  # Se ignora el argumento no usado
    db.session.remove()

@app.route('/')
def dashboard():
    total_products = get_total_products()
    low_stock_items = get_low_stock_items()
    top_category = get_top_category()
    categories_sales = get_top_categories()
    total_sales = get_total_sales()
    critical_stock_items = get_critical_low_stock_items()

    return render_template('dashboard.html',total_products=total_products, 
                           low_stock_items=low_stock_items, 
                           top_category=top_category,
                           categories_sales=categories_sales,
                           total_sales=total_sales,
                           critical_stock_items=critical_stock_items)

@app.route('/ventas')
def ventas():
    products = db.session.query(Product).filter_by(estado=1).all() #productos de la tabla 'productos'
    return render_template('ventas.html', products=products)

from datetime import datetime


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        try:
            if 'delete_product' in request.form:
                # 🗑️ Eliminar (desactivar) producto
                product_id = int(request.form['product_id'])
                product = db.session.query(Product).get(product_id)
                
                if product:
                    product.estado = 0  # 🔹 Desactivar el producto
                    product.cantidad = 0  # 🔹 Poner cantidad en 0
                    db.session.commit()
                    print(f"🗑️ Producto desactivado: {product.nombre}")
                else:
                    print("❌ No se encontró el producto para eliminar.")

            else:
                # 🟢 Agregar / Modificar producto
                nombre = request.form['nombre']
                cantidad = int(request.form['cantidad'])
                precio = float(request.form['precio'])
                categoria = request.form['categoria']

                existing_product = db.session.query(Product).filter_by(nombre=nombre).first()
                now = datetime.now(LOCAL_TIMEZONE).date()

                if existing_product:
                    existing_product.cantidad = cantidad  # 🔹 Actualizar cantidad
                    existing_product.precio = precio  
                    existing_product.categoria = categoria  
                    existing_product.estado = 1  # 🔹 Asegurar que esté activo
                    
                    # 🔥 Si la cantidad era 0, actualizamos la fecha_ingreso
                    if existing_product.cantidad == cantidad:
                        existing_product.fecha_ingreso = now

                    print(f"🔄 Producto actualizado: {nombre}")
                else:
                    new_product = Product(
                        nombre=nombre, 
                        cantidad=cantidad, 
                        precio=precio, 
                        categoria=categoria, 
                        estado=1,
                        fecha_ingreso=now # 🔹 Nueva fecha de ingreso
                    )
                    db.session.add(new_product)
                    db.session.commit()
                    new_product.generar_codigo()  
                    print(f"🆕 Producto agregado: {nombre}")

            db.session.commit()
            db.session.close()  
            print("💾 Cambios guardados correctamente.")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error en la base de datos: {e}")

        return redirect(url_for('products'))

    # 🔹 Mostrar solo productos activos
    products = db.session.query(Product).filter_by(estado=1).all()

    return render_template('products.html', products=products)


@app.route('/buscar_producto', methods=['GET'])
def buscar_producto():
    try:
        nombre = request.args.get('nombre', '').strip()
        print(f"Nombre recibido: {nombre}")
        if not nombre:
            return jsonify({'error': 'No se proporcionó un nombre'}), 400

        productos = db.session.query(Product).filter(
            Product.nombre.ilike(f"%{nombre}%"), Product.estado == 0
        ).all()

        resultados = [{
            'nombre': p.nombre,
            'precio': p.precio,
            'categoria': p.categoria,
            'cantidad': p.cantidad
        } for p in productos]

        return jsonify(resultados)

    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")
        return jsonify({'error': str(e)}), 500







@app.route('/reports', methods=['GET', 'POST'])
def reports():
    # Obtener productos con stock bajo y la categoría más vendida
    low_stock = db.session.query(Product).filter(Product.cantidad >= 1, Product.cantidad <= 10).all()
    categories_sales = get_top_categories()

    # Total de ventas del día
    sales_today = []
    total_sales_day = 0

    # Definir por defecto  today
    selected_period = request.form.get('period', 'today')

    # Filtrar ventas según el periodo seleccionado
    if selected_period == 'today':
        sales_today = db.session.query(Sale).filter(Sale.fecha.like(f'{datetime.now(LOCAL_TIMEZONE).strftime("%Y-%m-%d")}%')).all()

    elif selected_period == 'month':
        start_date = datetime.now() - timedelta(days=30)
        sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

    elif selected_period == '3months':
        start_date = datetime.now() - timedelta(days=90)
        sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

    elif selected_period == '6months':
        start_date = datetime.now() - timedelta(days=180)
        sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

    elif selected_period == 'year':
        start_date = datetime.now() - timedelta(days=365)
        sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date).all()

    elif selected_period == 'custom':
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        sales_today = db.session.query(Sale).filter(Sale.fecha >= start_date, Sale.fecha <= end_date).all()

    # Calcular el total de ventas en el periodo seleccionado
    total_sales_day = round(sum(sale.cantidad * sale.producto.precio for sale in sales_today),2)

    return render_template('reports.html', 
                           low_stock=low_stock, 
                           categories_sales=categories_sales, 
                           sales=sales_today, 
                           total_sales_day=total_sales_day)


@app.route('/realizar_venta', methods=['POST'])
def realizar_venta():
    data = request.get_json()

    if not data.get('productos'):
        return jsonify({'error': 'No se recibieron productos.'}), 400

    total = 0
    try:
        with db.session.begin():
            for producto_data in data['productos']:
                # Obtener el producto de la base de datos
                
                producto = Product.query.get(producto_data['id'])

                if not producto:
                    return jsonify({'error': f"Producto con ID {producto_data['id']} no encontrado."}), 404

                # Verificar si hay suficiente cantidad
                if producto.cantidad < producto_data['cantidad']:
                    return jsonify({'error': f"Cantidad insuficiente para {producto.nombre}."}), 400

                # Actualizar la cantidad en la tabla productos
                producto.cantidad -= producto_data['cantidad']
                total += producto.precio * producto_data['cantidad']

                # Insertar el registro de la venta en la tabla ventas
                nueva_venta = Sale(producto_id=producto.id, cantidad=producto_data['cantidad'], fecha=datetime.now(LOCAL_TIMEZONE))
                db.session.add(nueva_venta)

            db.session.commit()

        return jsonify({'message': 'Venta registrada con éxito.', 'total': total}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)