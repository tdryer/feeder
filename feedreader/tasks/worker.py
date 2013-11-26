from celery.bin.worker import worker

from feedreader.config import Config
from feedreader.tasks import Tasks

if __name__ == '__main__':
    config = Config.from_args()
    tasks = Tasks(config.amqp_uri)

    kwargs = {
        'events': True,
        'loglevel': 'info',
    }
    worker(app=tasks.app).run(**kwargs)
