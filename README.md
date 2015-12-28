## Установка окружения

### Установка Imagemagick и python-обертки Imagemagick wand

* `sudo apt-get install imagemagick`
* `sudo apt-get install libmagickwand-dev`
* `sudo apt-get install python-wand`

### Установка mysql

* `sudo apt-get install apache2 apache2-doc`
* `sudo apt-get install mysql-server`
* `sudo mysql_secure_installation`

### Установка celery и rabbitmq-server

* `wget https://www.rabbitmq.com/rabbitmq-signing-key-public.asc`
* `sudo apt-key add rabbitmq-signing-key-public.asc`
* `sudo apt-get install rabbitmq-server`

### Клонирование проекта

* `git clone http://gitlab.simbirsoft/renat.abbyazov/image-web-service.git`

### Создание python virtual environment

* `cd image-web-service/`
* `sudo apt-get install python-virtualenv`
* `virtualenv venv_iws`
* `source venv_iws/bin/activate`
* `sudo apt-get install rabbitmq-server`
* `pip install flask celery`
* `pip install --allow-external mysql-connector-python mysql-connector-python`

## Запуск приложения

Сначала нужно создать таблицы пользователей users и изображений images в базе данных mysql.
* `python sql.py`

Кроме этого, добавляется один тестовый пользователь в таблицу users.

Можно проверить создание таблиц mysql в консоли
* `mysql -uroot -ppassword`
* `mysql> select * from users_images.users;`
* `mysql> select * from users_images.images;`

Далее необходимо запустить rabbitmq-server

* `sudo rabbitmq-server`

и приложение flask

* `python app.py`

## Использование приложения
В отдельной вкладке терминала нужно запустить очередь заданий celery,
которая отвечает за фоновую обработку изображений с периодичностью 30 сек
(значение установлено в celeryconfig.py).

* `celery -A process_image worker --loglevel=info --beat`

Далее добавляем изображение через http запрос
от пользователя c значениями имени пользователя, пароля,
пути к изображению с использованием curl
* `curl -v -H "Content-type: application/octet-stream" -u "admin:secret" -X POST "http://127.0.0.1:5000/v1/image?h=120&w=120" --data-binary "@seam.jpg"`

Если после этого сделать запрос в базу данных (в течении 30 сек)
то можно увидеть, что оригинальное изображение сохранено на диск в папку
original/ , кроме того в таблицу добавлены параметры запроса для высоты и ширины
изображения, которые используются celery для работы с изображениями.

* `mysql> select * from users_images.images;`
значение original_image_path равно
original/original_us6pqiq3745ge0z.jpg,
resized_image_path равно NULL, height - 120,
width - 120.

После выполнения задачи celery колонка resized_image_path
будет заполнена значением пути к преобразованному изображению,
а преобразованное изображение будет сохранено в папку
resized/.

## Описание файлов проекта


* `app.py`

приложение flask, в котором осуществляется авторизация и сохранение изображения
от соответствующего пользователя

* `celeryconfig.py`

параметры celery, в частности значение интервала, с которым выполяется
фоновая задача преобразования изображения

* `common.py`

генератор суффикса для имени сохраняемого изображения

* `config.py`

параметры mysql и названия имен и директорий для изображений

* `process_image.py`

фоновая задача celery - преобразование и сохранение изображений

* `sql.py`

создание таблиц баз данный mysql
