# -*- coding: utf-8 -*-
from wand.image import Image
import os
import mysql.connector
from celery import Celery
from common import id_generator
import config as cfg

celery = Celery('tasks')
celery.config_from_object('celeryconfig')


@celery.task
def process_images_queue():
    try:
        cnx = mysql.connector.connect(user=cfg.MYSQL_USER,
                                      password=cfg.MYSQL_PASSWORD,
                                      database=cfg.DATABASE)
        cursor = cnx.cursor()
        query = ("SELECT id, original_image_path, "
                 "width, height FROM images "
                 "WHERE resized_image_path IS NULL")

        cursor.execute(query)
        rows = cursor.fetchall()

        for (id, original_image_path, width, height) in rows:
            with Image(filename=original_image_path) as original_img:
                resized_img = original_img.clone()
                resized_img.compression_quality = 85
                resized_img.resize(int(height), int(width))

                resized_filename = cfg.RESIZED_FILENAME_PREFIX + '_' + \
                    id_generator() + '.jpg'
                resized_image_path = os.path.join(cfg.RESIZED_DIRECTORY,
                                                  resized_filename)
                resized_img.save(filename=resized_image_path)

                cursor.execute("""
                UPDATE images
                SET resized_image_path=%s
                WHERE id=%s
                """, (resized_image_path, id))

        cnx.commit()
    except mysql.connector.Error as err:
        print("Mysql error: {}".format(err))
    finally:
        cursor.close()
        cnx.close()
