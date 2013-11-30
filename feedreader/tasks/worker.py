from argparse import ArgumentParser

from celery.bin.worker import worker

from feedreader.config import ConnectionConfig
from feedreader.tasks import Tasks


def get_args():
    parser = ArgumentParser()
    parser.add_argument('--config', default='deploy/production.yaml',
                        help='path to connection settings yaml')
    parser.add_argument('--number', type=int, default=0)
    return parser.parse_args()


def main():
    args = get_args()
    conn_config = ConnectionConfig.from_file(args.config)
    kwargs = {
        'concurrency': 1,
        'events': True,
        'hostname': '%h.worker.{}'.format(args.number),
        'loglevel': 'info',
    }

    tasks = Tasks(conn_config.amqp_uri)
    worker(app=tasks.app).run(**kwargs)


if __name__ == '__main__':
    main()
