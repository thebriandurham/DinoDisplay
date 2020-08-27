# dino_mon.py
# gets GPU, CPU core temps and sends it over serial to a connected arduino
# Copyright 2020 - Midnight Labs

# Global Imports
##### Placeholder

# Meta Vars
DEBUG = True
COMPORT = 0 # read from preferences.conf

def test():

	# Setup setps
	if check_os() == True:
		init_debug_mode()
		init_error_log()
		
		init_open_hw_monitor()

		print("dinodisp:test_program: COMPORT on OPEN: %s" % (COMPORT))

		assign_comport()

		print("dinodisp:test_program: COMPORT post ASSIGN: %s" % (COMPORT))

		temp_data = get_ohm_temp_data()
		display_string = process_temp_data_for_arduino(temp_data)

		#print("dinodisp:test_program: temp_data: %s" % (temp_data))
		#print("dinodisp:test_program: display_string: %s" % (display_string))

		arduino_rx_tx(display_string)

def arduino_rx_tx(display_string):
	from time import sleep
	import serial

	comport_str = "COM" + str(COMPORT)

	try:
		serial_interface = serial.Serial(comport_str,9600,timeout=30)
	except Exception as err:
		write_error("dinodisp.py:arduino_rx_tx: Error opening COMPORT: %s; error(%s)" % (COMPORT,err))

	try:
		# DEBUG:
		print("dinodisp.py:arduino_rx_tx: Sending message to Arduino: %s" % (display_string))

		#serial_interface.write(display_string.encode())
		#print(serial_interface.readline().decode())
		#TESTING
		display_chars = list(display_string)
		#print(display_chars)
		for char in display_chars:
			print("dinodisp.py:arduino_rx_tx: Sending char %s to Arduino" % (char))
			serial_interface.write(char.encode())
			print("dinodisp.py:arduino_rx_tx: Awaiting Arduino response")
			response = serial_interface.readline().decode()
			print("dinodisp.py:arduino_rx_tx: Response received: %s" % (response))
			sleep(.1)

		# DEBUG:
		# print("dinodisp.py:arduino_rx_tx: Arduino response: %s" % (response))

		# if "OK" in response:
		# 	sleep(.1)
		# 	continue
		# else:
		# 	write_error("dinodisp.py:arduino_rx_tx: Received invalid response from Arduino device. Exiting")
		# 	return False

		#serial_io.close()
		#serial_interface.close()

	except Exception as err:
		write_error("dinodisp.py:arduino_rx_tx: Error during send/receive to Arduino; error(%s)" %(err))
		return False

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
			append_str += "CPU: %s" % (sub_values['avg_temp'])
		elif "gpu" in sub_values['tag']:
			append_str += "GPU: %s" % (sub_values['avg_temp'])
		display_string += (append_str + ";")

	return display_string

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

def write_error(error_message):
	from datetime import datetime

	error_message = str(datetime.now()) + ":" + error_message

	if DEBUG:
		print(error_message)

	error_log = open("errors.txt","a")
	error_log.write("\n%s" % (error_message))
	error_log.close()

def init_error_log():
	import os
	if not os.path.exists("errors.txt"):
		with open("errors.txt",'w'): pass

def init_debug_mode():
	global DEBUG
	DEBUG = True

def check_os():
	import os

	if os.name == "nt":
		return True 
	else:
		write_error("dinodisp.py:check_os: Detected Operating System is non-Windows; only Windows is supported at this time")