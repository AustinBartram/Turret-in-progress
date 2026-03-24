import tkinter as tk
import serial
import time

# =========================================================
# ---------------- SERIAL COMMUNICATION --------------------
# =========================================================
# This creates a serial connection between your PC and Arduino.
# Think of this like a "data pipe" over USB.

# 'COM3' must match the port your Arduino is connected to.
# You can find this in Arduino IDE → Tools → Port.
# If this is wrong, the program will crash at startup.
#
# 9600 is the baud rate (speed of communication).
# This MUST match Serial.begin(9600) in your Arduino code.
arduinoConnection = serial.Serial('COM3', 9600)

# When a serial connection opens, Arduino resets.
# This delay gives it time to restart before we send data.
time.sleep(2)


# =========================================================
# ---------------- GUI DIMENSIONS --------------------------
# =========================================================
# These define the size of the control area (in pixels).
# This area represents your full turret movement range.

canvasWidth = 400
canvasHeight = 400

# Changing these:
# - Larger → more precise control (more mouse space)
# - Smaller → more sensitive (small mouse moves = big changes)


# =========================================================
# ---------------- CONTROL STATE VARIABLES -----------------
# =========================================================
# These variables represent the "state" sent to Arduino.

motorOn = 0
# 1 = turret motors are active (moving)
# 0 = motors are stopped

fireCommand = 0
# 1 = fire the dart
# 0 = do nothing


# =========================================================
# ---------------- DATA RATE LIMITING ----------------------
# =========================================================
# Prevents sending too many serial messages per second.
# Without this, your Arduino can get overwhelmed.

lastSendTime = 0

sendInterval = 0.03
# Minimum time (seconds) between messages
#
# Example:
# 0.03 → ~33 updates/sec (good balance)
# 0.01 → very fast, but may cause jitter or overload
# 0.1  → slower, but smoother and more stable


# =========================================================
# ---------------- FIRING CONTROL --------------------------
# =========================================================
# Prevents firing too rapidly (like a cooldown in games).

lastFireTime = 0

fireCooldown = 0.5
# Minimum time between shots (seconds)
#
# Lower → faster firing rate
# Higher → slower, more controlled firing


# =========================================================
# ---------------- SMOOTHING SYSTEM ------------------------
# =========================================================
# These variables smooth movement to avoid jerky motion.

smoothX = 126
smoothY = 126
# 126 is the center value in your 0–253 range.

alpha = 0.2
# Smoothing factor:
# This controls how fast the system reacts to changes.
#
# Formula used:
# smooth = smooth + alpha * (target - smooth)
#
# Values:
# 0.1 → very smooth (slow response)
# 0.3 → balanced
# 0.7 → fast but less smooth
# 1.0 → no smoothing (instant jump)


# =========================================================
# ---------------- DEAD ZONE -------------------------------
# =========================================================
# Prevents tiny mouse movements from causing jitter.

deadZone = 10  # pixels

# If the mouse is within this distance from center,
# the turret will NOT move.

# Increase → more stable center, less sensitivity
# Decrease → more responsive, but may jitter


# =========================================================
# ---------------- SEND DATA FUNCTION ----------------------
# =========================================================
def sendData(xValue, yValue):
    """
    Sends a structured packet to the Arduino.

    Packet format:
    [255, X, Y, motorOn, fireCommand, 254]

    255 = start marker
    254 = end marker

    Why markers?
    → Ensures Arduino knows where each message begins/ends
    → Prevents corrupted or partial reads

    X and Y must be integers between 0–253.
    """

    packet = bytearray([
        255,                 # Start marker
        int(xValue),         # X position (pan)
        int(yValue),         # Y position (tilt)
        motorOn,             # Whether motors should move
        fireCommand,         # Fire signal
        254                  # End marker
    ])

    # Send the packet over USB to Arduino
    arduinoConnection.write(packet)


