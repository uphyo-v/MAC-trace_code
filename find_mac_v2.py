import re
import os
import argparse
from netmiko import ConnectHandler
from dotenv import dotenv_values
from mac_convert import MAC
def parse_variables_arguments():
	argParser = argparse.ArgumentParser()
	argParser.add_argument("-s", "--search_mask", help="lldp neighbor search mask")
	argParser.add_argument("-u", "--username", help="username")
	argParser.add_argument("-p", "--password", help='Password')
	argParser.add_argument("-m", "--mac", help="Mac address")
	argParser.add_argument("-t", "--devicetype", help="Device type: \
				'cisco_ios','dell_force10','arista_eos'")
	argParser.add_argument("-d", "--device", help="Device")
	args = argParser.parse_args()

	with open ('info.env', 'r', encoding='utf-8') as _:
		raw = _.read()
		if args.password or os.environ.get('PPP'):
			if os.environ.get('PPP'):
				pp = os.environ.get('PPP')
			if args.password:
				pp = args.password				
			if re.search(r'pp=.+',raw):
				raw = raw.replace(re.search(r'pp=.+',raw).group(), f'pp="{pp}"')
			else:
				raw = raw+f'pp={pp}\n'
		if args.username or os.environ.get('UUU'):
			if os.environ.get('UUU'):
				uu = os.environ.get('UUU')
			if args.username:
				uu = args.username				
			if re.search(r'uu=.+',raw):
				raw = raw.replace(re.search(r'uu=.+',raw).group(), f'uu="{uu}"')
			else:
				raw = raw+f'uu={uu}\n'
		if args.search_mask or os.environ.get('LLDP_SEARCH_MASK'):
			if os.environ.get('LLDP_SEARCH_MASK'):
				smask = os.environ.get('LLDP_SEARCH_MASK')
			if args.search_mask:
				smask = args.search_mask
			if re.search(r'lldp_search_mask=.+',raw):
				raw = raw.replace(re.search(r'lldp_search_mask=.+',raw).group(), f'lldp_search_mask="{smask}"')
			else:
				raw = raw+f'lldp_search_mask={smask}\n'
	if args.device:
		dlist = [args.device]
	else:
		with open ('devices_list.txt', 'r', encoding='utf-8') as _:
			dlist = _.read().splitlines()

	if args.mac:
		mlist = [args.mac]
	else:
		with open('mac_list.txt','r', newline='', encoding='utf-8') as _:
			mlist = _.read().splitlines()
	if args.devicetype:
		dtype = args.devicetype
	else:
		dtype = None
	return raw,dlist,mlist,dtype

def prgreen(message):
	'''Print Working'''
	os.system("")
	print('\033[0;32m'+message+'\033[0m')

def prred(message):
	'''Print Not Working'''
	os.system("")
	print('\033[0;31m'+message+'\033[0m')

def connect(ip_addr,username,password,devicetype):
	'''Connect SSH'''
	device={'ip': ip_addr, 'username': username, 'password': password, 'secret': password,\
	'device_type': devicetype}
	try:
		prgreen(f'\n>>>>> SSH-Connecting to {device["ip"]}')
		ssh_conn = ConnectHandler(**device)
		return ssh_conn
	except Exception as _:
		prred('\nxxxxxCannot connect with SSH')
		print('-'*30)
		return None

def disconnect(connection):
	'''Function disconnecting ssh client'''
	prgreen('>>>>> Disconnecting')
	connection.disconnect()
	prgreen('>>>>> Disconnected Successfully')
	print('-'*30)

def print_result(mac_result,ssh_client,interface):
	'''Function Prining result'''
	if mac_result:
		name = ssh_client.find_prompt().split(re.search('[#,>]',ssh_client.find_prompt()).group())[0]
		print(f'\t>>>>> {name}')
		print('\t>>>>> got mac')
		print('\t>>>>> '+interface)
		return name + ' ' + interface
	return None

def nothing():
	'''Function returning as nothing'''
	mac_a = 'NA'
	device='NA'
	status='stop'
	interface='NA'
	neigh=None
	dev_type = 'NA'
	return (mac_a,device,status,interface,neigh,dev_type)

def get_neighbor_details(ssh_client,interface,devicetype):
	''' Function checking neighbor details'''
	if "port-channel" in interface or "Po" in interface:
		if devicetype == 'arista_eos':
			pcs = ssh_client.send_command('show port-channel dense')
			for item in pcs.splitlines():
				if interface in item:
					seperate = item.split(" ")
					interface = (re.search(r"\b(eth|Et)[0-9]+",item).group())
					cmd = f'show lldp neighbors {interface} detail'

		if devicetype == 'dell_force10':
			pcs = ssh_client.send_command('show port-channel summary')
			for item in pcs.splitlines():
				if interface in item:
					seperate = item.split(" ")
					if 'p' in seperate[-2].split("(")[-1].lower():
						interface = 'ethernet '+seperate[-2].split("(")[0]

					cmd = f'show lldp neighbors interface {interface} detail'
	else:
		if devicetype == 'dell_force10':
			cmd = f'show lldp neighbors interface {interface} detail'
		else:
			cmd = f'show lldp neighbors {interface} detail'

	connected = ssh_client.send_command(cmd)
	return connected

