
# Usa una imagen oficial ligera de Python
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requisitos y el código fuente al contenedor
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Expone el puerto donde correrá Flask
EXPOSE 5000

# Comando para correr la app
CMD ["python", "app.py"]
