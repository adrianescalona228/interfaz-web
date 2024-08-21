# Usar una imagen base oficial de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos de requisitos y el código fuente
COPY requirements.txt requirements.txt
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Establecer la variable de entorno FLASK_APP
ENV FLASK_APP=app.py

# Exponer el puerto en el que corre Flask
EXPOSE 5000

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]