from celery.schedules import schedule

CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'process_image.process_images_queue',
        'schedule': schedule(run_every=30),
    },
}
