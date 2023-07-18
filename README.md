# [API COLMENA ABEJA](#indice)

El presente proyecto fue desarrollado durante el ramo **trabajo de titulo**, para optar al titulo de **ingenierío civil informático** en la Universidad Técnica
Federico Santa María (UTFSM). API que contiene el extractor de características y la red neuronal convolucional (CNN), para detectar la presencia o ausencia de abeja reina dentro de la colmena.

### <a id="indice"></a>Índice

* <a id="introduccion"></a>[Introducción](#Introducción)
* <a id="pre-rrequisitos"></a> [Prerrequisitos](#Prerrequisitos)
* <a id="descarga"></a> [Descargar el repositorio](#Descargar-el-repositorio)
* <a id="entorno"></a>[Variables de entorno](#Variables-de-entorno)
  * <a id="entorno-frontend"></a>[Para el FRONTEND](#Para-el-FRONTEND)
  * <a id="entorno-api"></a>[Para la API](#Para-la-API)
* <a id="run"></a>[Ejecutar la aplicación](#Ejecutar-la-aplicación)

## [Introducción](#introduccion)

El presente repositorio contiene la API utilizada por el sistema APP COLMENA ABEJA. Esta API contiene un extractor de características y una CNN, los cuales son utilizados para determinar la presencia o ausencia de abeja reina. A continuación se dan algunos detalles del funcionamiento de la API a grandes rasgos.

* Para determinar la presencia o ausencia de abeja reina, se le envia un archivo de audio a la API (la cual contiene los zumbidos emitidos por la colmena de abeja, duración mínima del archivo de audio 3 segundos) y la zona horaria del cliente web. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L302-L303
  
* Luego de recibir el archivo de audio, se procede a obtener su contenido **serie de tiempo de la amplitud** y **tasa de muestreo** (la CNN fue entrenada con audios con tasa de muestreo de 44100 muestras por segundo, por lo tanto la tasa de muestreo usada por el sistema es de 44100). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L304

* En caso de que el archivo de audio tenga una duración mayor a 3 segundos, solo se toman los primeros 3 segundos de los zumbidos presentes en el archivo de audio (la CNN esta diseñada para procesar solamente audios con duración de 3 segundos). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L305

* Posteriormente se usa el extractor de características para obtener la información relevante de la muestra de audio, se extraen 13 MFCCs (Coeficientes Cepstrales en la Frecuencia de Mel). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L306-L307

* La matriz que contiene los 13 MFCCs es redimensionada para calzar con el tamaño de matriz recibida por la capa de entrada de la CNN. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L308 De esta manera puede ser pasada a la CNN con la finalidad de obtener una predicción. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L309-L311

* Luego de obtener la predicción, se obtiene la fecha en la cual el cliente web ha enviado el archivo a la API. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L312 Y Se formatean los resultados. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L313

* Finalmente el resultado es enviado al cliente web. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L314

## [Prerrequisitos](#pre-rrequisitos)

El sistema ha sido probado en SO Windows 11.

* Docker Desktop con Servidor WSL 2. Ver documentación sobre [Docker Desktop para Windows](https://docs.docker.com/desktop/install/windows-install/)

## [Descargar el repositorio](#descarga)

Para descargar el repositorio use:

```python
git clone --recurse-submodules git@github.com:cristopher1/app_colmena_abeja.git
```

## [Variables de entorno](#entorno)

La información de las variables de entorno se encuentra dentro del archivo .env.example, este archivo tiene 8 variables, que son usadas dentro del archivo
docker-compose.yml para establecer la forma en que se va a desplegar el sistema. A continuación se muestra su estructura.

https://github.com/cristopher1/app_colmena_abeja/blob/9bb1a74002ca747bb5d142e7fb5a44329cb35d2c/docker-compose.yml#L1-L21

A continuación se muestran las variables de entorno usadas en el archivo docker-compose.yml presentado anteriormente.

### [Para el FRONTEND](#entorno-frontend)

https://github.com/cristopher1/app_colmena_abeja/blob/23bea7412bc6b070c52e0b026cf7102eb3c47060/.env.example#L7-L22

* `FRONTEND_PROJECT_DIRECTORY`: Nombre de la carpeta que contiene el FRONTEND y en su raíz esta el
archivo Dockerfile. Debería llamarse **frontend_app_colmena_abeja**

* `FRONTEND_STAGE`: Modo en el que se desplegará el FRONTEND. development o production

* `FRONTEND_HOST_PORT`: Puerto en el HOST, donde el FRONTEND escucha peticiones

* `FRONTEND_CONTAINER_PORT`: Puerto en el contenedor, donde el FRONTEND escucha peticiones

### [Para la API](#entorno-api)

https://github.com/cristopher1/app_colmena_abeja/blob/23bea7412bc6b070c52e0b026cf7102eb3c47060/.env.example#L24-L39

* `API_PROJECT_DIRECTORY`: Nombre de la carpeta que contiene la API y en su raíz esta el
archivo Dockerfile. Debería llamarse **api_colmena_abeja**

* `API_STAGE`: Modo en el que se desplegará la API. development o production

* `API_HOST_PORT`: Puerto en el HOST, donde la API escucha peticiones

* `API_CONTAINER_PORT`: Puerto en el contenedor, donde la API escucha peticiones

## [Ejecutar la aplicación](#run)

Para ejecutar la aplicación siga los siguientes pasos.

* **Nota: Los archivos Dockerfile presentes en el repositorio api_colmena_abeja y frontend_app_colmena_abeja utilizan**
**Multi-stage, por lo que no debe olvidar habilitar el docker BuildKit al momento de ejecutar la aplicación.**

* **Nota: A partir de la versión 23.0 de Docker Desktop y Docker Engine se usa de forma predeterminada el BuildKit**
**Por lo que no es necesario habilitarlo de forma manual.**

1. Ingrese a la carpeta app_colmena_abeja.
2. Cree un archivo llamado .env (en la misma carpeta donde esta el archivo .env.example)
3. Copie el contenido del archivo .env.example a .env
4. Si gusta, modifique los valores del archivo .env
5. Repita el paso 2, 3 y 4 en api_colmena_abeja y frontend_app_colmena_abeja
6. Abra una terminal
7. Desde la terminal, ingrese a la carpeta app_colmena_abeja
8. Ejecute el comando `docker-compose up --build`

Una vez completados los pasos, el sistema debería estar ejecutandose en `http://localhost:${FROTEND_HOST_PORT}`

https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/Dockerfile#L1-L59
