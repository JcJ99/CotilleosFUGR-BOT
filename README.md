# CotilleosFUGR BOT

@CotilleosFUGR es una cuenta de Twitter cuya finalidad es actuar a modo de tablón de anuncios en el cual cualquier persona puede publicar un mensaje de forma anónima. La función de este bot es crear una interfaz a través de los mensajes privados de Twitter que permita que los usuarios publiquen los tweets que deseen de forma instantánea además de proporcionar un sistema de notificaciones para que los usuarios conozcan las interacciones con los tweets que han publicado para que la experiencia se asemeje en la mayor medida posible a la que los usuarios tendrían si publicaran los tweets desde su cuenta

## Guía del usuario

### Publicar un tweet sólo con texto

Para publicar un tweet que no cite a otro ni cuente con archivos adjuntos basta con enviar un mensaje con el texto que desea publicarse. En caso de que existan erratas en el texto basta con mandar otro mensaje con el texto corregido. Una vez el texto sea  el correcto pulse el botón _Enviar tweet_.

![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/mensaje%20s%C3%B3lo%20con%20texto.png)

### Adjuntar un archivo en el tweet

Envía archivos de uno en uno para adjuntarlos en el tweet. Es posible adjuntar hasta un máximo de 4 fotos, 1 vídeo o un gif. No es posible combinar diferentes tipos de archivos.

![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/mensaje%20con%20foto.png)

### Citar un tweet

Para citar un tweet basta con enviar el link del mismo, no es posible citar tweets sin introducir texto

![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/mensaje%20con%20cita.png)

### Publicar un hilo

Edita los tweets uno a uno y pulsa _Añadir tweet al hilo_ para pasar a editar el siguente

## Set-Up

1. Clonar el código desde este repositorio

```bash
git clone https://github.com/JcJ99/CotilleosFUGR-BOT.git
```

2. Instala las librerías necesarias

```bash
sudo pip install -r requirements.txt
``` 

3. Editar el archivo config.py

Introduce en la variable APP_URL el link en el que está funcionando el bot

```Python
APP_URL = "https://xxxxx.herokuapp.com"
```

La variable **TWITTER_ENV_NAME** es el nombre del entorno de la aplicación registrada en Twitter Developers. https://developer.twitter.com/en/docs/basics/developer-portal/guides/dev-environments.html

Puede cambiar el número máximo de tweets que un usuario puede enviar en una hora ajustando la variable **MAX_TWEETS_PER_HOUR**

Introduzce la URI de una base de datos en la que el bot guardará ls ids de los usuario del bot así como las ids de los tweets publicados en la variable DATABASE_URL. Si para la base de datos usas PostgrelSQL rellena los campos, _user, pw..._ en caso contrario introduce la url de tu base de datos. Recuerda crear un usuario asociado al bot en la base de datos.

Ajusta el límite de puntuación negativa del filtro de spam con un valor entre 0 y -1. Siendo cero el más estricto. Se recomienda un valor de -0.85

Apaga o enciende el detector de texto sin sentido asignando los valores 0 o 1 a la variable SCORE_ZERO_ERROR, se recomienda que se mantenga apagada para evitar falsos positivos.

Todas estas configuraciones pueden ser ajustadas desde variables de entorno.

4. Introducir claves del servicio IBM Natural Languaje Understanding

El bot hace uso de este servicio para el fitro de Spam https://www.ibm.com/watson/services/natural-language-understanding/. Es necesario crear una cuenta y obtener una clave para su uso.

Introduce la url de la región de servicio deseada en la variable ibm_language_url y la clave en la variable ibm_key en el archivo Auths.py

Todas estas configuraciones pueden ser ajustadas desde variables de entorno.

5. Introducir keys de autenticación de la api de twitter

Estas se pueden introucir en el archivo Auths.py en forma de string o pueden ser añadidas como variables de entorno con los nombres:

```Python
"CONSUMER_KEY", "CONSUMER_SECRET_KEY", "TOKEN_KEY", "TOKEN_SECRET_KEY"
```
6. Configurar base de datos

Realiza la migración de la base de datos con el comando:

```Pyhton
pyhton manage.py db init && pyhton manage.py db migrate && pyhton manage.py db upgrade
```

7. Iniciar la aplicación utilizando gunicorn:

```bash
gunicorn wsgi
```
