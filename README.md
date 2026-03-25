# Smart Turret Control System

---

## What is Done

---

### Python Script

The Python control script is available in the main branch and provides the primary interface for operating the turret system.

Once downloaded, the system can be run using the following steps:

1. Open the Arduino IDE and connect the microcontroller to the turret
2. Identify and record the correct COM port and serial port number
3. Open the Python script and update the COM port to match your system

```python
SERIAL_PORT = "COM10"
```

4. Run the Python program to launch the GUI

---

### GUI Operation

When the program starts, a central control interface is displayed.

* A square control region appears with X and Y axes through the center
* This region defines the physical movement boundaries of the turret
* A crosshair (or targeting box) follows the mouse position in real time
* A 10-pixel dead zone is implemented to reduce jitter and unnecessary movement

---

### Movement Behavior

* Mouse movement directly maps to turret orientation
* The turret continuously updates its position through serial communication
* Movement is smooth and constrained within the defined control area

---

### Firing Controls

The firing sequence can be triggered using:

* Left Mouse Click (LMB)
* Enter key
* Spacebar

Each input sends a command sequence to the microcontroller to initiate the firing mechanism.

---

## System Overview

The system is built around three interacting components:

1. **Python GUI**
   Handles user input, visualization, and command generation

2. **Serial Communication Layer**
   Uses PySerial to transmit commands between the GUI and microcontroller

3. **Embedded Hardware System**
   Interprets commands and controls motors and actuation systems

---

## Hardware Integration

---

### Microcontroller

* Currently uses an Arduino-based system for control
* Planned transition to ESP32 for improved performance and onboard processing

---

### Camera Module (Planned)

The system will integrate the
https://www.amazon.com/Seeed-Studio-XIAO-ESP32-Sense/dp/B0C69FFVHH

This module provides:

* Built-in camera support
* Embedded processing capabilities
* Compatibility with AI frameworks

---

### Camera Reference Diagram

For wiring and configuration reference:
https://forum.arduino.cc/t/chinese-esp32-s3-cam/1318290/4

---

## AI Development (In Progress)

---

### ESP-WHO Framework

https://github.com/espressif/esp-who

ESP-WHO is an embedded AI framework developed by Espressif for ESP32 devices.

It provides:

* Face detection and recognition
* Object detection pipelines
* Optimized performance for embedded systems

Within this project, ESP-WHO will be used to enable:

* Real-time detection directly on the microcontroller
* Low-latency tracking without external computation
* Integration between detection results and turret movement

---

### Edge Impulse Platform

https://studio.edgeimpulse.com/studio/938769

Edge Impulse is used for building and deploying machine learning models to embedded systems.

In this project, it will support:

* Data collection and labeling
* Model training for object detection
* Optimization for ESP32 deployment
* Exporting models for real-time inference

---

### Planned AI Workflow

1. Capture image data using the onboard camera
2. Train models using Edge Impulse
3. Deploy optimized models to the ESP32
4. Run inference using ESP-WHO or compatible runtime
5. Convert detection output into turret movement commands
6. Enable autonomous targeting behavior

---

## Future Goals

---

### System Improvements

1. ESP32 Conversion
   Transition to a fully embedded system to reduce latency and remove dependency on a host computer

2. Camera Implementation
   Integrate the XIAO ESP32-S3 Sense for onboard vision processing

3. AI Integration
   Enable autonomous detection, tracking, and targeting

---

### Hardware Development

4. Stronger Motors
   Improve torque, responsiveness, and positional accuracy

5. Chassis Development

6. Circuitry Simplification
   Improve wiring layout and explore potential PCB integration

---

## Project Structure (Planned)

```
/project-root
│── main.py
│── serial_control.py
│── ai_module/
│── hardware/
│── README.md
```

---

## Notes

* Ensure the correct COM port is selected before running the program
* Close the Arduino Serial Monitor before launching the Python script
* Verify baud rate consistency between systems
* Ensure adequate power supply for motors and peripherals

---

## Author

Austin
Computer Engineering Student
Some Integration and refining used by AI Usage. 

---

## License

This project is intended for educational and development purposes.
