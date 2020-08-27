# dinodisp.py
# Gets computer hardware data and sends it over serial to a connected arduino
# Copyright 2020 - Brian Durham @ Midnight Labs, MIT Open Source Software License

# Global Imports
##### Placeholder

# Meta Vars
DEBUG = True
COMPORT = 0 # read from preferences.conf

# TODO:
# 	- Figure out how to properly close the subprocess (Open Hardware Monitor) on script exit
# 	- Remove / edit print statements once testing is completed to provide a better output to the end user
# 	- Create readme.txt
# 	- Once testing is completed, either package everything as an installer & .exe, or set the python process to hide/minimize once communication with the arduino is established
# 	- Refactor preferences parsing into JSON file format (more efficient than REGEXP)
#	- Add preferences parsing for time / date formats, update time string fetch to reflect this
# 	- Add preference for minimizing/hiding/showing the commandline on launch

# TODO: Remove once testing is completed __main__ is implemented
def test():

	arduino_rx_tx()

# Main function that fetches data and sends/receives to Arduino
def arduino_rx_tx():
	from datetime import datetime
	from time import sleep
	import serial

	# Setup steps
	if check_os() == True:
		init_error_log()
		init_open_hw_monitor()

		print("dinodisp:test_program: COMPORT on OPEN: %s" % (COMPORT))

		assign_comport()

		# Very preferences.conf is correctly parsed
		print("dinodisp:test_program: COMPORT post ASSIGN: %s" % (COMPORT))
	else:
		quit()

	# Keep local string copy of COMPORT for sending to serial.Serial
	comport_str = "COM" + str(COMPORT)

	# Init the serial interface
	try:
		serial_interface = serial.Serial(comport_str,9600,timeout=1)
	except Exception as err:
		write_error("dinodisp.py:arduino_rx_tx: Error opening COMPORT: %s; error(%s)" % (COMPORT,err))

	# Fetch and send data to the Arduino
	try:
		while True:
			temp_data = get_ohm_temp_data()
			display_string = process_temp_data_for_arduino(temp_data)
			display_string += str(datetime.now()) + ";\n"

			print("dinodisp.py:arduino_rx_tx: Sending message to Arduino: %s" % (display_string))
			serial_interface.write(display_string.encode())

			print("dinodisp.py:arduino_rx_tx: Awaiting Arduino response")
			print(serial_interface.readline().decode())

			# Sleep to reduce host *and* client load
			sleep(2)

	except Exception as err:
		write_error("dinodisp.py:arduino_rx_tx: Error during send/receive to Arduino; error(%s)" %(err))
		return False

	except KeyboardInterrupt as key:
		print("dinodisp:arduino_rx_tx: Exit command received from user, quitting")
		serial_interface.close()
		quit()
		return -1

# Takes data returned from get_ohm_temp_data, consolidates and averages it, and outputs it as a single line string for the Arduino to parse
def process_temp_data_for_arduino(temp_data):
		
	# Get average temp for CPUs with multiple cores
	processed_temps = {}
	for temp in temp_data:
		if temp['tag'] not in processed_temps:
			processed_temps[temp['tag']] = {
				'tag':temp['tag'],
				'name':temp['name'],
				'avg_temp':temp['value'],
				'num_temps':1
				}
		else:
			processed_temps[temp['tag']]['num_temps'] += 1
			processed_temps[temp['tag']]['avg_temp'] += temp['value']
	
	# Recalculate the average temp
	for temp_dict,sub_values in processed_temps.items():
		sub_values['avg_temp'] = int(sub_values['avg_temp'] / sub_values['num_temps'])

	display_string = ""
	for temp_dict,sub_values in processed_temps.items():
		append_str = ""
		if "cpu" in sub_values['tag']:
			append_str += "CPU: %s" % (sub_values['avg_temp']) + "C"
		elif "gpu" in sub_values['tag']:
			append_str += "GPU: %s" % (sub_values['avg_temp']) + "C"
		display_string += (append_str + ";")
	return display_string

# Use WMI and Open Hardware Monitor to retrieve desired hardware data
def get_ohm_temp_data():
	import wmi 

	wmi_interface = wmi.WMI(namespace="root\OpenHardwareMonitor")
	temp_data = wmi_interface.Sensor()

	valid_temp_tags = ["intelcpu","amdcpu","nvidiagpu","amdgpu"]
	temperatures = []

	for sensor in temp_data:
		for valid_tag in valid_temp_tags:
			if valid_tag in sensor.Identifier:
				if sensor.SensorType == "Temperature":
					temperatures.append({
						"tag":valid_tag,
						"name":sensor.Name,
						"value":sensor.Value
						})

	return temperatures

# Open Open Hardware Monitor process and hide it
def init_open_hw_monitor():
	import subprocess

	# Set startup info to hide Open Hardware Monitor on start
	window_vis = 0
	info = subprocess.STARTUPINFO()
	info.dwFlags = subprocess.STARTF_USESHOWWINDOW
	info.wShowWindow = window_vis

	try:
		cmd = ['OpenHardwareMonitor\OpenHardwareMonitor.exe']
		process = subprocess.Popen(cmd, stdout = subprocess.PIPE, startupinfo=info)
	except Exception as err:
		write_error("dinodisp.py:init_open_hw_monitor: Could not open Open Hardware Monitor, is the file present/are you running as Admin?; error(%s)" % (err))

# Assign the COMPORT global using the preferences.conf
def assign_comport():
	import re

	conf_regex = r"\$comport = ([0-9]{1})\$"
	conf_file = open("preferences.conf","r")
	conf_file_contents = conf_file.read()

	matches = re.search(conf_regex,conf_file_contents, re.MULTILINE)

	if matches.group(1):
		global COMPORT
		COMPORT = int(matches.group(1))
	else:
		write_error("dinodisp.py:assign_comport: Could not find comport integer in preferences.conf file")

# Simple error logging function
def write_error(error_message):
	from datetime import datetime

	error_message = str(datetime.now()) + ":" + error_message

	if DEBUG:
		print(error_message)

	error_log = open("errors.txt","a")
	error_log.write("\n%s" % (error_message))
	error_log.close()

# Create the errors.txt log file if it doesn't exist yet
def init_error_log():
	import os
	if not os.path.exists("errors.txt"):
		with open("errors.txt",'w'): pass

# Makes sure the host OS is Windows (linux not supported currently, would probably be a lot easier and more efficient though)
def check_os():
	import os

	if os.name == "nt":
		return True 
	else:
		write_error("dinodisp.py:check_os: Detected Operating System is non-Windows; only Windows is supported at this time")