# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, session, Response
from functools import wraps
import mysql.connector
from wand.image import Image
import os
from common import id_generator
import config as cfg

app = Flask(__name__)
app.secret_key = 'Qp%wJYTczZQq|6#aE#ae'


############################################################
# application
############################################################

def init_env():
    if not os.path.exists(cfg.ORIGINAL_DIRECTORY):
        os.makedirs(cfg.ORIGINAL_DIRECTORY)
    if not os.path.exists(cfg.RESIZED_DIRECTORY):
        os.makedirs(cfg.RESIZED_DIRECTORY)


def init_users():
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        query = ("SELECT id, username, password FROM users")
        cursor.execute(query)
        cached_users = cursor.fetchall()
        cached_users_dict = {user[1]: (user[0], user[2])
                             for user in cached_users}
        return cached_users_dict
    except mysql.connector.Error as err:
        print("Mysql error: {}".format(err))
        exit(1)
    finally:
        cursor.close()
        cnx.close()


def check_auth(username_in, password_in):
    user = cached_users_dict.get(username_in)
    if not user:
        return False
    elif user[1] == password_in:
        session.user_id = user[0]
        return True
    else:
        return False


def no_authenticate():
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
            return no_authenticate()
        elif not check_auth(auth.username, auth.password):
            return no_authenticate()
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
                cnx_insert = cnxpool.get_connection()
                cnx_insert_cursor = cnx_insert.cursor()
                add_image = ("INSERT INTO images "
                             "(original_image_path, width, height, user_id) "
                             "VALUES (%s, %s, %s, %s)")
                image_data = (original_image_path, width, height,
                              session.user_id)
                cnx_insert_cursor.execute(add_image, image_data)
                cnx_insert.commit()
            except mysql.connector.Error as err:
                return Response(
                    "Mysql error: {}".format(err), 500)
            finally:
                cnx_insert_cursor.close()
                cnx_insert.close()
        return "image get"
    else:
        return Response(
            'Unsupported Media Type', 415)

##################################################
# приложение
##################################################

if __name__ == '__main__':
    init_env()

    dbconfig = {
        "database": cfg.DATABASE,
        "user":     cfg.MYSQL_USER,
        "password":  cfg.MYSQL_PASSWORD
    }

    cnxpool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool",
                                                          pool_size=3,
                                                          **dbconfig)
    cached_users_dict = init_users()
    app.run()
