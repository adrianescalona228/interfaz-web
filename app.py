# app.py
#from flask import Flask, g, render_template
from flask import Flask, g, render_template
from routes.ventas.ventas import ventas_bp
from routes.compras.compras import compras_bp
from routes.clientes.clientes import clientes_bp
from routes.inventario.inventario import inventario_bp
from routes.database import get_db
import sqlite3

def cargar_clave_secreta():
    clave_secreta = None
    with open('query.txt', 'r') as f:
        clave_secreta = f.read().strip()
    return clave_secreta

def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def create_app():
    app = Flask(__name__, template_folder='templates')

    # Configuración secreta
    app.config['SECRET_KEY'] = cargar_clave_secreta()

    # Conexión y gestión de la base de datos
    @app.before_request
    def before_request():
        g.db = get_db()

    @app.teardown_appcontext
    def teardown_appcontext(error):
        close_db(error)

    @app.route('/')
    def index():
        return render_template('index.html')

    # Registrar los Blueprints
    app.register_blueprint(ventas_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(inventario_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)
