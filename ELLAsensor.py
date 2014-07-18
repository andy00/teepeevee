#!/usr/bin/env python

'''
v0.9
- Added separate process for calling GCMServer.jar

v0.8
- Get and send to multiple PHONES from RegID file

v0.7
- Added Temp Read : )
- Added upload temp to xively

v0.6
- Added SMS

v0.5
- Changed print to console to log
- Added time when console logging

v0.4
- changed filename from apsensor.py to ELLAsensor.py
- Added FALL detection
- Added Sending alert during fall detection

v0.3
- NONE

v0.2
- Commented out calling: python gcmserver.py
- Added calling: GCMServer.jar
- Added function to bring up raspi Bluetooth device: BringUpBT

'''
from os import walk
from xively_upload import sendData, initSendData
from sensor_calcs import calcTmpTarget
import send_sms
import sys
import pexpect
import os
import TurnOnBluetoothDev
import time
from datetime import datetime
import logging

#PARAMETER
connected = False
tosigned = lambda n: float(n-0x10000) if n>0x7fff else float(n)
tosignedbyte = lambda n: float(n-0x100) if n>0x7f else float(n)
elderlyInfo = '/home/pi/ElderInfo.txt'

class SensorTag:
	def __init__(self):
		global connected
		# send ./gatttool -I -i hci0
		self.sensor = pexpect.spawn('/home/pi/Downloads/bluez-5.19/attrib/gatttool -i hci0 -I')
		
		# expecting response "[                 ][LE]>"
		self.sensor.expect('\[LE\]>')

		# send connect 1C:BA:8C:20:E7:B4
		self.sensor.sendline('connect 1C:BA:8C:20:E7:B4')

		# expecting responses:
		# "Connection Successful"
		# "Error: connect error: Connection refused (111)"
		# "[1C:BA:8C:20:E7:B4][LE]>"
		# TIMEOUT
		index = self.sensor.expect(['Connection successful','Error: connect error: Connection refused (111)','[1C:BA:8C:20:E7:B4][LE]>',pexpect.TIMEOUT])
		if index == 0:
			# call function to enable button
			#print 'CONNECTED WITH 1C:BA:20:E7:B4'
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
			logging.info (dt + ' ' +'CONNECTED WITH 1C:BA:20:E7:B4')
			connected = True
		elif index ==  1:
			# turn on BT dongle in raspi
			connected = False
			#print 'BT dongle is off, please turn it on with hciconfig hci0 up'
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
			logging.info (dt + ' ' + 'BT dongle is off, please turn it on with hciconfig hci0 up')
		elif index == 2:
			# just press the button on SensorTag
			connected = False
			#print 'just press the button on SensorTag'
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
			logging.info (dt + ' ' + 'just press the button on SensorTag')
		elif index == 3:
			# timeout when nothing happens
			connected = False
			#print 'timeout baby'
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
			logging.info (dt + ' ' + 'timeout baby')
			 
		return

	def char_write_cmd( self, handle, value ):
        	# Send char-write-cmd
	        cmd = 'char-write-cmd 0x%02x 0%x' % (handle, value)
        	#print cmd
		dt = datetime.now()
		dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
        	logging.info (dt + ' ' +cmd)
        	self.sensor.sendline( cmd )
        	return


	def notification_loop( self ):
		global connected
		global NotificationsCounter
		global FallNotificationsCounter
		feedback  = {}
		
		#initSendData()

		while True:
			pnum = self.sensor.expect('Notification handle = .*? \r',timeout=None)

			dongle_info = self.sensor.after
			dongle_info = dongle_info.split()[3:]
			handle = dongle_info[0]

			# TEMP
			'''if handle == '0x0025':
				objT1 = int (dongle_info[3],16)
				objT2 = int (dongle_info[2],16)
				ambT1 = int (dongle_info[5],16)
				ambT2 = int (dongle_info[4],16)
				
				objT = (objT1<<8)+objT2
				ambT = (ambT1<<8)+ambT2
				targetT = calcTmpTarget(objT, ambT)

				dt = datetime.now()
				dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
				logging.info (dt + ' ' +str(targetT)+' Celcius')
				#os.system('python sendData targetT')
				#sendData(targetT)
				#time.sleep(5)
			'''	
			# ACCELERATION
			if handle == '0x0030':
				feedback[0] = long(float.fromhex(dongle_info[2]))
                		feedback[1] = long(float.fromhex(dongle_info[3]))
                		feedback[2] = long(float.fromhex(dongle_info[4]))
                
	                	#print "Values :", feedback
        	        	accel = lambda v: tosignedbyte(v) / 64.0  # Range -2G, +2G
	        	        xyz = [accel(feedback[0]), accel(feedback[1]), accel(feedback[2])]
        	        	mag = (xyz[0]**2 + xyz[1]**2 + xyz[2]**2)**0.5

	            		#print "Acc Value", mag
            
			        if mag > 1.0 :
                			#print "SENDING MESSAGE FOR FALL ALERT:",mag
                			dt = datetime.now()
					dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
	        	        	#send_sms.send_sms_oi("SENDING MESSAGE FOR FALL ALERT: HELP!",smsTO)
					logging.info (dt + ' ' + "SENDING MESSAGE FOR FALL ALERT: HELP!")
	        	        	
					file = open('/home/pi/FallNotifications/'+ str(FallNotificationsCounter), 'w+')
					FallNotificationsCounter = FallNotificationsCounter+1
	        	        	
	        	        	#iterate file
	        	        	#f = []
	        	        	#for (dirpath, dirnames, filenames) in walk('/home/pi/RegID'):
	        	        	#	f.extend(filenames)
	        	        		
	        	        	#for x in f:                
	        	        	#	os.system('java -jar /home/pi/Downloads/teepeevee/GCMServer.jar /home/pi/RegID/' + x + ' ' + elderlyInfo + ' &')


	            	# BUTTON                
           		if handle == '0x006b':
	        	    	#keyStatus = long(float.fromhex(dongle_info[2]))
        	        	keyStatus = int(dongle_info[2])
		                #print "Key Status", keyStatus
				if keyStatus == 01 :
	        	        	#print "EMERGENCY ALERT:",keyStatus
	        	        	dt = datetime.now()
					dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
					logging.info(dt + ' ' +  "EMERGENCY ALERT: BUTTON 1")
					
					file = open('/home/pi/Notifications/'+ str(NotificationsCounter), 'w+')
					NotificationsCounter = NotificationsCounter+1
					
  	        	        	#f = []
	        	        	#for (dirpath, dirnames, filenames) in walk('/home/pi/RegID'):
	        	        	#	f.extend(filenames)

	        	        	#for x in f:                
	        	        	#	os.system('java -jar /home/pi/Downloads/teepeevee/GCMServer.jar /home/pi/RegID/' + x + ' ' + elderlyInfo + ' &')

	      	        	elif keyStatus == 02:
                			#print "TALK2ME ALERT:",keyStatus
          	        	        dt = datetime.now()
		      			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
					logging.info (dt + ' ' + "TALK2ME ALERT: BUTTON 2")
				
		return



