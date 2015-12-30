# -*- coding: utf-8 -*-
from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode
import config as cfg

##################################################
# создание таблиц в mysql
##################################################

TABLES = {}
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `username` varchar(255) UNIQUE NOT NULL,"
    "  `password` varchar(255) UNIQUE NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['images'] = (
    "CREATE TABLE `images` ("
    "  `id` int(11) NOT NULL AUTO_INCREMENT,"
    "  `original_image_path` varchar(255),"
    "  `resized_image_path` varchar(255),"
    "  `width` int(11),"
    "  `height` int(11),"
    "  `user_id` int(11) NOT NULL,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")


cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                              password=cfg.MYSQL_PASSWORD)

cursor = cnx.cursor()


def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT "
            "CHARACTER SET 'utf8'".format(cfg.DATABASE))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

try:
    cnx.database = cfg.DATABASE
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor)
        cnx.database = cfg.DATABASE
    else:
        print(err)
        exit(1)

for name, ddl in TABLES.iteritems():
    try:
        print("Creating table {}: ".format(name), end='')
        cursor.execute(ddl)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")

cursor.close()
cnx.close()

##################################################
# добавление демо-данных в mysql
##################################################

cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                              password=cfg.MYSQL_PASSWORD,
                              database=cfg.DATABASE)

cursor = cnx.cursor()

try:
    add_user = ("INSERT INTO users "
                "(username, password) "
                "VALUES (%s, %s)")
    user_data = ('admin', 'secret')
    cursor.execute(add_user, user_data)
    cnx.commit()
except mysql.connector.Error as err:
    print("Mysql error: {}".format(err))
finally:
    cursor.close()
    cnx.close()

##################################################
# добавление индекса для resized_image_path
##################################################

cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                              password=cfg.MYSQL_PASSWORD,
                              database=cfg.DATABASE)

cursor = cnx.cursor()

try:
    add_index = ("CREATE INDEX idx1 ON images(resized_image_path(1))")
    cursor.execute(add_index)
    cnx.commit()
except mysql.connector.Error as err:
    print("Mysql error: {}".format(err))
finally:
    cursor.close()
    cnx.close()
