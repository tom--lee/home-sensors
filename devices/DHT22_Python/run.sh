$!/usr/bin/env bash

OUTPUT='output.txt'
HOST=localhost
PORT=52638

python3 sense-dht22.py > $OUTPUT && \
nc $HOST -p $PORT < $OUTPUT