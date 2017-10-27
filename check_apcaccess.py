#!/usr/bin/env python
# -*- coding: utf-8 -*-

# check_apcaccess.py - a script for checking a APC UPS
# using the apcaccess utility
#
# 2016 By Christian Stankowic
# <info at stankowic hyphen development dot net>
# https://github.com/stdevel
#
# Enhanced and error corrections by Chris Johnston 2017
# Tested on BX1300G & RS 1500G but should work on most APC UPS
# <HireChrisJohnston at g mail>
# 
#> Added detection of TONBATT
#> Corrected misc errors
#> Enchanced charting & messaging

from optparse import OptionParser, OptionGroup
import os
import subprocess
import logging
import re

#set logger
LOGGER = logging.getLogger("check_apcaccess")

#global variables
ups_info={}
state=0



def check_value(val, desc, warn, crit, reverse=False):
	#compares value to thresholds and sets codes
	LOGGER.debug("Comparing '{0}' ({1}) to warning/critical thresholds {2}/{3} (reverse: {4})".format(val, desc, warn, crit, reverse))
	snip=""
	if reverse == False:
		if val > crit:
			#critical
			snip="{0} *Critical* ({1})".format(desc, val)
			set_code(2)
		elif val > warn:
			#warning
			snip="{0} -Warning ({1})".format(desc, val)
			set_code(1)
		else: snip="{0}: {1}".format(desc, val)
	else:
		if val < crit:
			#critical
			snip="{0} *Critical* ({1})".format(desc, val)
			set_code(2)
		elif val < warn:
			#warning
			snip="{0} -Warning ({1})".format(desc, val)
			set_code(1)
		else: snip="{0}: {1}".format(desc, val)
	return snip



def set_code(int):
	#set result code
	global state
	if int > state: state = int



def get_return_str():
	#get return string
	if state == 3: return "UNKNOWN"
	elif state == 2: return "CRITICAL"
	elif state == 1: return "WARNING"
	else: return "OK"



def get_value(key, isFloat=False):
	#get value from apcaccess information
	if isFloat:
		temp = re.findall(r'[-+]?[0-9]*\.?[0-9]*', ups_info[key])
		return float(temp[0])
	else: return ups_info[key]



def calc_consumption():
	#calculate power consumption
	load = get_value('LOADPCT', True)
	out = get_value('NOMPOWER', True)
	power_cons = int(out*(load/100))
	LOGGER.debug("MATH says, based on the information provided, it is assumed that the power consumption might be ~{0} watts".format(power_cons))
	return power_cons



def check_ups():
	#check UPS
	global state
	
	#get _all_ the values
	starttime = get_value('STARTTIME')
	status = get_value('STATUS')
	battv = get_value('BATTV', True)
	LOGGER.debug("BattV: {0}".format(battv))
	load = get_value('LOADPCT', True)
	batt = get_value('BCHARGE', True)
	xfers = get_value('NUMXFERS')
	tot_onbat =  get_value('CUMONBATT')
	on_bat = get_value('TONBATT')
	linev = get_value('LINEV')

	if options.time_warn and options.time_crit: time = get_value('TIMELEFT', True)
	power_cons = calc_consumption()

	#Check if line level is high
	curr_line_level = get_value('LINEV', True)
	
	if options.line_level > curr_line_level:
		snip_line_level = " Line Level low {2} {0} for {1}".format(status,on_bat,linev)
		set_code(1)
	else: snip_line_level = status
 
	#check Batt V
	snip_battv = check_value(battv, "Voltage", options.battv_warn, options.battv_crit, True) +'v'
	
	#check load
	snip_load = check_value(load, "Load", options.load_warn, options.load_crit)+ '%'
	
	#check battery charge
	snip_batt = check_value(batt, "Charge", options.bat_warn, options.bat_crit, True) +'%'
	
	#check battery time (optional)
	if options.time_warn or options.time_crit:
		snip_time = check_value(time, "Time Left", options.time_warn, options.time_crit, True) + 'min'
	else: snip_time=""
	
	#check power consumption (optional)
	if options.consum_warn or options.consum_crit:
		snip_consum = check_value(power_cons, "Power consumption", options.consum_warn, options.consum_crit) +'w'
	else: snip_consum=""
	
	# get detail
	snip_detail ="(Total On Battery: " + tot_onbat + " / #Xfers: " + xfers + " since "+starttime+")"
	#get performance data
	if options.show_perfdata:
		#initialize perfdata
		perfdata=" |"
		
		#power consumption
		if options.consum_warn and options.consum_crit: perfdata = "{0} 'consumption'={1};{2};{3};;".format(perfdata, power_cons, float(options.consum_warn), float(options.consum_crit))
		else: perfdata = "{0} 'Consumption'={1}w;;;".format(perfdata, power_cons)
		
		#voltage
		perfdata = "{0} 'Voltage'={1}v;{2};{3};{4};{5}".format(perfdata, battv, float(options.battv_warn), float(options.battv_crit), 11.0, 27.3)
		
		#load
		perfdata = "{0} 'Load'={1}%;{2};{3};{4};{5}".format(perfdata, load, float(options.load_warn), float(options.load_crit), 0.0, 100.0)
		
		#battery charge
		perfdata = "{0} 'Battery_Charge'={1}%;{2};{3};{4};{5}".format(perfdata, batt, float(options.bat_warn), float(options.bat_crit), 0.0, 100.0)
		
		#battery time left only if user specified the warning and critical values
		if options.time_warn or options.time_crit:
			perfdata =  "{0} 'Battery_Time_Left'={1};{2};{3};;".format(perfdata, time, float(options.time_warn), float(options.time_crit))
	else: perfdata=""
	
	#return result
	snips = [x for x in [snip_line_level,snip_battv, snip_batt, snip_load,snip_consum,snip_time,snip_detail ] if x != ""]
	print "{0}: {1}{2}".format(get_return_str(), str(", ".join(snips)), perfdata)
	exit(state)




