# [API COLMENA ABEJA](#indice)

El presente proyecto fue desarrollado durante el ramo **trabajo de titulo**, para optar al titulo de **ingenierío civil informático** en la Universidad Técnica
Federico Santa María (UTFSM). API que contiene el extractor de características y la red neuronal convolucional (CNN), para detectar la presencia o ausencia de abeja reina dentro de la colmena. Si quiere facilitar el despliegue del sistema, mediante automatización, vaya al repositorio [APP_COLMENA_ABEJA](https://github.com/cristopher1/app_colmena_abeja)

### <a id="indice"></a> Índice

* <a id="introduccion"></a>[Introducción](#Introducción)
* <a id="pre-rrequisitos"></a> [Prerrequisitos](#Prerrequisitos)
* <a id="descarga"></a> [Descargar el repositorio](#Descargar-el-repositorio)
* <a id="entorno"></a>[Variables de entorno](#Variables-de-entorno)
  * <a id="entorno-django"></a>[Variables de entorno para configurar DJANGO](#Variables-de-entorno-para-configurar-DJANGO)
  * <a id="entorno-api"></a>[Variables de entorno para configurar la API](#Variables-de-entorno-para-configurar-la-API)
* <a id="dockerfile"></a>[Docker](#Docker)
* <a id="run"></a>[Ejecutar la aplicación](#Ejecutar-la-aplicación)

## <a id="Introducción"></a> [Introducción](#introduccion)

El presente repositorio contiene la API utilizada por el sistema APP COLMENA ABEJA. Esta API contiene un extractor de características y una CNN, los cuales son utilizados para determinar la presencia o ausencia de abeja reina. A continuación se dan algunos detalles del funcionamiento de la API a grandes rasgos.

* Para determinar la presencia o ausencia de abeja reina, se le envia un archivo de audio a la API (la cual contiene los zumbidos emitidos por la colmena de abeja, duración mínima del archivo de audio 3 segundos) y la zona horaria del cliente web. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L302-L303
  
* Luego de recibir el archivo de audio, se procede a obtener su contenido **serie de tiempo de la amplitud** y **tasa de muestreo** (la CNN fue entrenada con audios con tasa de muestreo de 44100 muestras por segundo, por lo tanto la tasa de muestreo usada por el sistema es de 44100). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L304

* En caso de que el archivo de audio tenga una duración mayor a 3 segundos, solo se toman los primeros 3 segundos de los zumbidos presentes en el archivo de audio (la CNN esta diseñada para procesar solamente audios con duración de 3 segundos). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L305

* Posteriormente se usa el extractor de características para obtener la información relevante de la muestra de audio, se extraen 13 MFCCs (Coeficientes Cepstrales en la Frecuencia de Mel). https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L306-L307

* La matriz que contiene los 13 MFCCs es redimensionada para calzar con el tamaño de matriz recibida por la capa de entrada de la CNN. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L308 De esta manera puede ser pasada a la CNN con la finalidad de obtener una predicción. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L309-L311

* Luego de obtener la predicción, se obtiene la fecha en la cual el cliente web ha enviado el archivo a la API. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L312 Y Se formatean los resultados. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L313

* Finalmente el resultado es enviado al cliente web. https://github.com/cristopher1/api_colmena_abeja/blob/63e36a2b23169d6c7f005c5ee01bff81eb46aa90/api/views.py#L314

## <a id="Prerrequisitos"></a> [Prerrequisitos](#pre-rrequisitos)

El sistema ha sido probado en SO Windows 11.

* Docker Desktop con Servidor WSL 2. Ver documentación sobre [Docker Desktop para Windows](https://docs.docker.com/desktop/install/windows-install/)

## <a id="Descargar-el-repositorio"></a> [Descargar el repositorio](#descarga)

Para descargar el repositorio use:

```console
git clone git@github.com:cristopher1/api_colmena_abeja.git
```

## <a id="Variables-de-entorno"></a> [Variables de entorno](#entorno)

La información de las variables de entorno se encuentra dentro del archivo .env.example, que se encuentra dentro de la carpeta api. https://github.com/cristopher1/api_colmena_abeja/blob/60a27b2363143c70c78f13bb325a647a13eb1468/api/.env.example#L1-L59

### <a id="Variables-de-entorno-para-configurar-DJANGO"></a> [Variables de entorno para configurar DJANGO](#entorno-django)

* ```DEBUG```: Activa el modo depurador, **en producción colocar el valor False**.
  
* ```SECRET_KEY```: Clave asociada a seguridad de DJANGO.
  
* ```ALLOWED_HOSTS```: Lista de HOST a los que puede responder DJANGO.
  
* ```CORS_ALLOWED_ORIGINS```: Lista de los servidores que estan autorizados para realizar una petición de origen cruzado a DJANGO.

### <a id="Variables-de-entorno-para-configurar-la-API"></a> [Variables de entorno para configurar la API](#entorno-api)

* ```VENTANA_TIEMPO```: Tamaño de la ventana de tiempo, de la cual se extraen los datos de los archivos de audio, para que la API pueda identificar el estado de
la colmena. (Para la CNN que el sistema usa, este valor es 3).

* ```N_CANAL```: Número de canales que tienen las características extraídas de los archivos de audio, para que la CNN pueda procesarlos. (Para las características
que el sistema procesa, este valor es 1).

## <a id="Docker"></a> [Docker](#dockerfile)

El sistema incluye un archivo **Dockerfile**, para poder facilitar su despliegue.
https://github.com/cristopher1/api_colmena_abeja/blob/60a27b2363143c70c78f13bb325a647a13eb1468/Dockerfile#L1-L59 Se puede apreciar que el Dockerfile ha sido
dividido en 3 etapas: base, development y production.

* En la etapa development: Se incluyen herramientas para desarrollo, como nano. Tambíén se despliega el sistema usando el servidor de desarrollo de DJANGO
utilizando el puerto 8000 para escuchar las peticiones web.
https://github.com/cristopher1/api_colmena_abeja/blob/60a27b2363143c70c78f13bb325a647a13eb1468/Dockerfile#L42

* En la etapa production: Se despliega la API usando unicorn y se usa el puerto 443 para escuchar las peticiones web.
https://github.com/cristopher1/api_colmena_abeja/blob/60a27b2363143c70c78f13bb325a647a13eb1468/Dockerfile#L59

## <a id="Ejecutar-la-aplicación"></a> [Ejecutar la aplicación](#run)

Para ejecutar la aplicación siga los siguientes pasos.

* **Nota: El archivo Dockerfile de este repositorio utiliza multi-stage, por lo que no debe olvidar habilitar el docker BuildKit al momento de**
**ejecutar la aplicación.**

* **Nota: A partir de la versión 23.0 de Docker Desktop y Docker Engine se usa de forma predeterminada el BuildKit por lo que no es necesario habilitarlo**
**de forma manual.**

1. Ingrese a la carpeta api_colmena_abeja/api (por la teminal o interfaz gráfica).
2. Cree un archivo llamado .env (en la misma carpeta donde esta el archivo .env.example)
3. Copie el contenido del archivo .env.example a .env
4. Si gusta, modifique los valores del archivo .env
6. Abra una terminal e ingrese a la carpeta api_colmena_abeja
8. Ejecute los siguientes comandos:
   * Para modo desarrollo:
     * Crear la imagen:
       ```console
       docker build --target development -t api_colmena_abeja_dev .
       ```
     * Ejecutar el contenedor:
       ```console
       docker run -p host_port:8000 --env-file api/.env api_colmena_abeja_dev
       ```
       Reemplace **host_port** por el puerto en su host, por el cual las peticiones web serán redirigidas al contenedor docker.
       
   * Para modo producción:
     * Crear la imagen:
       ```console
       docker build --target production -t api_colmena_abeja_prod .
       ```
     * Ejecutar el contenedor:
       ```console
       docker run -p host_port:443 --env-file api/.env api_colmena_abeja_prod
       ```
       Reemplace **host_port** por el puerto en su host, por el cual las peticiones web serán redirigidas al contenedor docker.

**Nota: Para modo producción no use directamente gunicorn para servir el sistema. Conecte el contenedor con la API a un servidor de producción como nginx,**
**para redirigir las peticiones al contenedor de la API.**

Una vez completados los pasos, el sistema debería estar ejecutandose en `http://localhost:host_port`
