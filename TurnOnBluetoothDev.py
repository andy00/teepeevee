#!/usr/bin/env python
'''
This app is designed for 1 Bluetooth dongle hardcoded hci0
No support for more than 1 Bluetooth dongle
'''

import pexpect

hci0up = False

def devNotAvail():
	print 'Bluetooth USB device hci0 is not detected\n'
	print 'Please connect Bluetooth USB device to RasPi to continue\n'

def devAvailUp():
	print 'Device is UP:	hci0'

def BringUpBT():
	global hci0up
	hci0up = False
	
	# hciconfig to check whether hciX is available
	hciCheck = pexpect.spawn ('hciconfig')

	# check feedback stream for hciX
	hciAvail1 = hciCheck.expect(['hci0', pexpect.EOF, pexpect.TIMEOUT])
		
	# if TIMEOUT
	if (hciAvail1==2):
		print 'TIMEOUT'
		hci0up = False

	# if hciX not available, it will get EOF, print note and exit app
	elif (hciAvail1==1):
		devNotAvail()
		hci0up = False

	# if available check whether hciX is running 
	elif (hciAvail1==0):
		print 'Dev Available:	hci0'

		# hciconfig to check whether hciX is available
		hciCheck = pexpect.spawn ('hciconfig')
			
		# check feedback stream for RUNNING / DOWN / EOF / TIMEOUT
		hciAvail2 = hciCheck.expect(['RUNNING', 'DOWN', pexpect.EOF, pexpect.TIMEOUT])

		if (hciAvail2==3):
			print 'TIMEOUT'
			hci0up = False

		# EOF (no response), means hciX not available, print note and exit app
		elif (hciAvail2==2):
			devNotAvail()
			hci0up = False

		# hci0 is DOWN, send command hciconfig hci0 up
		elif (hciAvail2==1):
		
			# send command to turn on hci0
			print 'Turning on Dev:	hci0'
			hciCheck = pexpect.spawn ('sudo hciconfig hci0 up')

			# check feedback stream for EOF / TIMEOUT
			hciAvail3 = hciCheck.expect([pexpect.TIMEOUT, pexpect.EOF])

			# TIMEOUT
			if (hciAvail3==0):
				print 'TIMEOUT'
				hci0up = False

			# EOF
			elif (hciAvail3==1):
			
				# Send another hciconfig
				hciCheck = pexpect.spawn ('hciconfig')
				
				# check feedback stream for RUNNING / DOWN / EOF / TIMEOUT
				hciAvail4 = hciCheck.expect(['RUNNING', 'DOWN', pexpect.EOF, pexpect.TIMEOUT])
				
				# RUNNING
				if (hciAvail4==0):
					devAvailUp()
					hci0up = True
				
				# DOWN	
				elif (hciAvail4==1):
					print 'still down :('
					hci0up = False
				
				# EOF
				elif (hciAvail4==2):
					print 'EOF'
					hci0up = False
				
				# TIMEOUT	
				elif (hciAvail4==3):
					print 'TIMEOUT'
					hci0up = False

		# hci0 is UP
		elif (hciAvail2==0):
			devAvailUp()
			hci0up = True

	if (hci0up==False):
		return False

	else:
		return True

