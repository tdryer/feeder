# Unnamed Feed Reader

A project by Elders of the Internet.

## Getting Started

Install run-time dependencies:

`pip install -r requirements.txt`

Install py.test if you want to run tests:

`pip install pytest`

Run tests by running `py.test` in the feedreader directory.

Install tape if you want to use run.sh:

`pip install git+https://github.com/wspringer/tape.git#egg=tape`

run.sh will serve the public directory to localhost:8080/ and reverse-proxy
the API server to localhost:8080/api/.
