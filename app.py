# app.py
#from flask import Flask, g, render_template
from flask import Flask, g, render_template
from routes.ventas.ventas import ventas_bp
from routes.compras.compras import compras_bp
from routes.clientes.clientes import clientes_bp
from routes.inventario.inventario import inventario_bp
# from routes.graficas.graficas import graficas_bp
from routes.database2 import get_db
import os
import logging
import socket
import sys
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import configparser


class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level  
        self.linebuf = ''

    def write(self, buf):
        for line in buf.strip().splitlines():
            self.logger.log(self.level, line.strip())

    def flush(self):
        pass

def configurar_logging():
    # Crear el directorio de logs si no existe
    if not os.path.exists('logs'):
        os.mkdir('logs')

    hostname = socket.gethostname()
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    archivo_log = f'logs/app_{hostname}_{fecha_actual}.log'

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Configurar el manejador de archivo con rotación diaria y codificación UTF-8
    file_handler = TimedRotatingFileHandler(
        archivo_log,
        when='midnight',       # Rotar a medianoche
        interval=1,           # Intervalo de 1 día
        backupCount=30        # Mantener archivos de log de los últimos 30 días
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    file_handler.setLevel(logging.INFO)
    file_handler.encoding = 'utf-8'  # Configurar la codificación para el archivo

    logger.addHandler(file_handler)

    # Configurar salida en la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    # Redirigir stdout y stderr a los logs
    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)

    logging.info('Logging configurado correctamente')


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
    # app.register_blueprint(graficas_bp)

    return app

if __name__ == '__main__':
    configurar_logging()
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
