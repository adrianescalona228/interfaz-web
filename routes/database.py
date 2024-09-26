import os
import sqlite3
from flask import g

# Obtén el directorio actual del script
basedir = os.path.abspath(os.path.dirname(__file__))

# Configura la base de datos usando una ruta relativa
DATABASE = os.path.join(basedir, '..', 'DATABASE', 'inventory2_copy3.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db