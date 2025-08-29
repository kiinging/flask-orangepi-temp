# This allows the Cloudflare Worker to:
# Control the light
# Read temperatures from shared memory

# web_api.py
from flask import Flask, jsonify, request
import OPi.GPIO as GPIO
from shared_data import data

app = Flask(__name__)

# ---------------- GPIO Setup ----------------
LIGHT_PIN = "PC14"
GPIO.setmode(GPIO.SUNXI)
GPIO.setup(LIGHT_PIN, GPIO.OUT)

# --- Initial state: ensure OFF --------------
GPIO.output(LIGHT_PIN, GPIO.LOW)
data["light"] = 0  #
data["plc"] = 0  # plc always OFF at boot

# ---------------- Light Control ----------------
@app.route('/light/on', methods=['POST'])
def turn_light_on():
    GPIO.output(LIGHT_PIN, GPIO.HIGH)
    data["light"] = 1
    return jsonify({"light": data["light"]}), 200

@app.route('/light/off', methods=['POST'])
def turn_light_off():
    GPIO.output(LIGHT_PIN, GPIO.LOW)
    data["light"] = 0
    return jsonify({"light": data["light"]}), 200

# ---------------- Web Control: Start/Stop ----------------
@app.route('/web/on', methods=['POST'])
def web_start():
    data["web"] = 1
    return jsonify({"web": data["web"]}), 200


@app.route('/web/off', methods=['POST'])
def web_stop():
    data["web"] = 0
    return jsonify({"web": data["web"]}), 200


# ---------------- plc Control ----------------
@app.route('/plc/on', methods=['POST'])
def plc_on():
    data["plc"] = 1
    return jsonify({"plc": data["plc"]}), 200

@app.route('/plc/off', methods=['POST'])
def plc_off():
    data["plc"] = 0
    return jsonify({"plc": data["plc"]}), 200


# ---------------- Mode Control ----------------
@app.route('/mode/manual', methods=['POST'])
def mode_manual():
    data["mode"] = 0
    return jsonify({"mode": data["mode"]}), 200

@app.route('/mode/auto', methods=['POST'])
def mode_auto():
    data["mode"] = 1
    return jsonify({"mode": data["mode"]}), 200


# ---------------- Control Status ------------
@app.route('/control_status', methods=['GET'])
def get_control_status():
    return jsonify({
        "light": data.get("light"),
        "plc": data.get("plc"),
        "web": data.get("web"),
        "mode": data.get("mode"),
        
    })


# ---------------- Temperature Status ----------------
@app.route('/temp', methods=['GET'])
def get_temperature():
    """Return both temperatures + control states"""
    return jsonify({
        "rtd_temp": data.get("rtd_temp"),
        "last_update": data.get("last_update"),
        # "light": data.get("light"),
        # "plc": data.get("plc"),
    })

# ---------------- Trend Buffer ----------------
@app.route('/trend', methods=['GET'])
def get_trend_data():
    # return last 60 records (e.g., last hour if sampled per minute)
    trend_data = list(data["trend"])[-60:]
    return jsonify(trend_data)

# ---------------- Setpoint Control ----------------
@app.route('/setpoint', methods=['POST'])
def update_setpoint():
    try:
        req = request.get_json()
        sp = float(req.get("setpoint"))

        if sp > 80:
            sp = 80   # clamp to max 80

        data["setpoint"] = sp
        return jsonify({"setpoint": data["setpoint"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/setpoint_status', methods=['GET'])
def get_setpoint():
    return jsonify({"setpoint": data.get("setpoint", 50.0)})

# ---------------- PID Control ----------------
@app.route('/pid', methods=['POST'])
def update_pid():
    try:
        req = request.get_json()
        kp = float(req.get("kp"))
        ti = float(req.get("ti"))
        td = float(req.get("td"))
        data["pid"] = {"kp": kp, "ti": ti, "td": td}
        return jsonify(data["pid"]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/pid_status', methods=['GET'])
def get_pid():
    return jsonify(data.get("pid", {"kp": 1.0, "ti": 10.0, "td": 0.0}))


def main():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
