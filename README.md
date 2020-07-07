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

Edita los tweets uno a uno y pulsa _Añadir tweet al hilo_ para pasar a editar el siguente.

### Activar/Desactivar notificaciones

Es posible activar y desactivar las notificaciones de la actividad de los tweets publicados enviando un mensaje con el siguiente comando:

```bash
/noti
```

## Guía del administrador

Hay disponibles una serie de comandos exclusivos de una serie de usuarios (de Twitter) que se designan como administradores. Estos permiten evitar comportamientos indeseados, dando a los administradores la posibilidad de evitar que un usuario twitee durante o tiempo o indefinidamente.

### Gestión del grupo de administradores

Es necesario crear una cuenta de administrador de Django para gestionar los administradores de Twitter. Para ello, se ejecuta el siguiente comando en la terminal, y se introduce la información que requiera el programa.

```bash
python cotilleosfugrbot/manage.py createsuperuser
```

Una vez creada la cuenta de administrador de Django es posible acceder al panel de control del bot a través de:

```url
APP_URL/admin
```
![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/login.png)

Tras iniciar sesión, se añade un administrador clicando en User -> Añadir
![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/control_panel.png)

Para añadir un usuario de Twitter al grupo de administradores es necesario conocer su id de Twitter, para ello son útiles herramientas como: https://tweeterid.com/. Una vez conocido el id del usuario a añadir como administrador, este se introduce en el campo "Id" de la imagen, y se marca la casilla is_admin. Para guardar los cambios se clica en "Grabar"

![alt text](https://raw.githubusercontent.com/JcJ99/CotilleosFUGR-BOT/master/readme_files/add_user.png)

### Comandos de administrador

Los administradores tienen acceso a comandos adicionales a través de mensajes directos del bot.

#### Ban

Es posible evitar que un usuario publique mensajes nunca más haciendo uso del comando:

```bash
/ban user <user_name (@)>
/ban link <bot_tweet_link>
```

Existen dos formas de banear a un usuario. La primera de ellas es conociendo su nombre de usuario de Twitter y la segunda es conociendo el link de un tweet publicado por el usuario haciendo uso del bot. La identidad del usuario será revelada incluso si se hace uso del segundo método.

#### Timeout

También es posible evitar que un usuario twitee durante un tiempo determinado. Para ello se hace uso del comando:

```bash
/timeout user <user_name (@)>
/timeout link <bot_tweet_link>
```

El funcionamiento es análogo al del comando /ban.

#### Free

Elimina el castigo impuesto sobre un usuario determinado:

```bash
/free <user_name (@)>
```

#### List

Muestra una lista de todos los usuarios castigados:

```bash
/list
```

#### Delete

Elimina un tweet publicado por cualquier usuario:

```bash
/delete <tweet_link>
```


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
APP_URL = "https://xxxxx.example.com"
```

La variable **TWITTER_ENV_NAME** es el nombre del entorno de la aplicación registrada en Twitter Developers. https://developer.twitter.com/en/docs/basics/developer-portal/guides/dev-environments.html

Puede cambiar el número máximo de tweets que un usuario puede enviar en una hora ajustando la variable **MAX_TWEETS_PER_HOUR**

Introduzce la URI de una base de datos en la que el bot guardará ls ids de los usuario del bot así como las ids de los tweets publicados en la variable DATABASE_URL. Es posible configurar cualquier tipo de base de datos en el archivo cotilleosfugrbot.settings.py https://docs.djangoproject.com/en/3.0/ref/databases/. Recuerda crear un usuario asociado al bot en la base de datos.

Ajusta el límite de puntuación negativa del filtro de spam con un valor entre 0 y -1. Siendo cero el más estricto. Se recomienda un valor de 0, pues es una característica experimental.

Apaga o enciende el detector de texto sin sentido asignando los valores 0 o 1 a la variable SCORE_ZERO_ERROR, se recomienda que se mantenga apagada para evitar falsos positivos.

Todas estas configuraciones pueden ser ajustadas desde variables de entorno con el mismo nombre.

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

```Shell
python manage.py migrate && python manage.py chatbot makemigrations && python manage.py migrate
```

7. Iniciar la aplicación utilizando gunicorn:

```bash
gunicorn --chdir cotilleosfugr cotilleosfugr.wsgi
```

Este repositorio está preparado para funcionar directamente si se aloja en heroku.
