from flask import Blueprint, render_template, send_file
import os
import logging
import re

logger = logging.getLogger(__name__)

notas_de_entrega_bp = Blueprint('notas_de_entrega', __name__)

@notas_de_entrega_bp.route('/notas_de_entrega')
def notas_de_entrega(): 
    directorio = '/home/ubuntu/Documents/trabajo/NOTA_DE_ENTREGA 2.0' 
    archivos = [f for f in os.listdir(directorio) if f.endswith('.pdf') or f.endswith('.xlsx')] 
    # Extraer el número de venta y ordenar los archivos 
    def extract_number(filename): 
        match = re.search(r'\.(\d+)_', filename) 
        return int(match.group(1)) if match else 0 
    archivos_ordenados = sorted(archivos, key=extract_number, reverse=True) 
    return render_template('/ventas/notas_de_entrega.html', archivos=archivos_ordenados)

@notas_de_entrega_bp.route('/ver_nota/<filename>', methods=['GET'])
def ver_nota_entrega(filename):
    directorio = '/home/ubuntu/Documents/trabajo/NOTA_DE_ENTREGA 2.0'
    file_path = os.path.join(directorio, filename)
    return send_file(file_path, as_attachment=False)
