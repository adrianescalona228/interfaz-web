import sqlite3
from routes.database2 import get_db

# Conectar a la base de datos
conn = get_db()
cursor = conn.cursor()

def cambiar_comas_a_puntos():
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='inventario';")
        if not cursor.fetchone():
            raise ValueError("La tabla 'inventario' no existe en la base de datos.")

        # Actualizar la columna 'costo'
        cursor.execute("""
            UPDATE inventario
            SET costo = REPLACE(costo, ',', '.')
            WHERE costo LIKE '%,%';
        """)
        
        # Confirmar los cambios
        conn.commit()

        print("Actualización completada exitosamente.")

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")

    except ValueError as e:
        print(e)

    finally:
        # Cerrar la conexión
        if conn:
            conn.close()

if __name__ == "__main__":  
    cambiar_comas_a_puntos()
