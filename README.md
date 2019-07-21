# CotilleosFUGR BOT

@CotilleosFUGR es una cuenta de Twitter cuya finalidad es actuar a modo de tablón de anuncios en el cual cualquier persona puede publicar un mensaje de forma anónima. La función de este bot es crear una interfaz a través de los mensajes privados de Twitter que permita que los usuarios publiquen los tweets que deseen de forma instantánea además de proporcionar un sistema de notificaciones para que los usuarios conozcan las interacciones con los tweets que han publicado para que la experiencia se asemeje en la mayor medida posible a la que los usuarios tendrían si publicaran los tweets desde su cuenta

## Guía del usuario

Publicar un tweet utilizando este bot es extremadamente sencillo, basta con enviar el texto del tweet a publicar a través mensaje privado a la cuenta @CotilleosFUGR. El bot te contestará con un mensaje con todas las acciones posibles en forma de botones interactivos. El uso de estos botones ni siquiera es obligatorio pues el bot es capaz de reconocer si se le ha enviado un link, una foto, simple texto o varias cosas a la vez y responder en consecuencia. 
Esta forma amigable de interactuar con el usuario permite símplemente seguir los pasos que se muestran en pantalla para publicar un tweet, sin embargo a continuación se explica como realizar todas las acciones que permite llevar a cabo este bot

### Publicar un tweet sólo con texto

Para publicar un tweet que no cite a otro ni cuente con archivos adjuntos basta con enviar un mensaje con el texto que desea publicarse. En caso de que existan erratas en el texto basta con mandar otro mensaje con el texto corregido. Una vez el texto sea  el correcto pulse el botón "Enviar tweet".

## Set-Up

Esta aplicación está preparada para trabajar en un PC, siendo esta totalmente portable o en el servicio de Hosting de aplicaciones web Heroku. Para configurar esta aplicación se han de seguir los siguientes pasos:

1. Clonar el código desde este repositorio

```
git clone https://github.com/JcJ99/CotilleosFUGR-BOT.git
```

**Si estás trabajando en un PC** se han de instalar una serie de librerías. Para ello usar el comando:

```
sudo pip install -r requirements.txt
``` 

2. Editar el archivo config.py

**Si la aplicación se aloja en Heroku** Es necesario introducir la variable APP_URL. El valor de esta debe ser la url en la que trabajará la aplicación. Si se trabaja en un PC esta va a ser ignorada

```
APP_URL = "https://xxxxx.herokuapp.com"
```

La variable **TWITTER_ENV_NAME** es el nombre del entorno de la aplicación registrada en Twitter Developers. https://developer.twitter.com/en/docs/basics/developer-portal/guides/dev-environments.html

Puede cambiar el número máximo de tweets que un usuario puede enviar en una hora ajustando la variable **MAX_TWEETS_PER_HOUR**

3. Introducir keys de autenticación de la api de twitter

Estas se pueden introucir en el archivo Auths.py en forma de string o pueden ser añadidas como variables de entorno con los nombres:

```
"CONSUMER_KEY", "CONSUMER_SECRET_KEY", "TOKEN_KEY", "TOKEN_SECRET_KEY"
```

**NOTA**: Las variables de entorno se han de crear en el servidor de Heroku en caso de estar la aplicación alojada allí

4. **Si estás trabajando en un PC** basta ya con iniciar la aplicación utilizando Python 3.7:

```
python3 cotilleosfugrbot.py
```

**Si la aplicación se aloja en Heroku** has de crear ahora la aplicación en el sitio web de Heroku y crear la variable de entorno en el servidor:

```
ONHEROKU=1
```

Después basta con subir **todos** los archivos descargados inicialmente y modificados en el proceso de configuración al servidor de Heroku