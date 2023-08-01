
import macaddress

class MAC(macaddress.OUI):
	formats = macaddress.MAC.formats + (
		'xxxxxxxxxxxx',
		'xx:xx:xx:xx:xx:xx:xx',
		'xxxx.xxxx.xxxx'
	)

	def to_colon(self):
		raw_mac = str(self).replace('-', ':').lower()
		return raw_mac

	def to_dot(self):
		mac = str(self).replace("-","").lower()
		raw_mac = ".".join([mac[i:i+4] for i in range (0,len(mac),4)])
		return raw_mac
