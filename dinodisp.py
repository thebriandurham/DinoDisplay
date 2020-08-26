# dino_mon.py
# gets GPU, CPU core temps and sends it over serial to a connected arduino
# Copyright 2020 - Midnight Labs

# Global Imports
##### Placeholder

# Meta Vars
COMPORT = 0 # read from preferences.conf

def process_temp_data_for_arduino(temp_data):
	output_string = "" # Init output string for bytestream to arduino
		
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

	# Create the single line output string for the Arduino
	for temp_dict,sub_values in processed_temps.items():
		temp_title = None
		if "cpu" in sub_values['tag']:
			temp_title = "CPU"
		elif "gpu" in sub_values['tag']:
			temp_title = "GPU"
		else:
			temp_title = sub_values['tag'] # Edge case for unknown make/manufacturer
		output_string += "%s:%sC," % (temp_title,sub_values['avg_temp'])

	# Terminator character for Arduino processing
	output_string += "\n"
	return output_string


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

	## DEBUG : TODO: REMOVE THIS ONCE TESTING IS COMPLETE
	print(temperatures)

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
	except Exception as e:
		write_error("dinodisp.py:init_open_hw_monitor: Could not open Open Hardware Monitor, is the file present/are you running as Admin?")

def assign_comport():
	import re

	conf_regex = r"\$comport = ([0-9]{1})\$"
	conf_file = open("preferences.conf","r")
	conf_file_contents = conf_file.read()

	matches = re.search(conf_regex,conf_file_contents, re.MULTILINE)

	if matches.group(1):
		COMPORT = int(matches.group(1))
	else:
		write_error("dinodisp.py:assign_comport: Could not find comport integer in preferences.conf file")

def write_error(error_message):
	error_log = open("errors.txt","a")
	error_log.write("\n%s" % (error_message))
	error_log.close()

def init_error_log():
	import os
	if not os.path.exists("errors.txt"):
		with open("errors.txt",'w'): pass

def check_os():
	import os

	if os.name == "nt":
		return True 
	else:
		write_error("dinodisp.py:check_os: Detected Operating System is non-Windows; only Windows is supported at this time")