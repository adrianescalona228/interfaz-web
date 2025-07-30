import os
from flask import Flask, render_template
from flask.json import load
from flask_sqlalchemy import SQLAlchemy
from routes.sales.sales import sales_bp
from routes.purchases.purchases import purchases_bp
from routes.clients.clients import clients_bp
from routes.inventory.inventory import inventario_bp
import logging
import socket
import sys
from dotenv import load_dotenv
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

load_dotenv()

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
    if not os.path.exists('logs'):
        os.mkdir('logs')

    hostname = socket.gethostname()
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    archivo_log = f'logs/app_{hostname}_{fecha_actual}.log'

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = TimedRotatingFileHandler(
        archivo_log, when='midnight', interval=1, backupCount=30
    )
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    file_handler.setLevel(logging.INFO)
    file_handler.encoding = 'utf-8'
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    sys.stdout = StreamToLogger(logger, logging.INFO)
    sys.stderr = StreamToLogger(logger, logging.ERROR)

    logging.info('Logging configurado correctamente')

def cargar_clave_secreta():
    with open('query.txt', 'r') as f:
        return f.read().strip()

from database import db

def create_app(testing=False):
    app = Flask(__name__, template_folder='templates')

    if testing:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    else:
        # Usa DATABASE_URL desde variables de entorno, o config.py como respaldo
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')  # fallback opcional

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = cargar_clave_secreta()

    db.init_app(app)

    with app.app_context():
        db.create_all()


    # Registrar Blueprints
    app.register_blueprint(sales_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(inventario_bp)
    # app.register_blueprint(graficas_bp)

    #print("pruebita ROUTES:")
    #for rule in app.url_map.iter_rules():
    #    print(rule)
    @app.route('/')
    def index():
        return render_template('index.html')

    return app

if __name__ == '__main__':
    configurar_logging()
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
