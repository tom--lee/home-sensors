# solar-logger-interface

Polls a **Hinen H5000-EU** hybrid solar inverter via its **SOLARMAN LSW-5** WiFi data logger and prints a snapshot of current system state.

## Hardware

| Component | Details |
|---|---|
| Inverter | Hinen H5000-EU (5 kW hybrid, single phase) |
| Logger | SOLARMAN LSW-5, firmware `LSW5_CSIP_02E0_1.06` |
| Logger serial | 3529655818 |
| Logger LAN IP | 192.168.0.47 (static DHCP lease recommended) |

The system has two inverters. This logger is attached to one of them. The inverter reports a system-wide PV total (via CT/meter) in addition to its own two MPPT string inputs, so the second inverter's contribution is inferred as the difference.

## How it works

The LSW-5 logger exposes a **SolarmanV5** TCP server on port 8899. This is a binary protocol that wraps standard **Modbus RTU** frames (function code 04 — read input registers). `poll.py` sends three contiguous register reads and decodes the results against the Hinen Modbus register map (protocol doc: `Inverter.Modbus.RTU.Protocol.V1.62`, dated 2024-09-27).

`pysolarmanv5.py` is a vendored copy of [jmccrohan/pysolarmanv5](https://github.com/jmccrohan/pysolarmanv5) (MIT licence). `umodbus/` is a vendored copy of the client-side subset of [riptideio/umodbus](https://github.com/riptideio/umodbus) (MPL-2.0 licence). No external dependencies.

## Usage

```
python3 poll.py
```

No installation required beyond Python 3.9+.

## Output

```
────────────────────────────────────────────
  Hinen H5000-EU                Today    Lifetime
────────────────────────────────────────────
  PV — system total        7993 W
    PV1                    4100 W  380.1 V  10.8 A
    PV2                    3893 W  375.4 V  10.4 A
    This inverter          7993 W
    Other inverter            0 W  (inferred)
  PV generation                    24.3      8431.2 kWh
────────────────────────────────────────────
  Load                     2100 W      8.1        2944.7 kWh
  Grid import                 0 W      0.0        1203.4 kWh
  Grid export              5893 W     16.2        5288.1 kWh
  Net grid                -5893 W  (+ import / - export)
────────────────────────────────────────────
  Battery SOC                100 %
  Battery voltage           53.2 V
  Battery temp              28.4 °C
  Charging                    0 W
  Discharging                 0 W
  Net battery                 0 W  (+ discharge / - charge)
────────────────────────────────────────────
  BMS SOC                   100 %
  BMS voltage               53.1 V
  BMS current              +0.0 A  (- charging)
  BMS SOH                   100 %
────────────────────────────────────────────
  AC output                7993 W     24.3        8431.2 kWh
────────────────────────────────────────────
```

## Register map notes

- **Battery SOC** (reg 128): raw value is a direct percentage 0–100, no scaling
- **BMS current** (reg 164): signed, negative = charging
- **Energy counters**: daily totals reset at inverter midnight (clock synced from Solarman cloud). Battery charge/discharge energy is not available as a hardware counter — integration from the instantaneous W readings is needed for those.
- **PV system total** (regs 1–2): includes both inverters via a system meter; individual string readings (regs 6–7, 11–12) reflect only this inverter's two MPPT inputs

## Logger web UI

- Main config: `http://192.168.0.47/`  (admin / admin)
- Hidden config: `http://192.168.0.47/config_hide.html`

The hidden config page exposes the cloud server push destination (Server A). Do not overwrite this accidentally — the logger only has one active outbound server slot despite the UI suggesting two.
