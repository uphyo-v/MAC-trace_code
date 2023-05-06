def dot_to_colon(mac):
	mac = mac.replace('.', '')
	raw_mac = ':'.join([mac[i : i + 2] for i in range(0, len(mac), 2)])
	return raw_mac

def colon_to_dot(mac):
	mac = mac.replace(":","")
	raw_mac = ".".join([mac[i:i+4] for i in range (0,len(mac),4)])
	return raw_mac


if __name__ == '__main__':
	with open('mac_list.txt','r', newline='', encoding  ='utf-8') as _:
		maclist = _.read().splitlines()
	for item in maclist:
		print(dot_to_colon(item))
		print(colon_to_dot(item))
