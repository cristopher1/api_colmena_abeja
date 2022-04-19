FROM python:3.10

RUN apt-get update && apt-get install -y libsndfile1-dev ffmpeg

WORKDIR /api_colmena_abeja

COPY requirements.txt ./

RUN pip --no-cache-dir install -r requirements.txt

COPY . ./

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
