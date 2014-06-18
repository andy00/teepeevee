#!/usr/bin/python

import pexpect
import os

connected = False

class SensorTag:
	def __init__(self):
		global connected
		# send ./gatttool -I -i hci0
		self.sensor = pexpect.spawn('../../bluez-5.19/attrib/gatttool -i hci0 -I')
		
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
			print 'CONNECTED WITH 1C:BA:20:E7:B4'
			connected = True
		elif index ==  1:
			# turn on BT dongle in raspi
			connected = False
			print 'BT dongle is off, please turn it on with hciconfig hci0 up'
		elif index == 2:
			# just press the button on SensorTag
			connected = False
			print 'just press the button on SensorTag'
		elif index == 3:
			# timeout when nothing happens
			connected = False
			print 'timeout baby'
			 
		return

	def char_write_cmd( self, handle, value ):
        	# Send char-write-cmd
	        cmd = 'char-write-cmd 0x%02x 0%x' % (handle, value)
        	print cmd
        	self.sensor.sendline( cmd )
        	return


	def notification_loop( self ):
		global connected
	        while True:
			pnum = self.sensor.expect('Notification handle = .*? \r',timeout=None)
			# If notification handle is in the feedback
			if pnum==0:
				print 'Button was pressed'
				os.system("python gcmserver.py")
		
		return



def main():
	global connected
	print '\n'
	while True:
		# Call SensorTag function to establish connection
		tag = SensorTag()
		
		while (connected == True):
			# Send char-write-cmd
			tag.char_write_cmd(0x6C,0x0100)
		
			# READ
			tag.notification_loop()
		
		raw_input("Type any key to try to connect with SensorTag...")
		connected = False
		


if __name__ == '__main__':
	main()
