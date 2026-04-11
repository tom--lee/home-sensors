"""
Poll Hinen H5000-EU inverter via LSW-5 logger (SolarmanV5 / Modbus RTU).
Reads config from stdin and pushes data to the dashboard on each poll cycle.
"""
import json
import sys
import time
from http.client import HTTPConnection
from pysolarmanv5 import PySolarmanV5, V5FrameError

config = json.load(sys.stdin)

host          = config['host']
port          = config['port']
device_id     = config['deviceId']
sleep_time    = config['everyMinutes'] * 60
logger_ip     = config['loggerIp']
logger_serial = config['loggerSerial']
logger_port   = config.get('loggerPort', 8899)
slave_id      = config.get('slaveId', 1)

connection = HTTPConnection(f"{host}:{port}")

FIELD_ORDER = [
    "pv_w", "batt_soc", "batt_v", "batt_w", "grid_import_w", "grid_export_w",
    "load_w", "pv_today_kwh", "pv_total_kwh", "load_today_kwh",
    "load_total_kwh", "imp_today_kwh", "imp_total_kwh",
    "exp_today_kwh", "exp_total_kwh",
]

def s16(v):
    return v if v < 0x8000 else v - 0x10000

def read_inverter():
    modbus = PySolarmanV5(logger_ip, logger_serial, port=logger_port, mb_slave_id=slave_id)
    # Block A: regs 1–110   — PV strings, AC, grid, load, battery power
    # Block B: regs 127–174 — battery voltage, SOC, BMS
    # Block C: regs 250–315 — energy counters (kWh)
    a = modbus.read_input_registers(register_addr=1,   quantity=110)
    b = modbus.read_input_registers(register_addr=127, quantity=48)
    c = modbus.read_input_registers(register_addr=250, quantity=66)
    modbus.disconnect()

    def A(i): return a[i - 1]
    def B(i): return b[i - 127]
    def C(i): return c[i - 250]
    def u32A(i): return ((A(i) << 16) | A(i+1)) * 0.1
    def u32C(i): return ((C(i) << 16) | C(i+1)) * 0.1

    pv_w          = u32A(1)
    grid_import_w = u32A(66)
    grid_export_w = u32A(74)
    load_w        = u32A(76)
    batt_disch_w  = u32A(102)
    batt_chg_w    = u32A(104)

    batt_v        = B(127) * 0.1
    batt_soc      = B(128)
    batt_w        = batt_disch_w - batt_chg_w  # positive = discharging, negative = charging

    pv_today      = u32C(272);  pv_total      = u32C(274)
    load_today    = u32C(300);  load_total    = u32C(302)
    exp_today     = u32C(304);  exp_total     = u32C(306)
    imp_today     = u32C(308);  imp_total     = u32C(310)

    return {
        "pv_w":          pv_w,
        "batt_soc":      batt_soc,
        "batt_v":        batt_v,
        "batt_w":        batt_w,
        "grid_import_w": grid_import_w,
        "grid_export_w": grid_export_w,
        "load_w":        load_w,
        "pv_today_kwh":  pv_today,
        "pv_total_kwh":  pv_total,
        "load_today_kwh": load_today,
        "load_total_kwh": load_total,
        "imp_today_kwh": imp_today,
        "imp_total_kwh": imp_total,
        "exp_today_kwh": exp_today,
        "exp_total_kwh": exp_total,
    }

def push(data):
    value = '_'.join(str(round(data[f], 1)) for f in FIELD_ORDER)
    connection.request("PUT", f"/{device_id}/{value}")
    response = connection.getresponse()
    response.read()  # drain

while True:
    try:
        data = read_inverter()
        push(data)
        print(f"pushed: pv={data['pv_w']:.0f}W  batt={data['batt_soc']}%  "
              f"grid_import={data['grid_import_w']:.0f}W  load={data['load_w']:.0f}W")
    except (V5FrameError, ConnectionRefusedError, TimeoutError) as e:
        print(f"{type(e).__name__}: {e}")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
    time.sleep(sleep_time)
