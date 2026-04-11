# home-sensors

A Raspberry Pi dashboard showing indoor temperature, outdoor (BOM) temperature, and solar inverter data on a local web page.

## Architecture

```
DHT22 sensor  ──► sense-dht22.py ──┐
                                    ├──► dashboard/server.py ──► browser (index.html)
Hinen inverter ─► sense-solar.py ──┘
                  (via LSW-5 logger)
```

There are two sensor clients and one dashboard server. Each client reads config from stdin, polls its data source on an interval, and pushes readings to the server via HTTP PUT. The browser polls the server for the latest reading from each device and updates the display in real time.

## Components

### `dashboard/server.py`

A plain Python HTTP server (no dependencies). Reads config from stdin:

```json
{ "host": "0.0.0.0", "port": 8000, "data_dir": "dashboard/output" }
```

**Endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves `index.html` |
| `PUT` | `/{device-id}/{value}` | Stores a reading for a device |
| `GET` | `/{device-id}/latest` | Returns the most recent reading as JSON |
| `GET` | `/bom/latest` | Fetches current outdoor temperature from the Bureau of Meteorology |

Readings are stored as CSV files in `data_dir`, one file per device per month: `{device-id}_{year}-{month}.csv`. Each row is `timestamp,value` where `value` is a `_`-separated list of fields whose meaning depends on the device type.

### `devices/DHT22_Python/sense-dht22.py`

Reads temperature and humidity from a DHT22 sensor wired to GPIO pin 4, and pushes to the dashboard every N minutes.

Config (stdin):
```json
{ "host": "localhost", "port": 8000, "deviceId": "living-room", "everyMinutes": 5 }
```

Value format: `{temperature}_{humidity}` (e.g. `23.4_61.2`)

### `devices/solarman-logger/sense-solar.py`

Polls a Hinen H5000-EU solar inverter via its SOLARMAN LSW-5 WiFi data logger and pushes a snapshot to the dashboard every N minutes. Errors (inverter offline at night, network issues) are logged and retried — the script does not exit on failure.

Config (stdin):
```json
{
  "host": "localhost",
  "port": 8000,
  "deviceId": "solar",
  "everyMinutes": 5,
  "loggerIp": "192.168.0.47",
  "loggerSerial": 3529655818
}
```

Value format (15 `_`-separated fields, in order):

| # | Field | Unit |
|---|-------|------|
| 0 | `pv_w` | W |
| 1 | `batt_soc` | % |
| 2 | `batt_v` | V |
| 3 | `batt_w` | W (positive = discharging, negative = charging) |
| 4 | `grid_import_w` | W |
| 5 | `grid_export_w` | W |
| 6 | `load_w` | W |
| 7 | `pv_today_kwh` | kWh |
| 8 | `pv_total_kwh` | kWh |
| 9 | `load_today_kwh` | kWh |
| 10 | `load_total_kwh` | kWh |
| 11 | `imp_today_kwh` | kWh |
| 12 | `imp_total_kwh` | kWh |
| 13 | `exp_today_kwh` | kWh |
| 14 | `exp_total_kwh` | kWh |

See `devices/solarman-logger/README.md` for hardware details and register map notes.

### `dashboard/index.html`

Single-page dashboard. Polls the server every 10–60 seconds and updates without a page reload.

**Layout:**
- Top: date
- Middle: time (large)
- Bottom-left: solar panel (load, PV, battery kW + SOC, grid)
- Bottom-right: indoor temperature (top) and BOM outdoor temperature (bottom)

## Running

Start the dashboard server, piping config via stdin:

```sh
cd dashboard
echo '{"host": "0.0.0.0", "port": 8000, "data_dir": "output"}' | python3 server.py
```

Start the temperature sensor (on the Pi with DHT22 attached):

```sh
cd devices/DHT22_Python
echo '{"host": "localhost", "port": 8000, "deviceId": "living-room", "everyMinutes": 5}' | python3 sense-dht22.py
```

Start the solar logger:

```sh
cd devices/solarman-logger
echo '{"host": "localhost", "port": 8000, "deviceId": "solar", "everyMinutes": 5, "loggerIp": "192.168.0.47", "loggerSerial": 3529655818}' | python3 sense-solar.py
```

Open `http://<pi-hostname>:8000` in a browser.

## Development / dummy data

Sample data files for local testing live in `dashboard/output/`:

- `living-room_2026-04.csv` — temperature and humidity readings
- `solar_2026-04.csv` — solar inverter readings

Start the server pointing at this directory to test the dashboard without hardware.
