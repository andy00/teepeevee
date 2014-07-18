#!/usr/bin/env python

from datetime import datetime
import logging
from os import walk
from os import remove
import os
import send_sms

elderlyInfo = '/home/pi/ElderInfo.txt'
logging.basicConfig(filename='/var/log/ELLAsensor.log',level=logging.INFO)
varz = 1
smsTO="+6592763100"

while varz == 1:

	# For every file in /home/pi/Notifications call the function to send Notification
	g = []
	f = []
	for (dirpath, dirnames, filenames) in walk('/home/pi/Notifications'):
		g.extend(filenames)

	for y in g:
		# For every file in /home/pi/RegID send Notification
		for (dirpath, dirnames, filenames) in walk('/home/pi/RegID'):
			f.extend(filenames)
	
		for x in f:
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")

			logging.info ('call GCMServer.jar and send SMS')
			#send_sms.send_sms_oi("Tango 12345",smsTO)
			os.system('java -jar /home/pi/Downloads/teepeevee/GCMServer.jar /home/pi/RegID/' + x + ' ' + elderlyInfo + ' &')
			logging.info (dt + ' ' + 'Called GCM and sent SMS')

		# Remove the file in /home/pi/Notifications after running GCM
		os.remove('/home/pi/Notifications/'+ y)

	e = []
	f = []
	for (dirpath, dirnames, filenames) in walk('/home/pi/FallNotifications'):
		e.extend(filenames)
	
	for z in e:
		# For every file in /home/pi/RegID send Notification
		for (dirpath, dirnames, filenames) in walk('/home/pi/RegID'):
			f.extend(filenames)
			
		for x in f:
			dt = datetime.now()
			dt = dt.strftime("%A, %d. %B %Y %I:%M%p")
			
			logging.info ('call GCMServer.jar and send SMS')
			#send_sms.send_sms_oi("Tango 12345, smsTO")
			os.system('java -jar /home/pi/Downloads/teepeevee/GCMServer.jar /home/pi/RegID/' + x + ' ' + elderlyInfo + ' &')
			logging.info (dt + ' ' + 'Called GCM and sent SMS')
		
		# Remove the file in /home/pi/FallNotifications after running GCM
		os.remove('/home/pi/FallNotifications/'+ z)
