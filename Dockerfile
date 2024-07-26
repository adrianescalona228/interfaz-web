# Usa una imagen base de Python
FROM python:3.10

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo requirements.txt y luego instala las dependencias
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo del contenedor
COPY . /app

# Expone el puerto en el que Flask se ejecuta
EXPOSE 5000

# Comando para ejecutar la aplicación en modo de desarrollo
CMD ["flask", "run", "--host=0.0.0.0"]