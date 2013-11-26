from argparse import ArgumentParser


class Config(object):

    @classmethod
    def from_args(cls):
        '''
        Create a Config instance from sys.argv.
        '''
        parser = ArgumentParser()
        parser.add_argument('--amqp', default='')
        parser.add_argument('--database', default='sqlite://')
        parser.add_argument('--dummy', action='store_true', default=False)
        parser.add_argument('--port', type=int, default=8080)
        parser.add_argument('--updates', action='store_true', default=False)

        args = parser.parse_args()
        return cls(args.amqp, args.database, args.dummy, args.port,
                   args.updates)

    def __init__(self, amqp, database, dummy,  port, updates):
        self.amqp_uri = amqp
        self.database_uri = database
        self.dummy_data = dummy
        self.port = port
        self.periodic_updates = updates
