#!/usr/local/env python3

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone
import urllib.request
import urllib.error

config = json.load(sys.stdin)

host = config['host']
port = config['port']
data_dir = config['data_dir']

# TODO check data_dir does not exist as file

if not os.path.isdir(data_dir):
    os.mkdir(data_dir)

def data_path(device_id, year, month):
    filename = "{}_{}-{}.csv".format(device_id, year, month)
    return os.path.join(data_dir, filename)

def read_html_file():
    with open("index.html", "r") as file:
        return file.read()

def handle_get_home():
    return read_html_file()

def getBomMeasurements():
    bomEndpoint = "http://www.bom.gov.au/fwo/IDN60801/IDN60801.94729.json"
    responseJson = {}
    try:
        request = urllib.request.Request(
            bomEndpoint,
            # BOM will reject requests that appear automated.
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0'
            }
        )
        with urllib.request.urlopen(request) as response:
            responseJson = json.load(response)
    except urllib.error.URLError as e:
        print('error: ' + e.reason)
        print(e.args)
    #responseJson = json.load(responseText)
    temperature = responseJson['observations']['data'][0]['air_temp']
    return {
        "timestamp": "",
        "temperature": temperature,
        "humidity": 0
    }

def handle_put_device_value(device_id, value):
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    temperature, humidity = value.split('_', 1)
    now = datetime.now()
    year = now.year
    month = now.month
    path = data_path(device_id, year, month)
    with open(path, "a") as file:
        file.write(f"{timestamp},{temperature},{humidity}\n")
    return f"Data saved for {device_id}"

def handle_get_device_latest(device_id):
    files = [ path for path in os.listdir(data_dir) if device_id in path ].sort()

    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    current_filepath = data_path(device_id, year, month)
    prev_filepath = data_path(device_id, year, month)
    if os.path.exists(current_filepath):
        path = current_filepath
    else:
        path = prev_filepath
    
    try:
        with open(path, "r") as file:
            lines = file.readlines()
            latest = lines[-1].strip().split(',')
            return json.dumps(
                {
                    "timestamp": latest[0],
                    "temperature": float(latest[1]),
                    "humidity": float(latest[2]),
                }
            )
    except (IOError, IndexError):
        return json.dumps({"error": "No data found"})

class SimpleWebServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(handle_get_home().encode())
        elif "/latest" in self.path:
            device_id = self.path.split('/')[1]
            if device_id == 'bom':
                response = json.dumps(getBomMeasurements()).encode()
            else:
                response = handle_get_device_latest(device_id).encode()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response)
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        device_id, value = self.path[1:].split('/')
        if device_id and value:
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            response = handle_put_device_value(device_id, value)
            self.wfile.write(response.encode())
        else:
            self.send_response(400)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=SimpleWebServer, port=8000):
    server_address = ('0.0.0.0', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting httpd on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

