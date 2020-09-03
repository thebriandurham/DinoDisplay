# DinoDisplay
Python to Arduino PC metadata display. The backend python script leverages WMI and Open Hardware Monitor to fetch and provide computer operational (temp, load, etc.) data to the arduino for display using a chosen LCD/OLED/LED screen. 

## Goal
This project is still under development, but the end goal is to have a self-contained unit that utilizes an Arduino Nano with a digital display, connected to your PC, and housed within a 3D printed enclosure that is minimalistic, and unobtrusive on a desktop surface.

## Contents

### ./dinodisp.py
The main logic component of this setup. This script handles launching OHM, fetching the operational data, parsing it into small screen format friendly strings, and sending it to the connected Arduino over its serial connection.

### ./dinodisp/dinodisp.ino
The Arduino C++ script that runs the hardware's logical loop. It reads data from the serial buffer, if available, and outputs it to the attached screen.

### ./errors.txt
Log file used to store any errors that occur during runtime, primarily for debugging and troubleshooting use

### ./preferences.conf
(Soon to be) JSON file that allows end-users to set their preferences in terms of process window visibility, time format, etc.

### ./requirements.txt
PIP requirements list

## TODO:
* Finish detailing the README
* Implement JSON data format in pereferences.conf
  * Implement logic changes in the Python script to account for JSON preferences.conf format
* Test on AMD hardware (currently developed using an Intel CPU/NVidia GPU, so for scalability and accuracy, it needs to be ran on an AMD only machine)
  * Current tags for amdcpu,amdgpu are unconfirmed and may (read: probably) won't work
* Once testing is complete:
  * Remove debug/print statements, migrate to full errors.txt use (possibly implement a log.txt file as well)
  * Implement OHM subprocess exiting on script termination
  * Figure out how to best package the end product for pretty much anyone to be able to just download it and run it
* Once hardware / software is finalized:
  * Design 3D models to house the Arduino and Display
  * Assemble and test everything
