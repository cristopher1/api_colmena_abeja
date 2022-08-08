from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tensorflow import keras
from pathlib import Path
import librosa
import logging
logger = logging.getLogger('django')

cnn_path = Path(__file__).resolve().parent / 'CNN' / \
    '13_mfcc_abeja_reina_3_seg.h5'
model = keras.models.load_model(cnn_path)


class EstadoSaludColmena(APIView):

    def post(self, request):
        try:
            audio = request.FILES['audio'].file
            serie_tiempo, tasa_muestreo = librosa.load(audio, sr=None)
            mfcc_13 = librosa.feature.mfcc(
                y=serie_tiempo, sr=tasa_muestreo, n_mfcc=13, dct_type=2)
            prediccion = model.predict(mfcc_13)
            return Response(prediccion, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
