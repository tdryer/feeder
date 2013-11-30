from argparse import ArgumentParser

import yaml


class ConnectionConfig(object):

    @classmethod
    def from_file(cls, filepath):
        raw_config = yaml.load(open(filepath).read())

        return cls(raw_config.get('amqp', ''),
                   raw_config.get('database', 'sqlite://'))

    def __init__(self, amqp, database):
        self.amqp_uri = amqp
        self.database_uri = database


class FeederConfig(object):

    @classmethod
    def from_args(cls):
        parser = ArgumentParser()
        parser.add_argument('--config', default='deploy/dev.yaml',
                            help='path to connection settings yaml')
        parser.add_argument('--dummy', action='store_true', default=False,
                            help='enable dummy data')
        parser.add_argument('--port', type=int, default=8080,
                            help='run the server on this port')
        parser.add_argument('--updates', action='store_true', default=False,
                            help='enable periodic feed updates')
        parser.add_argument('--number', type=int, default=0,
                            help='instance number')

        args = parser.parse_args()
        return cls(args.config, args.dummy, args.port, args.updates,
                   args.number)

    def __init__(self, conn_filepath, dummy,  port, updates, number):
        self.conn_filepath = conn_filepath
        self.dummy_data = dummy
        self.port = port
        self.periodic_updates = updates
        self.instance_number = number
