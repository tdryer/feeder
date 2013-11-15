import os

from fabric.api import env, local, prefix, put, run 

CSIL_USERNAME = raw_input('CSIL USERNAME: ')

base_path = os.path.dirname(__file__)
env.gateway = '{}@cmpt470.csil.sfu.ca'.format(CSIL_USERNAME)
env.hosts = ['feeder@mx4']
env.password = 'qwerty123'


def deploy():
    local('py.test')
    put(base_path, '~/')
    with prefix('source .virtualenvs/feeder/bin/activate'):
        run('pip install --upgrade -r project/requirements.txt')


def start():
    with prefix('[ ! -e /tmp/supervisor.sock ] || exit 0'):
        run('supervisord -c ~/project/deploy/feeder_supervisor.conf')
    run('supervisorctl -c ~/project/deploy/feeder_supervisor.conf restart all')
