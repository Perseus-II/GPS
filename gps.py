import socket
import serial
import time
import pynmea2
from thread import *
import threading

class GPS:
	def __init__(self):
		self.lat = 0
		self.lng = 0
		self.num_sv_in_view = 0
		self.num_sv_in_use = 0
		self.spd_over_grnd = 0
		self.horizontal_dil = 0
	def print_string(self):
		print "lat: ", self.lat, 
		"\nlng: ", self.lng, 
		"\nnum_sv_in_view: ", self.num_sv_in_view, 
		"\nnum_sv_in_use: ", self.num_sv_in_use, 
		"\nhorizontal_dil: ", self.horizontal_dil
	def count_sv(self,msg):
		count = 0
		for i in range(1,13):
			attr = "sv_id"
			if i < 10:
				attr = attr+"0"+str(i)
			else:
				attr = attr+str(i)
			try:
				int(getattr(msg,attr))
				count += 1
			except ValueError:
				pass
		return count

class ParseGPS(threading.Thread):
	def run(self):
		print "Reading GPS data..."
		while(True):
			line = ser.readline()
			try:
				msg = pynmea2.parse(line)
#				print type(msg)
				if isinstance(msg, pynmea2.types.GGA):
					if not hasattr(msg, 'latitude') or not hasattr(msg, 'longitude'):
						print "no satellite signal..."
						time.sleep(5)
						continue
					gps.horizontal_dil = msg.horizontal_dil
					gps.lat = msg.latitude
					gps.lng = msg.longitude
#					print "horizontal_dil:", gps.horizontal_dil
#					print "lat: ", gps.lat , "\nlng: ", gps.lng
				if isinstance(msg, pynmea2.types.GSA):
					gps.num_sv_in_use = gps.count_sv(msg)
#					print "num_sv_in_use: ", gps.num_sv_in_use
				if isinstance(msg, pynmea2.types.GSV):
					gps.num_sv_in_view = msg.num_sv_in_view
#					print "num_sv_in_view: ", gps.num_sv_in_view
			except ValueError:
				pass

def server(conn):
	conn.send("IAMAGPSAMA\n")
	while True:
		try:
			data = conn.recv(1024)
			if not data: 
				break
			l = [str(gps.lat), str(gps.lng), str(gps.num_sv_in_view), str(gps.num_sv_in_use), str(gps.horizontal_dil)]
			reply = ','.join(l)
			print reply
			conn.sendall(reply+"\n")
		except Exception:
 			break
	conn.close()




#Connect to GPS device at UART1 RX/TX
ser = serial.Serial(
		port='/dev/ttyO1',
		baudrate=4800#,
		#timeout=1
)

gps = GPS()

t1 = ParseGPS()
t1.start()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 1477))
sock.listen(5)

while 1:
	(conn, address) = sock.accept()
	start_new_thread(server ,(conn,))