# =========================================================
# ---------------- MOUSE MOVEMENT HANDLER ------------------
# =========================================================
def onMouseMove(event):
    """
    This function runs EVERY time the mouse moves inside the canvas.

    It converts:
    Mouse position → normalized values → smoothed output → serial packet
    """

    global motorOn, lastSendTime, smoothX, smoothY

    currentTime = time.time()

    # -------- RATE LIMITING --------
    # Skip sending if not enough time has passed
    if currentTime - lastSendTime < sendInterval:
        return

    # -------- POSITION RELATIVE TO CENTER --------
    dx = event.x - canvasWidth / 2
    dy = event.y - canvasHeight / 2

    # -------- DEAD ZONE CHECK --------
    # If mouse is near center → stop movement
    if abs(dx) < deadZone and abs(dy) < deadZone:
        xValue = 126
        yValue = 126
        motorOn = 0

    else:
        # -------- NORMALIZATION --------
        # Convert pixel position → 0–253 range
        xRaw = (event.x / canvasWidth) * 253
        yRaw = (event.y / canvasHeight) * 253

        # -------- SMOOTHING --------
        smoothX = smoothX + alpha * (xRaw - smoothX)
        smoothY = smoothY + alpha * (yRaw - smoothY)

        xValue = smoothX
        yValue = smoothY
        motorOn = 1

    # -------- SEND DATA --------
    sendData(xValue, yValue)
    lastSendTime = currentTime

    # -------- UPDATE CROSSHAIR --------
    canvas.coords(crosshair,
                        event.x - 5, event.y - 5,
                        event.x + 5, event.y + 5)


# =========================================================
# ---------------- MOUSE EXIT HANDLER ----------------------
# =========================================================
def onMouseLeave(event):
    """
    Triggered when the mouse leaves the control area.

    This acts as a safety:
    → Stops turret movement immediately
    → Prevents runaway motion
    """

    global motorOn

    motorOn = 0

    # Send center position (neutral)
    sendData(126, 126)


# =========================================================
# ---------------- FIRE FUNCTION ---------------------------
# =========================================================
def shoot(event=None):
    """
    Handles firing the turret.

    Triggered by:
    - Enter key
    - Spacebar
    - GUI button

    Includes cooldown protection.
    """

    global fireCommand, motorOn, lastFireTime

    currentTime = time.time()

    # -------- COOLDOWN CHECK --------
    if currentTime - lastFireTime < fireCooldown:
        return

    # -------- TRIGGER FIRE --------
    fireCommand = 1
    motorOn = 1

    # Send fire packet
    sendData(126, 126)

    # Reset immediately so it only fires once
    fireCommand = 0

    lastFireTime = currentTime


# =========================================================
# ---------------- GUI SETUP -------------------------------
# =========================================================
root = tk.Tk()
root.title("Turret Control System")

# Frame groups UI elements together
mainFrame = tk.Frame(root)
mainFrame.pack()

# Canvas = main control area
canvas = tk.Canvas(mainFrame,
                    width=canvasWidth,
                    height=canvasHeight,
                    bg="white")
canvas.grid(row=0, column=0)

# Draw center cross (visual reference)
canvas.create_line(canvasWidth/2, 0, canvasWidth/2, canvasHeight)
canvas.create_line(0, canvasHeight/2, canvasWidth, canvasHeight/2)

# Crosshair (tracks mouse position)
crosshair = canvas.create_rectangle(195, 195, 205, 205, outline="red")

# Bind mouse events
canvas.bind("<Motion>", onMouseMove)
canvas.bind("<Leave>", onMouseLeave)

# Optional shoot button (backup input)
shootButton = tk.Button(mainFrame,
                        text="SHOOT",
                        command=shoot,
                        height=5,
                        width=10)
shootButton.grid(row=0, column=1)


# =========================================================
# ---------------- KEYBOARD CONTROLS -----------------------
# =========================================================
# Allows firing using keyboard
root.bind('<Return>', shoot)   # Enter key
root.bind('<space>', shoot)    # Spacebar


# =========================================================
# ---------------- MAIN LOOP -------------------------------
# =========================================================
# Keeps the program running and listening for events
root.mainloop()