# server the API server and public files using the reverse proxy "tape"

tape --version >/dev/null 2>&1 || { echo >&2 "development server requires: https://github.com/wspringer/tape"; exit 1; }

PORT=8080
API_SERVER_PORT=8081

echo "starting api server..."
python -m feedreader.main $API_SERVER_PORT &

tape --root public \
     --proxy /api=http://localhost:$API_SERVER_PORT \
     --port $PORT &

trap 'kill $(jobs -p)' EXIT
wait
