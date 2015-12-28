# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, session
from functools import wraps
import mysql.connector
from wand.image import Image
import os
from common import id_generator
import config as cfg

app = Flask(__name__)
app.secret_key = 'Qp%wJYTczZQq|6#aE#ae'


def check_auth(username_in, password_in):
    try:
        cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                                      password=cfg.MYSQL_PASSWORD,
                                      database=cfg.DATABASE)
        cursor = cnx.cursor()
        query = ("SELECT * FROM users")
        cursor.execute(query)
        rows = cursor.fetchall()

    except mysql.connector.Error as err:
        print("Mysql error: {}".format(err))
    finally:
        cursor.close()
        cnx.close()
    for (id, username, password) in rows:
        if username_in == username and password_in == password:
            session.user_id = id
            return True


def authenticate():
    message = {'message': "Authentication failed."}
    resp = jsonify(message)

    resp.status_code = 401
    resp.headers['WWW-Authenticate'] = 'Basic realm="Example"'

    return resp


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return authenticate()

        elif not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated

_VERSION = 1

@app.route('/v{}/image'.format(_VERSION), methods=["POST"])
@requires_auth
def rest_api():
    height = request.args.get('h')
    width = request.args.get('w')

    if request.headers['Content-Type'] == 'application/octet-stream':
        with Image(blob=request.data) as original_img:
            original_filename = cfg.ORIGINAL_FILENAME_PREFIX + '_' + \
                id_generator() + '.jpg'
            original_image_path = os.path.join(cfg.ORIGINAL_DIRECTORY,
                                               original_filename)
            original_img.save(filename=original_image_path)
            try:
                cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                                              password=cfg.MYSQL_PASSWORD,
                                              database=cfg.DATABASE)
                cursor = cnx.cursor()
                add_image = ("INSERT INTO images "
                             "(original_image_path, width, height, user_id) "
                             "VALUES (%s, %s, %s, %s)")
                image_data = (original_image_path, width, height,
                              session.user_id)
                cursor.execute(add_image, image_data)
                cnx.commit()
            except mysql.connector.Error as err:
                print("Mysql error: {}".format(err))
            finally:
                cursor.close()
                cnx.close()

        return "image get"
    else:
        return "415 Unsupported Media Type"

##################################################
# приложение
##################################################

if __name__ == '__main__':
    if not os.path.exists(cfg.ORIGINAL_DIRECTORY):
        os.makedirs(cfg.ORIGINAL_DIRECTORY)
    if not os.path.exists(cfg.RESIZED_DIRECTORY):
        os.makedirs(cfg.RESIZED_DIRECTORY)
    app.run()
