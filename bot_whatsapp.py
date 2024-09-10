from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.keys import Keys
import logging

# Configuración básica del logger
logging.basicConfig(filename='errores_chat.log', level=logging.ERROR, 
                    format='%(asctime)s %(levelname)s: %(message)s')


contactos = {
    'pruebas': [
        {'nombre': 'Pipa', 'numero': '+58 414-4232501'},
        {'nombre': '+58 424-4074402', 'numero': '+58 424-4074402'}, 
        {'nombre': 'Andres Guerra', 'numero': '+58 424-4569942'}, 
        {'nombre': 'Ruth Juge', 'numero': '+58 414-1431059'},
    ],
    'clientes': [
        {'nombre': 'tu', 'numero': '+584244074402'}
    ]
}

def abrir_whatsapp():
    # Configura las opciones de Chrome para usar tu perfil
    chrome_options = Options()
    chrome_options.add_argument(r"user-data-dir=C:\Users\adria\AppData\Local\Google\Chrome\User Data")
    chrome_options.add_argument(r"profile-directory=Default")  # Cambia a tu perfil específico si es necesario

    
    # Configura el WebDriver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get('https://web.whatsapp.com')

    try:
        # Espera a que aparezca la caja de búsqueda de chats (indica que WhatsApp está cargado)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        # time.sleep(10000000)
        print("WhatsApp Web está abierto y listo.")
        return driver

    except Exception as e:
        print(f"Error al abrir WhatsApp Web: {e}")

        return 
    
def buscar_contacto(driver, numero, nombre):
    try:
        # Buscar el contacto en la barra de búsqueda
        search_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        # Seleccionar todo el texto en el campo de búsqueda y eliminarlo
        search_box.send_keys(Keys.CONTROL + "a")
        search_box.send_keys(Keys.DELETE)
        search_box.send_keys(numero)
        time.sleep(0.5)
        # print(f"Contacto {nombre} buscado.")
        return True
    except Exception as e:
        print(f"Error al buscar el contacto {nombre}: {e}")
        return False
def confirmar_chat_y_entrar(driver, nombre):
    chat_encontrado = False  # Agregamos la bandera

    try:
        # Esperar a que aparezcan los resultados de búsqueda
        search_results = WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//span[@title]'))
        )

        # Recorrer los resultados y verificar si alguno coincide con el nombre
        for chat_title in search_results:
            chat_nombre = chat_title.text
            if chat_nombre.lower() == nombre.lower():
                chat_title.click()  # Entrar al chat si es el correcto
                
                # print(f"Confirmado y entrando al chat con {nombre}.")
                chat_encontrado = True  # Cambiamos la bandera a True
                break  # Salir del bucle for
            else:
                error_message = f"Chat no encontrado con el nombre {nombre}."
                print(error_message)
                logging.error(error_message)  # Guardar el error en el log
                break  # Salir del bucle for

    except Exception as e:
        error_message = f"Error al confirmar el chat {nombre}: {e}"
        print(error_message)
        logging.error(error_message)  # Guardar el error en el log

    return chat_encontrado  # Devolvemos si el chat fue encontrado o no



# Llama a la función para probar
driver = abrir_whatsapp()

# time.sleep(100000)

for contacto in contactos['pruebas']:
    if buscar_contacto(driver, contacto['numero'], contacto['nombre']):
        confirmar_chat_y_entrar(driver, contacto['nombre'])
