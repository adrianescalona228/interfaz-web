
# Usa una imagen oficial ligera de Python
FROM python:3.14-rc-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists*;

# Copia los archivos de requisitos y el código fuente al contenedor
COPY requirements.txt .
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY . .

# Expone el puerto donde correrá Flask
EXPOSE 5000

# Comando para correr la app
CMD ["python3", "app.py"]