def is_network_device_connected(connected,device,status,search_mask):
	''' Function checking if network device connected'''
	swi = re.search(f' {search_mask}[^\",^\n]+', connected)
	apt = re.search(r"[a-zA-Z][a-zA-Z][a-zA-Z]-apt*[0-9]+",connected)
	result_a = 'end device'
	if swi:
		result_a = swi.group()
		if "emc networking os10" in connected.lower():
			dev_type = "dell_force10"
		if "arista networks eos version" in connected.lower():
			dev_type = 'arista_eos'
		if "cisco" in connected.lower():
			dev_type = "cisco_ios"
		status = 'continue'
		device = result_a
		neigh = result_a

	elif apt:
		neigh = apt.group()
		dev_type = 'cisco_ios'
	else:
		__, __, status, __,neigh,dev_type = nothing()
		# if 'Endpoint' in connected:
		neigh = 'end device'
	return (device,dev_type,status,neigh)

def show_mac(ssh_client, mac_a,devicetype,path,cmd,interface):
	''' Function checking mac address and neighbor information'''
	mac_result = ssh_client.send_command(cmd)
	if 'Invalid' in mac_result:
		mac_result = ssh_client.send_command(f'show mac add | i {mac_a}')
	if len(mac_result)>1:
		interface = re.search(f"{interface}",mac_result).group()
		connected= get_neighbor_details(ssh_client,interface,devicetype)
		path.append (print_result(mac_result,ssh_client,interface))
	else:
		connected = False
	return connected, 'stop', interface

def find(ssh_client, mac_a,devicetype,path):
	""" Function finding neighbor and network devices"""
	info=dotenv_values('info.env')
	device=ssh_client.find_prompt().split('#')[0]
	if devicetype == 'dell_force10':
		mac_a = MAC(mac_a).to_colon()
		cmd = f'show mac address-table address {mac_a}'
		connected,status,interface = show_mac(ssh_client,mac_a,devicetype,path,cmd,\
					r'ethernet\d+/\d*/\d*|port-channel[0-9]+')
		if connected:
			device, dev_type, status, neigh = is_network_device_connected(connected,\
								 device,status,info['lldp_search_mask'])
		else:
			mac_a,device,status,interface,neigh,dev_type = nothing()

	if devicetype == 'cisco_ios':
		mac_a = MAC(mac_a).to_dot()
		cmd = f'show mac address-table | i {mac_a}'
		connected,status,interface = show_mac(ssh_client,mac_a,devicetype,path,cmd,\
					r'((g[i,iga]|G[i,iga]|[fa,Fa]|[Et,et]+)[0-9]/[0-9]+/*[0-9]*)|ether-channel[1-9]+[0-9]*')
		if connected:
			device, dev_type, status, neigh = is_network_device_connected(connected,\
								 device,status,info['lldp_search_mask'])
		else:
			mac_a,device,status,interface,neigh,dev_type = nothing()
			device=ssh_client.find_prompt().split('#')[0]
			dev_type = 'cisco_ios'
	if devicetype == 'arista_eos':
		mac_a = MAC(mac_a).to_dot()
		cmd = f'show mac address-table | i {mac_a}'
		connected,status,interface = show_mac(ssh_client,mac_a,devicetype,path,cmd,\
					r"Et\d+|Po[1-9]+[0-9]*")
		if connected:
			device, dev_type, status, neigh = is_network_device_connected(connected,\
								 device,status,info['lldp_search_mask'])

		else:
			mac_a,device,status,interface,neigh,dev_type = nothing()
			device=ssh_client.find_prompt().split('>')[0]
			dev_type = 'cisco_ios'
	return(device,status,interface,neigh,dev_type,path)

def find_mac(device,mac_addr,raw_data,dvt=None):
	"""Function finding mac address"""
	path =[]
	with open ('info.env','w', encoding='utf-8') as info:
		info.writelines(raw_data)
	info=dotenv_values('info.env')
	status = 'not-found'
	prgreen("\n"+'*'*60)
	prgreen(f'Searching mac addresss: {mac_addr}')
	prgreen('*'*60)
	if not dvt:
		dvt = 'dell_force10'
	while status != 'stop' or status != 'stop':
		print(dvt)
		ssh_client=connect(device,info['uu'],info['pp'],dvt)
		if ssh_client:
			device,status,interface,neigh,dvt,path= find(ssh_client, mac_addr, dvt,path)
			disconnect(ssh_client)
		else:
			status = 'stop'
			device = 'NA'
		## Found or not Found
		if status == 'stop':
			placeholder = ''
			if len(path) > 0:
				for swi in path:
					placeholder = placeholder + ' '+swi+'\n'
				if device == 'NA':
					prred('\t>>>>> Not found')
					response=f'Path: \n{placeholder}\n\t>>>>> Mac address:{mac_addr} is at {path[-1]}'
				else:
					response=f'Path: \n{placeholder}\n\t>>>>> Mac address:{mac_addr} is at {path[-1]} '
					if neigh:
						response=f'Path: \n{placeholder}\n\t>>>>> Mac address:{mac_addr}({neigh}) is at {device} {interface}'
				# return response
			# if device == 'NA':
			# 	prred('\t>>>>> Not found')
			# 	return None
			else:
				prred(f'\t>>>>> Mac address:{mac_addr} is Not Found')
				response = f'\t>>>>> Mac address:{mac_addr} is Not Found'
			return response


	return None

raw,devicelist, maclist,ditype = parse_variables_arguments()

result=[]
for d in devicelist:
	for mac in maclist:
		r=find_mac(d,mac,raw,ditype)
		if r:
			result.append(r)

if len(result) > 0:
	prgreen('\n'.join(result))
	print("\nResult lists:")
	for i in result:
		if "Not Found" in i:
			prred(i.splitlines()[-1])
		else:
			prgreen(i.splitlines()[-1])