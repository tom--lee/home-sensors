"""
Poll Hinen H5000-EU inverter via LSW-5 logger (SolarmanV5 / Modbus RTU).
"""
from pysolarmanv5 import PySolarmanV5, V5FrameError

LOGGER_IP     = "192.168.0.47"
LOGGER_SERIAL = 3529655818
PORT          = 8899
SLAVE_ID      = 1

def s16(v):
    return v if v < 0x8000 else v - 0x10000

try:
    modbus = PySolarmanV5(LOGGER_IP, LOGGER_SERIAL, port=PORT, mb_slave_id=SLAVE_ID)
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

    # ── Instantaneous ────────────────────────────────────────────────
    pv_w          = u32A(1)
    pv1_v, pv1_a  = A(3) * 0.1,  A(4) * 0.1
    pv1_w         = u32A(6)
    pv2_v, pv2_a  = A(8) * 0.1,  A(9) * 0.1
    pv2_w         = u32A(11)
    this_inv_w    = pv1_w + pv2_w
    other_inv_w   = pv_w - this_inv_w

    grid_import_w = u32A(66)
    grid_export_w = u32A(74)
    load_w        = u32A(76)
    batt_disch_w  = u32A(102)
    batt_chg_w    = u32A(104)

    batt_v        = B(127) * 0.1
    batt_soc      = B(128)
    batt_temp     = s16(B(136)) * 0.1
    bms_soc       = B(162)
    bms_v         = B(163) * 0.1
    bms_a         = s16(B(164)) * 0.1
    bms_soh       = B(174)

    net_grid      = grid_import_w - grid_export_w
    net_batt      = batt_disch_w  - batt_chg_w

    # ── Energy counters ──────────────────────────────────────────────
    ac_today      = u32C(250);  ac_total      = u32C(252)
    pv_today      = u32C(272);  pv_total      = u32C(274)
    load_today    = u32C(300);  load_total    = u32C(302)
    exp_today     = u32C(304);  exp_total     = u32C(306)
    imp_today     = u32C(308);  imp_total     = u32C(310)

    W  = 'W'
    KW = 'kWh'
    def row(label, val, unit, note=''):
        n = f'  ({note})' if note else ''
        if unit == KW:
            return f"  {label:<22} {val:>8.1f} {unit}{n}"
        else:
            return f"  {label:<22} {val:>8.0f} {unit}{n}"

    D = '─' * 44
    print(f"\n{D}")
    print(f"  Hinen H5000-EU                Today    Lifetime")
    print(D)
    print(f"  PV — system total     {pv_w:>8.0f} W")
    print(f"    PV1               {pv1_w:>6.0f} W  {pv1_v:.1f} V  {pv1_a:.1f} A")
    print(f"    PV2               {pv2_w:>6.0f} W  {pv2_v:.1f} V  {pv2_a:.1f} A")
    print(f"    This inverter     {this_inv_w:>6.0f} W")
    print(f"    Other inverter    {other_inv_w:>6.0f} W  (inferred)")
    print(f"  PV generation              {pv_today:>8.1f}  {pv_total:>10.1f} kWh")
    print(D)
    print(f"  Load                {load_w:>8.0f} W  {load_today:>8.1f}  {load_total:>10.1f} kWh")
    print(f"  Grid import         {grid_import_w:>8.0f} W  {imp_today:>8.1f}  {imp_total:>10.1f} kWh")
    print(f"  Grid export         {grid_export_w:>8.0f} W  {exp_today:>8.1f}  {exp_total:>10.1f} kWh")
    print(f"  Net grid            {net_grid:>+8.0f} W  (+ import / - export)")
    print(D)
    print(f"  Battery SOC              {batt_soc:>8} %")
    print(f"  Battery voltage          {batt_v:>8.1f} V")
    print(f"  Battery temp             {batt_temp:>8.1f} °C")
    print(f"  Charging            {batt_chg_w:>8.0f} W")
    print(f"  Discharging         {batt_disch_w:>8.0f} W")
    print(f"  Net battery         {net_batt:>+8.0f} W  (+ discharge / - charge)")
    print(D)
    print(f"  BMS SOC                  {bms_soc:>8} %")
    print(f"  BMS voltage              {bms_v:>8.1f} V")
    print(f"  BMS current              {bms_a:>+8.1f} A  (- charging)")
    print(f"  BMS SOH                  {bms_soh:>8} %")
    print(D)
    print(f"  AC output           {pv_w:>8.0f} W  {ac_today:>8.1f}  {ac_total:>10.1f} kWh")
    print(f"{D}\n")

except V5FrameError as e:
    print(f"Protocol error: {e}")
except ConnectionRefusedError:
    print("Connection refused — port 8899 not open.")
except TimeoutError:
    print("Timed out.")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
