# Feeder

A feed reader by Elders of the Internet.

## Getting Started

The feed reader consists of static files (in the public directory) and an
application server (in the feedreader directory).

Start by installing the dependencies for the server using pip:

`pip install -r requirements.txt`

The tests can be run using `py.test` in the `feedreader` directory.

The `run.py` script is the easiest way to run the feed reader. It will serve
the public directory to `localhost:8080/` and pseudo-reverse-proxy the API
server to `localhost:8080/api/`.

