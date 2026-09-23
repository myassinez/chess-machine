#!/usr/bin/env python3
# ev3/main.py
# Runs ON the EV3 brick (ev3dev, Python 2.7 or 3).
#
# Communication method:
#   PC creates a WiFi hotspot; EV3 connects to it over WiFi.
#   PC runs a plain http.server on port 80, serving the current move as plain text.
#   EV3 polls http://<PC_hotspot_IP>:80 every second with urllib (built-in � no pip needed).
#   urllib used because requests couldn't be installed on ev3dev (armel arch, no internet).
#
# Source: Install DKMS ev3dev.md (2024-05-04) — user asked for this exact pattern:
#   "give me a python code to constantly checking http://169.254.12.236:80
#    for the text its hosting and then printing it"
#
# Hardware: ev3dev image on EV3 brick, Python 2.7 (urllib2) or Python 3 (urllib.request)
# Run: python main.py  (from the EV3 SSH session or VS Code EV3 extension)

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2.7 (ev3dev default)
    from urllib2 import urlopen

import time

try:
    from ev3dev2.motor import LargeMotor, MediumMotor, OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D
    ON_EV3 = True
except ImportError:
    print("ev3dev2 not found — running in simulation mode")
    ON_EV3 = False

# ─── Config ──────────────────────────────────────────────────────────────────

PC_IP   = "192.168.137.1"    # PC's WiFi hotspot IP (Windows default); update if different
PC_PORT = 80
URL     = "http://{}:{}/".format(PC_IP, PC_PORT)
POLL_INTERVAL = 1  # seconds

# ─── Coordinate tables ───────────────────────────────────────────────────────
# Keys are uppercase single-char file letters (A-H) and rank strings (1-8, 10-12)
# Values are position units for gox()/goy()

x = {
    "A": -3, "B": -2, "C": -1, "D":  0,
    "E":  1, "F":  2, "G":  3, "H":  4,
}

y = {
    "1": 11, "2": 10, "3":  9, "4":  8,
    "5":  7, "6":  6, "7":  5, "8":  4,
    "9":  3, "10": 2, "11": 1, "12": 0,
}

# Garage: where captured pieces are deposited (outside the board)
garage = [
    "H10", "G10", "F10", "E10", "D10", "C10", "B10", "A10",
    "H11", "G11", "F11", "E11", "D11", "C11", "B11", "A11",
]
garage_index = -1

# ─── Motor state ─────────────────────────────────────────────────────────────

current_x = 0
current_y = 0

# ─── Motor primitives ────────────────────────────────────────────────────────

def talla3():
    """Z-axis up (Port D)"""
    if ON_EV3:
        m = LargeMotor(OUTPUT_D)
        m.run_to_rel_pos(position_sp=int(-1.3 * 360), speed_sp=1000, stop_action="hold")
        m.wait_while("running")

def yhabbet():
    """Z-axis down (Port D)"""
    if ON_EV3:
        m = LargeMotor(OUTPUT_D)
        m.run_to_rel_pos(position_sp=int(1.3 * 360), speed_sp=1000, stop_action="hold")
        m.wait_while("running")

def xod():
    """Gripper close (Port B)"""
    if ON_EV3:
        m = MediumMotor(OUTPUT_B)
        m.run_to_rel_pos(position_sp=int(-1.3 * 360), speed_sp=1000, stop_action="hold")
        m.wait_while("running")

def fta7lyed():
    """Gripper open (Port B)"""
    if ON_EV3:
        m = MediumMotor(OUTPUT_B)
        m.run_to_rel_pos(position_sp=int(1.3 * 360), speed_sp=1000, stop_action="hold")
        m.wait_while("running")

def gox(to):
    """Move X-axis (Port A) to position `to`"""
    global current_x
    if ON_EV3:
        diff = to - current_x
        m = LargeMotor(OUTPUT_A)
        m.run_to_rel_pos(position_sp=int(diff * 241), speed_sp=1000, stop_action="hold")
        m.wait_while("running")
    current_x = to

def goy(to):
    """Move Y-axis (Port C) to position `to`"""
    global current_y
    if ON_EV3:
        diff = to - current_y
        m = LargeMotor(OUTPUT_C)
        m.run_to_rel_pos(position_sp=int(-diff * 200), speed_sp=1000, stop_action="hold")
        m.wait_while("running")
    current_y = to

# ─── Move sequences ──────────────────────────────────────────────────────────

def take(a):
    """
    Normal move (no capture).
    a = uppercase UCI string e.g. 'E2E4'
    a[0]=file_from, a[1]=rank_from, a[2]=file_to, a[3]=rank_to
    """
    print("take", a)
    talla3()
    fta7lyed()
    gox(x[a[0]])
    goy(y[a[1]])
    yhabbet()
    xod()
    talla3()
    gox(x[a[2]])
    goy(y[a[3]])
    yhabbet()
    fta7lyed()
    talla3()
    goy(0)   # home: y first then x (matches original source)
    gox(0)
    yhabbet()
    xod()

def kill(a):
    """
    Capture move.
    a = uppercase UCI string e.g. 'E2E4'
    Sequence: grab captured piece → garage → grab own piece → destination → home
    """
    global garage_index
    garage_index += 1
    g = garage[garage_index]
    print("kill", a, "→ garage slot", g)

    # Pick up the captured piece (at destination square)
    fta7lyed()
    talla3()
    gox(x[a[2]])
    goy(y[a[3]])
    yhabbet()
    xod()
    talla3()

    # Deposit in garage
    gox(x[g[0]])
    goy(y[g[1:]])
    yhabbet()
    fta7lyed()
    talla3()

    # Pick up own piece (at source square)
    gox(x[a[0]])
    goy(y[a[1]])
    yhabbet()
    xod()
    talla3()

    # Place own piece at destination
    gox(x[a[2]])
    goy(y[a[3]])
    yhabbet()
    fta7lyed()
    talla3()

    # Return home: x first then y (matches original source)
    xod()
    gox(0)
    goy(0)
    yhabbet()

# ─── HTTP polling loop ───────────────────────────────────────────────────────

def poll_and_act():
    print("Polling {} every {}s...".format(URL, POLL_INTERVAL))
    last_command = "NOOP"

    while True:
        try:
            response = urlopen(URL, timeout=3)
            command  = response.read().decode("utf-8").strip()
        except Exception as e:
            print("HTTP error:", e)
            time.sleep(POLL_INTERVAL)
            continue

        # Only act on new non-NOOP commands
        if command != "NOOP" and command != last_command:
            print("Received:", command)
            last_command = command

            if command[0:4] == "kill":
                kill(command[5:])
            elif command[0:4] == "take":
                take(command[5:])
            else:
                print("Unknown command:", command)

        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    poll_and_act()
