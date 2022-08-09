FROM python:3.10 as base

# Se instalan paquetes necesarios para que las bibliotecas usadas por librosa puedan
# procesar audio.
RUN apt-get update && \
    apt-get install -y \
    # Librosa procesa audio usando las librerías audioread y soundfile. Si se usa
    # conda, no es necesario instalar nada, en caso contrario se necesitan paquetes
    # adicionales
    # Libsndfile: Necesario para que funcione correctamente soundfile.
    libsndfile1-dev

# Se establece el directorio de trabajo actual
WORKDIR /usr/src/api

FROM base as development

# Se copia el archivo con las dependencias
COPY requirements.dev.txt ./

# Se instalan las dependencias
RUN pip --no-cache-dir install -r requirements.dev.txt

# Se copia el resto de los archivos a la carpeta de trabajo actual
COPY . ./

# Se expone el puerto 8000
EXPOSE 8000

# Se ejecuta la api
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

FROM base as production

# Se copia el archivo con las dependencias
COPY requirements.prod.txt ./

# Se instalan las dependencias
RUN pip install -r requirements.prod.txt

# Se copia el resto de los archivos a la carpeta de trabajo actual
COPY . ./

# Se expone el puerto 8000
EXPOSE 443

# Se ejecuta la api
CMD [ "gunicorn", "api_memoria_colmena_abejas.wsgi:application", "--bind", "0.0.0.0:443" ]
