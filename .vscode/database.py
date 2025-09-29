from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()

def init_db(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Administrator/Documents/productos.db?check_same_thread=False'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # 🔹 Crear tablas dentro del contexto de la app
    with app.app_context():
        db.create_all()
