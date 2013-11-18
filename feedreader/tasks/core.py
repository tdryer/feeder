from celery import Celery


class Tasks(object):

    def __init__(self, debug=False):
        self.app = Celery()
        self.app.conf.update(
            CELERY_ACCEPT_CONTENT=['json'],
            CELERY_ALWAYS_EAGER=True,
            CELERY_ENABLE_UTC=True,
            CELERY_TASK_SERIALIZER='json',
            CELERY_RESULT_SERIALIZER='json',
            CELERY_TIMEZONE='America/Vancouver',
        )

        if not debug:
            self.app.conf.update(
                BROKER_URL='amqp://guest:guest@novus.mtomwing.com:5673//',
                CELERY_ALWAYS_EAGER=False,
                CELERY_RESULT_BACKEND='amqp',
            )

        # register tasks with celery
        self.fetch_feed = self.app.task()(self.fetch_feed)

    # celery tasks

    def fetch_feed(self, url):
        return 'hola bro'
