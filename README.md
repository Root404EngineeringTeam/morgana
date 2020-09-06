# Morgana

Herramienta para recopilar la información publica de un perfil de Instagram y sus interacciones (Fotos, Likes y Comentarios), para su posterior análisis.

# Instalación

    git clone https://github.com/Root404EngineeringTeam/morgana.git
    cd morgana
    pip install pipenv
    pipenv install
    pipenv shell
    python main.py --help

# Cookies

Aunque la cuenta que se va a analizar sea publica Intagram solo responde peticiones de usuarios logeados, por lo tanto hay que proveer al script de una sesión, para lo cual vamos a usar las cookies de sesión de una cuenta de Instagram.

Esta cookie de sesion la podemos obtener de varias formas, una de ellas es usar la consola de depuración de nuestro navegador, en la pestaña network, para interceptar las peticiones que se hacen a Instagram, entre estas peticiones vamoa ver unas entradas de la forma *?query_hash=XXXXX* estas nos sirven.

![cookies_01](https://edo0xff.me/cdn/morgana_2.png)

Click derecho > Copy > Copy as cURL

![cookies_01](https://edo0xff.me/cdn/morgana_3.png)

Eso lo pegamos en un archivo llamado *cookies.txt* (crealo si no existe) dentro de *morgana*, tendríamos algo así:

![cookies_01](https://edo0xff.me/cdn/morgana_4.png)

Aunque solo nos quedamos con las cookies, es decir lo que se encuentra dentro de las comillas sencillas en *-H 'cookie: xxxxxxxxxxx'*, siendo este el resultado final:

![cookies_01](https://edo0xff.me/cdn/morgana_5.png)

Guardamos y listo.

# Scraping

    python main.py -u <nombre_de_usuario> --scrap

# Estadisticas básicas

    python main.py -u <nombre_de_usuario> --statistics

# Realizar una busqueda en el perfil

    python main.py -u <nombre_de_usuario> --statistics --search <palabra_clave>

# Generar reporte en HTML

    python main.py -u <nombre_de_usuario> --statistics --html

# Colaboradores

Eduardo Becerril [@edo0xff](https://github.com/edo0xff)
Álvaro Stagg [@Algoru](https://github.com/Algoru)
