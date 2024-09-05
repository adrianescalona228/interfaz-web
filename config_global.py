import configparser
import socket

def config_global():
    # Leer el archivo de configuración
    config = configparser.ConfigParser()
    config.read('config.ini')

    nombre_maquina = socket.gethostname()
    entornos = {
        'Adrian': 'development',
        'arnaldo-PC': 'production'
    }

    entorno = entornos.get(nombre_maquina)

    if entorno is None:
        raise ValueError(f"Nombre de la máquina '{nombre_maquina}' no reconocido")

    # Obtener las rutas según el entorno
    ruta_plantilla = config[entorno]['ruta_plantilla']
    ruta_guardar = config[entorno]['ruta_guardar']

    print(f"Ruta plantilla: {ruta_plantilla}")
    print(f"Ruta guardar: {ruta_guardar}")

    return ruta_plantilla, ruta_guardar
