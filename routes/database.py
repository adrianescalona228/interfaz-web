import sqlite3
from flask import g

DATABASE = '/home/apolito/Programacion/Proyectos/interfaz_web/DATABASE/inventory.db'


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db