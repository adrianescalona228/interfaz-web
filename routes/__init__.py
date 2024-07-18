# from flask import Flask, g, render_template
# from .agregar_stock import agregar_stock_bp
# from .automatizar_mensajes import automatizar_mensajes_bp
# from .crear_notas_entrega import crear_notas_entrega_bp
# from .historial_ventas import historial_ventas_bp
# from .manejar_credito import manejar_credito_bp
# from .mostrar_inventario import mostrar_inventario_bp
# from .nueva_venta import nueva_venta_bp
# from .database import get_db
# import sqlite3


# def cargar_clave_secreta():
#     clave_secreta = None
#     with open('/home/apolito/.query.txt', 'r') as f:
#         clave_secreta = f.read().strip()
#     return clave_secreta

# def close_db(error):
#     if hasattr(g, 'db'):
#         g.db.close()

# def create_app():
#     app = Flask(__name__, template_folder='templates')


#     # Configuración secreta
#     app.config['SECRET_KEY'] = cargar_clave_secreta()

#     # Conexión y gestión de la base de datos
#     @app.before_request
#     def before_request():
#         g.db = get_db()

#     @app.teardown_appcontext
#     def teardown_appcontext(error):
#         close_db(error)

#     @app.route('/')
#     def index():
#         return render_template('index.html')

#     # Registrar los Blueprints
#     app.register_blueprint(agregar_stock_bp)
#     app.register_blueprint(automatizar_mensajes_bp)
#     app.register_blueprint(crear_notas_entrega_bp)
#     app.register_blueprint(historial_ventas_bp)
#     app.register_blueprint(manejar_credito_bp)
#     app.register_blueprint(mostrar_inventario_bp)
#     app.register_blueprint(nueva_venta_bp)

#     return app
