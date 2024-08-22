#routes/compras/compras.py
from flask import Blueprint, render_template
from .subfunciones.agregar_cliente_nuevo import agregar_clientes_nuevos_bp
from .subfunciones.lista_clientes import lista_clientes_bp
from .subfunciones.registrar_abono import *
from .subfunciones.ver_deudas import deudas_bp
from .subfunciones.historial_abonos import historial_abonos_bp

clientes_bp = Blueprint('clientes', __name__)
clientes_bp.register_blueprint(agregar_clientes_nuevos_bp, url_prefix='/agregar_clientes_nuevos')
clientes_bp.register_blueprint(lista_clientes_bp, url_prefix='/lista_clientes')
clientes_bp.register_blueprint(registrar_abono_bp, url_prefix='/registrar_abono')
clientes_bp.register_blueprint(deudas_bp, url_prefix='/ver_deudas')
clientes_bp.register_blueprint(historial_abonos_bp, url_prefix='/historial_abonos')

@clientes_bp.route('/clientes')
def clientes():
    return render_template('/clientes/clientes.html')