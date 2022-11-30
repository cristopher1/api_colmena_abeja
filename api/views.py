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
import enum
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


# Anomalias detectadas por la CNN
class Anomalias(enum.Enum):
    SIN_ABEJA_REINA = 0


# Utilizado para acceder al arreglo predicción que solo contiene dos valores.
# Si por algún motivo desea detectar más anomalias con la CNN, tendrá que cambiar
# la forma de acceder a los resultados de las predicciones mediante la función
# generarResultados.
class PresenciaAnomalias(enum.Enum):
    NO = 0
    SI = 1


def formatearResultados(nombre_audio, prediccion):
    """
        Formatea los resultados para que puedan ser consumidos por un cliente web.

        Procesa los resultados de analizar un solo archivo de audio mediante la
        CNN. Se genera un diccionario cuyas claves son:

        - audio (string): Indica el nombre del archivo de audio procesado
        (incluye la extensión del archivo).
        - anomalias (list): Lista que contiene las anomalias detectadas dentro de la colmena.
        Cada anomalia es representada mediante un diccionario cuyos valores son:
            - nombre (string): String que indica el nombre de la anomalia.
            - si (float): flotante que señala la probabilidad de que dicha anomalia este
            presente dentro de la colmena.
            - no (float): flotante que señala la probabilidad de que dicha anomalia no
            este presente dentro de la colmena.

        A continuación se da un ejemplo gráfico de la estructura de la respuesta enviada
        por el servidor.

        {
            "audio": "nombre audio",
            "anomalias": [
                {
                    "nombre": "sin_abeja_reina",
                    "si": 0.3,
                    "no": 0.7
                }
            ]
        }

        Hay que tener en cuenta que al momento de desarrollar esta aplicación, solo se
        analizaba si existia o no presencia de abeja reina, por lo tanto el largo de
        "anomalias" era 1. Si se cambia el sistema para analizar más anomalias, modificar
        esta parte de la documentacion.

        Parámetros:
        nombre_audio (string): Nombre del archivo de audio (incluye extension).
        prediccion (array 1D): Arreglo con las predicciones realizadas por la CNN.

        Retorno:
        (dict): Diccionario con la respuesta formateada.
    """
    # Nota. De momento la forma en que se formatea los datos solo funciona para una CNN que
    # indica si una colmena tiene o no una anomalia (por ejemplo: sin abeja reina o con abeja reina).
    # Si se quiere trabajar con una CNN que clasifique varias anomalías (por ejemplo: ausencia de
    # reina, presencia de varroa, ataque de algun insecto, etc) modificar la variable anomalias,
    # para ajustar la salida de la CNN con el formato de los datos entregados por el servidor.
    anomalias = [
        dict(
            nombre=anomalia.name.lower(),
            si=prediccion[PresenciaAnomalias.SI.value],
            no=prediccion[PresenciaAnomalias.NO.value]
        ) for anomalia in Anomalias
    ]
    return {
        "audio": nombre_audio,
        "anomalias": anomalias
    }


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


def borrarAudioCopiado(audio):
    """
        Borra el archivo temporal generado por copiarAudio.

        borrarAudioCopiado se encarga de borrar el archivo temporal generado por copiarAudio.
        Para que el archivo temporal sea borrado, la variable audio debe contener el nombre
        del archivo en cuestión.

        Parámetros:

        audio (Object): Si esta variable es de tipo string, corresponde
        al nombre del archivo temporal generado por copiarAudio. Si es un file-like object
        entonces es un archivo virtual que puede ser usado directamente por librosa,
        el cual no fue guardado en un archivo temporal, en dicho caso esta función no hace
        nada.
    """
    if isinstance(audio, str):
        os.unlink(audio)


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
        serie_tiempo, tasa_muestreo = librosa.load(audio, sr=44100)
        borrarAudioCopiado(audio)
        return serie_tiempo, tasa_muestreo
    except Exception as e:
        raise exceptions.AudioLoadError(
            "No se pudo cargar el audio", e.errors)


class EstadoSaludColmena(APIView):

    def post(self, request):
        try:
            audio = request.FILES['audio']
            serie_tiempo, tasa_muestreo = cargarAudio(audio)
            tamanno_muestra = tasa_muestreo * VENTANA
            if len(serie_tiempo) < tamanno_muestra:
                raise exceptions.AudioSizeError("Audio muy corto",
                                                "El archivo tiene una duración menor a {0} {1}"
                                                .format(VENTANA, "segundos"))
            serie_tiempo = serie_tiempo[:tamanno_muestra]
            mfcc_13 = librosa.feature.mfcc(
                y=serie_tiempo, sr=tasa_muestreo, n_mfcc=13, dct_type=2)
            mfcc_13 = mfcc_13.reshape(1, *mfcc_13.shape, N_CANAL)
            # Como solamente se esta procesando un archivo a la vez, se toma la primera
            # predicción de la matriz de predicciones
            prediccion = model.predict(mfcc_13)[0]
            resultado = formatearResultados(audio.name, prediccion)
            return Response(resultado, status=status.HTTP_200_OK)
        except exceptions.AudioSizeError as e:
            logger.info("excepcion {0}".format(e))
            return Response(e.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.info("excepcion {0}".format(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