def run_cmd(cmd=""):
	#run the command, it's tricky!
	output = subprocess.Popen("LANG=C {0}".format(cmd), shell=True, stdout=subprocess.PIPE).stdout.read()
	LOGGER.debug("Output of '{0}' => '{1}".format(cmd, output))
	return output



def get_apcaccess_data():
	#get output of apcaccess
	global ups_info
	
	raw_data = run_cmd("apcaccess -h" + options.host)
	raw_data = raw_data.splitlines()
	for line in raw_data:
		#parse lines to key/value dict
		key=line[:line.find(":")].strip()
		value=line[line.find(":")+1:].strip()
		LOGGER.debug("Found key '{0}' with value '{1}'".format(key, value))
		ups_info[key]=value



if __name__ == "__main__":
	#define description, version and load parser
	desc='''%prog is used to check a APC UPS using the apcaccess utility.
	
	https://github.com/HireChrisJohnston/nagios-apcupsd'''
	parser = OptionParser(description=desc,version="%prog version 1.0.0")
	
	gen_opts = OptionGroup(parser, "Generic options")
	mon_opts = OptionGroup(parser, "Monitoring options")
	thres_opts = OptionGroup(parser, "Threshold options")
	parser.add_option_group(gen_opts)
	parser.add_option_group(mon_opts)
	parser.add_option_group(thres_opts)
	
	#-d / --debug
	gen_opts.add_option("-d", "--debug", dest="debug", default=False, action="store_true", help="enable debugging outputs")
	
	#-P / --enable-perfdata
	mon_opts.add_option("-P", "--enable-perfdata", dest="show_perfdata", default=False, action="store_true", help="enables performance data (default: no)")
	
	#-w / --battv-warning
	thres_opts.add_option("-w", "--battv-warning", dest="battv_warn", default=24, type=float, metavar="VOLTS", action="store", help="Defines battery voltage warning threshold (default: 24)")
	
	#-W / --battv-critical
	thres_opts.add_option("-W", "--battv-critical", dest="battv_crit", default=23.3, type=float, metavar="VOLTS", action="store", help="Defines battery voltage critical threshold (default: 23.3)")
	
	#-c / --temp-critical
	#thres_opts.add_option("-c", "--temp-critical", dest="temp_crit", default=55, type=float, metavar="TEMP", action="store", help="Defines temprature critical threshold(defalt: 55)")
	
	#-l / --load-warning
	thres_opts.add_option("-l", "--load-warning", dest="load_warn", default=50, type=int, metavar="PERCENT", action="store", help="Defines load warning threshold in percent (default: 50%)")
	
	#-L / --load-critical
	thres_opts.add_option("-L", "--load-critical", dest="load_crit", default=80, type=int, metavar="PERCENT", action="store", help="Defines load critical threshold in percent (default: 80%)")
	
	#-b / --battery-warning
	thres_opts.add_option("-b", "--battery-warning", dest="bat_warn", default=30, type=int, metavar="PERCENT", action="store", help="Defines battery load warning threshold in percent (default: 30%)")
	
	#-B / --battery-critical
	thres_opts.add_option("-B", "--battery-critical", dest="bat_crit", default=15, type=int, metavar="PERCENT", action="store", help="Defines battery load critical threshold in percent (default: 15%)")
	
	#-t / --time-warning
	thres_opts.add_option("-t", "--time-warning", dest="time_warn", type=int, metavar="TIME", action="store", help="Defines battery time left warning threshold in minutes (default: empty). If defined you must also define time-critical")
	
	#-T / --time-critical
	thres_opts.add_option("-T", "--time-critical", dest="time_crit", type=int, metavar="TIME", action="store", help="Defines battery time left critical threshold in minutes (default: empty). If defined you must also define time-warning")
	
	#-u / --consumption-warning
	thres_opts.add_option("-u", "--consumption-warning", dest="consum_warn", type=int, metavar="WATTS", action="store", help="Defines power consumption warning threshold in watts (default: empty)")
	
	#-U / --consumption-critical
	thres_opts.add_option("-U", "--consumption-critical", dest="consum_crit", type=int, metavar="WATTS", action="store", help="Defines power consumption critical threshold in watts (default: empty)")
	
	#-H / --host
	gen_opts.add_option("-H", "--host", dest="host", type="string", action="store", default="127.0.0.1", help="host of appcupsd")	

	#-X / --line-level
        gen_opts.add_option("-X", "--line-level", dest="line_level", type="int", action="store", default="110", help="Volts of power outlet to detect no power if less than the line level")
	
	#parse arguments
	(options, args) = parser.parse_args()
	
	#set logger level
	if options.debug:
		logging.basicConfig(level=logging.DEBUG)
		LOGGER.setLevel(logging.DEBUG)
	else:
		logging.basicConfig()
		LOGGER.setLevel(logging.INFO)
	
	#debug outputs
	LOGGER.debug("OPTIONS: {0}".format(options))
	
	#get information
	get_apcaccess_data()
	
	#check UPS
	check_ups()
