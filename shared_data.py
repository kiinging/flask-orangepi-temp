# shared_data.py
# Shared memory for both sensor.py and web_api.py.
from multiprocessing import Manager

manager = Manager()
data = manager.dict()

# ---------------- Measurements ----------------
data["rtd_temp"] = None
data["thermo_temp"] = None
data["internal_temp"] = None
data["fault"] = False
data["last_update"] = None

# ---------------- Control & Process Vars ----------------
data["mv"] = None              # Manipulated Variable calculated by the PID (0–100% PWM)
data["mv_manual"] = 0          # MV manually set by operator
data["pv_source"] = "rtd"      # PV source: "rtd" or "thermo"
data["sensor_select"] = 0      # 0 = thermo, 1 = rtd


# ---------------- Trend Buffer ----------------
# Logs: [{"time": "12:30:02", "pv": 65.2, "mv": 23.5}, ...]
data["trend"] = manager.list()

# ---------------- Actuator States ----------------
data["light"] = 0   # light: 0=OFF, 1=ON
data["plc"] = 0     # on/off system: 0=OFF, 1=ON
data["mode"] = 0    # default mode at startup is manual

# ---------------- Control Parameters ----------------
data["web"] = 0  # Setpoint source: 0 → use HMI, 1 → use Web
data["setpoint"] = 30.0
data["pid"] = {"kp": 1.0, "ti": 10.0, "td": 0.0}

