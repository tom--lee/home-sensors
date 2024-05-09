PORT=8000
nc -l ${PORT} &

python3 sense-dht22.py <<EOF{
  "host": "127.0.0.1",
  "port": 8000,
  "deviceId": "test-device",
  "everyMinutes": 1,
  "numMeasurements": 1
}
EOF