def main():
	global connected
	global NotificationsCounter
	global FallNotificationsCounter

	FallNotificationsCounter = 0
	NotificationsCounter = 0
	logging.basicConfig(filename='/var/log/ELLAsensor.log',level=logging.INFO)
	
	# Call GCMServer.py
	os.system('sudo python /home/pi/Downloads/teepeevee/GCMServer.py &')
	
	# Check hci0 and bring up if it is down
	hci0status = TurnOnBluetoothDev.BringUpBT()
	
	# Check the response of bringing up hci0
	# if it fails to bring up, exit app
	if (hci0status==False):
		# exit app
	      	dt = datetime.now()
		dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
		logging.info (dt + ' ' + 'EXITING APPLICATION.')
		sys.exit(0)

	# Else it is good to go
	else:
		#print 'Device is UP:	hci0'
	      	dt = datetime.now()
		dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
		logging.info (dt + ' ' + 'Device is UP:	hci0')

	while True:

		# Call SensorTag function to establish connection
		tag = SensorTag()
		
		while (connected == True):
			# Send char-write-cmd for BUTTON
			tag.char_write_cmd(0x6C,0x0100)
		
			# Send char-write-cmd for TEMPERATURE
			tag.char_write_cmd(0x29,0x01)
			tag.char_write_cmd(0x26,0x0100)

			# FALL
			tag.char_write_cmd(0x31,0x0100)
			tag.char_write_cmd(0x34,01)

			# READ
			tag.notification_loop()
		
		dt = datetime.now()
		dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
		logging.info (dt + ' ' + 'Not connected to SensorTag. Press the SensorTag button to try pairing again.')
		#raw_input("Type any key to try to connect with SensorTag...")
		connected = False
		


if __name__ == '__main__':
	main()
