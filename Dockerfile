# El modulo librosa procesa audio usando las librerías audioread y soundfile. Si se quiere
# procesar archivos .mp3 mediante librosa, se tendrá que instalar paquetes adicionales para
# que audioread pueda hacerlo, para ello puede consultar la página
# https://github.com/beetbox/audioread
FROM python:3.10-slim@sha256:5ddc6ea17ec33701f8d5a6777a7b9953b7786eddeafb28b0d4e84011ebe6976b as base

# Se instalan paquetes necesarios para que las bibliotecas usadas por librosa puedan
# procesar audio.
RUN apt-get update && apt-get install -y \
    # Necesario para que funcione correctamente soundfile. Soundfile puede
    # procesar archivos .wav usando libsndfile
    libsndfile1-dev \
    # Necesario para que funcione correctamente audioread. Audioread puede
    # procesar archivos .mp3 usando ffmpeg mediante la interfaz de comandos
    ffmpeg

# Se establece el directorio de trabajo actual
WORKDIR /usr/src/api

FROM base as development

RUN apt-get update && apt-get install -y \
    # Instalar editor de texto, para revisar archivos dentro del contenedor
    nano \
    # Instalar pip, para los casos donde se deban probar paquetes de python
    # dentro del contenedor de desarrollo.
    python3-pip

# Se copia el archivo con las dependencias
COPY requirements.dev.txt ./

# Se instalan las dependencias
RUN pip --no-cache-dir install -r requirements.dev.txt

# Se copia el resto de los archivos a la carpeta de trabajo actual
COPY . ./

# Se expone el puerto
EXPOSE 8000

# Se ejecuta la api
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

FROM base as production

# Se copia el archivo con las dependencias
COPY requirements.prod.txt ./

# Se instalan las dependencias
RUN pip --no-cache-dir install -r requirements.prod.txt

# Se copia el resto de los archivos a la carpeta de trabajo actual
COPY . ./

# Se expone el puerto.
EXPOSE 443

# Se ejecuta la api
CMD [ "gunicorn", "api_memoria_colmena_abejas.wsgi:application", "--bind", "0.0.0.0:443" ]
