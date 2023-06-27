# Selecciona la imagen base con Ubuntu 22.04
FROM ubuntu:22.04

# Actualiza los paquetes y realiza la instalación de Python y otras dependencias necesarias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    libmysqlclient-dev

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /web

# Copia los archivos necesarios al contenedor
COPY . /web

# Instala las dependencias de Python desde el archivo requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Expone el puerto 5000 para que Flask pueda recibir solicitudes
EXPOSE 5000

# Ejecuta la aplicación utilizando el comando "flask run --host=0.0.0.0"
CMD ["flask", "run", "--host=0.0.0.0", "--debug"]
