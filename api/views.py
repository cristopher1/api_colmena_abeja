from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tensorflow import keras
from pathlib import Path
from . import exceptions
import librosa
import logging
import os
import tempfile
logger = logging.getLogger('django')

# Ruta donde se guarda el archivo que contiene los pesos y arquitectura de la CNN
cnn_path = Path(__file__).resolve().parent / 'CNN' / \
    '13_mfcc_abeja_reina_3_seg.h5'

# Se carga la CNN a partir del archivo anteriormente mencionado
model = keras.models.load_model(cnn_path)

# Variables de entorno
# Ventana de tiempo: Usada para tomar la muestra de audio a procesar.
# Depende de la CNN. Por ejemplo, una CNN que trabaja con muestras de audio
# de 3[s], usará una ventana con valor 3.
VENTANA = int(os.environ.get('VENTANA_TIEMPO'))
# Número de canales: Usado para dimensionar el vector de mfccs entregado a la CNN.
N_CANAL = int(os.environ.get('N_CANAL'))


def copiarAudio(audio, suffix):
    """
        Copia el contenido de un archivo virtual a un archivo temporal.

        Debido a que librosa procesa los archivos .mp3 (y otras extensiones)
        a partir de la ruta de un archivo que se encuentra en el sistema de archivos,
        se usa esta función para copiar el contenido del archivo virtual (file-like object)
        a un archivo temporal generado por el módulo tempfile.

        El archivo temporal generado no se borrará automáticamente, por lo tanto
        deberá usar os.unlink para borrar el archivo del sistema.

        Parámetros:
        audio (file-like object): Archivo cargado en memoria.
        suffix (string): Extensión del archivo cargado en memoria.

        Retorno:
        tmp_nombre (string): Nombre del archivo temporal generado. Tiene la
        extensión dada por el parametro suffix.

        Excepciones producidas:
        FileCopyError (Exception).
    """
    try:
        fuente = audio.open()
        destino = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
        tmp_nombre = destino.name
        for linea in fuente:
            destino.write(linea)
        fuente.close()
        destino.close()
        return tmp_nombre
    except Exception as e:
        raise exceptions.FileCopyError(
            "No se pudo copiar el archivo", e.errors)


def cargarAudio(audio):
    """
        Carga el contenido de un archivo de audio en memoria.

        Librosa usa dos módulos para cargar los archivos de audio: soundfile y audioread.
        - Soundfile:  Carga archivos de audio de tipo WAV desde el sistema de archivos,
        archivos virtuales (file-like object) u otros medios.
        - Audioread: Cargar archivos de audio con otros formatos, por ejemplo MP3, pero
        solo los puedo cargar desde el sistema de archivo.
        Debido a lo anterior, esta función se encarga de indicar a librosa como procesar el
        archivo. Si tiene formato WAV, se pasará el file-like object a librosa,
        en caso contrario, se llamará a la función copiarAudio para generar un archivo temporal
        que se guardará en el sistema de archivos, cuyo nombre será dado a librosa.load.

        Parámetros:
        audio (file-like object): Archivo cargado en memoria.

        Retorno:
        (tuple): Retorna una tupla con dos valores descritos a continuación (ordenados según la
        numeración utilizada).
        1. Serie_tiempo (array): Arreglo con la serie de tiempo contenida en el archivo de audio.
        2. Tasa_muestreo (int): Tasa de muestreo con la cual se capturo la serie de tiempo

        Excepciones producidas:
        AudioLoadError (Exception).
    """
    try:
        suffix = audio.name.split('.')[-1]
        audio = audio if suffix == "wav" else copiarAudio(audio, suffix)
        serie_tiempo, tasa_muestreo = librosa.load(audio, sr=None)
        # Borra el archivo temporal generado por copiarAudio
        if isinstance(audio, str):
            os.unlink(audio)
        return serie_tiempo, tasa_muestreo
    except Exception as e:
        raise exceptions.AudioLoadError(
            "No se pudo cargar el audio", e.errors)


class EstadoSaludColmena(APIView):

    def post(self, request):
        try:
            audio = request.FILES['audio']
            serie_tiempo, tasa_muestreo = cargarAudio(audio)
            serie_tiempo = serie_tiempo[:tasa_muestreo * VENTANA]
            mfcc_13 = librosa.feature.mfcc(
                y=serie_tiempo, sr=tasa_muestreo, n_mfcc=13, dct_type=2)
            mfcc_13 = mfcc_13.reshape(1, *mfcc_13.shape, N_CANAL)
            prediccion = model.predict(mfcc_13)
            return Response(prediccion, status=status.HTTP_200_OK)
        except Exception as e:
            logger.info("excepcion {0}".format(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
