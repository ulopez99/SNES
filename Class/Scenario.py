#!/usr/bin/env python3
from Class.Satellite import Satellite
from Class.Ground_Station import GroundStation
from Class.Time_parameters import time_parameters
from Class.Channel import channel
from skyfield.api import load, wgs84
from ipaddress import IPv4Network
import time
import subprocess


# class for the creation and management of nodes and channels. 
class scenario:

	# Varibles
	# 	node_list: Vector of nodes
	# 	channel_matrix: Matrix with the delay between nodes. If there is no contact between them, that position is determined with a -1
	# 	nNodes: Counter of existing nodes in the scenario
	#	TotalTime: duration of execution
	#	TimeInterval: periodicity with which the samples are updated
	#	date_time:instant of measurement if it is None date_time is the current time
	#	initial_date_time: instant when the emulation starts if it is None initial_date_time is the current time
	#	speed: speed at which time passes
	#	interface: intterface where the VMs are connected
	
	node_list = []
	matrix = []
	nNodes = 0
	TotalTime = 24			#[h]
	TimeInterval = 1		#[min]
	speed = 1
	date_time = None
	initial_date_time = None
	interface = 'virbr0'
	
	# Functions
	#	__init__
	# 	AddNode 
	# 	updete 
	#	delate
	#	step
	#	reset
	#	write_bash
	#	set_TotalTime
	#	set_TimeInterval
	#	set_date_time
	#	set_speed
	
	def __init__(self,TOMLfile,run_VM = True):
		self.start_Network()
		self.time_parameters = time_parameters(TOMLfile['Time'])
		self.node_list = []
		self.ip_Address = []
		self.channel = channel(TOMLfile['Channel'])
		self.nNodes = 0
		ip_Address = []
		Network = TOMLfile['Network']['network']
		while True:
			try:
				for addr in IPv4Network(Network):
					ip_Address.append(addr)
				break
			except ValueError:
				Network = input('%s is not a possible network. Insert a correct one:'%(Network)) 
		self.ip_Address = ip_Address[1:-1]
		self.interface = TOMLfile['Network']['interface']
		SpaceSegment = TOMLfile['SpaceSegment']
		for SatelliteSistem in SpaceSegment['SatelliteSistem']:
			config_file = SatelliteSistem['TLE']
			satellites = load.tle_file(config_file)
			for sat in satellites:
				self.AddSatellite(sat,SatelliteSistem,run_VM)
		GroundSegment = TOMLfile['GroundSegment']
		for GroundSistem in GroundSegment['GroundSistem']:
			self.AddGroundStation(GroundSistem,run_VM)
	def AddSatellite(self,sat,constallation,run_VM):
		try:
			name = sat.name
			SAT = Satellite(sat,constallation,self.ip_Address[self.nNodes])
			if self.Exist_Node(SAT):
				print ("- Satellite %s: NOT ACCEPTED"%(SAT.name))
			else:
				self.node_list.append(SAT)
				print ("- Satellite %s: ADDED"%(SAT.name))
				if run_VM: SAT.run_VM()
		except IndexError:
			print ('Maximum number of nodes exceeded: Node NOT ACCEPTED')
			return
		self.node_list[self.nNodes].update_position(self.time_parameters.get_t_skyfield())	
		self.nNodes += 1
		self.channel.AddNode(self.node_list,self.nNodes,self.time_parameters.get_t_skyfield())

	def AddGroundStation(self,TOML_GS,run_VM):
		try:
			GS = GroundStation(TOML_GS = TOML_GS, network = self.ip_Address[self.nNodes])
			if self.Exist_Node(GS):
				print ("- Ground Station %s: NOT ACCEPTED"%(GS.name))
				return None
			else:
				self.node_list.append(GS)
				print ("- Ground Station %s: ADDED"%(GS.name))
				if run_VM: GS.run_VM()
		except IndexError:
			print ('Maximum number of nodes exceeded: Node NOT ACCEPTED')
			return
		self.node_list[self.nNodes].update_position(self.time_parameters.get_t_skyfield())	
		self.nNodes += 1
		self.channel.AddNode(self.node_list,self.nNodes,self.time_parameters.get_t_skyfield())			
	def update(self,EMU = False):
		# channel_matrix is updated with the delay at one precise time instant.
		# EMU equals True, update the rules of the interfaces to represent the delay
		t_skyfield = self.time_parameters.get_t_skyfield()
		self.channel.update(self.node_list,self.nNodes,t_skyfield,EMU,self.interface)
	def delate (self):
		# delate all the nodes and channels
		self.node_list = []
		self.channel.delete()
		self.nNodes = 0
	def step(self,EMU = False,CESIUM = False):
		# change date_time and update the scenario
		if self.time_parameters.step():
			return True
		else:
			self.update(EMU = EMU)
			return False
	def reset(self):
		# restart the parameters of simulatión, put date_time equal to initial_date_time and update de scenario
		self.time_parameters.reset()
		self.update()
	def write_bash (self):
		# write two bash files for define the scenario and delete the configuration of the first file.
		w_runtime = open("runtime_bash.sh", "w")
		w_shutdown = open("shutdown_bash.sh", "w")
		w_runtime.write('#!/bin/sh\n')
		w_shutdown.write('#!/bin/sh\n')
		w_runtime.write('brctl addbr brSATEMU\nip link set dev brSATEMU up\n')
		w_shutdown.write('ip link set dev brSATEMU down\nbrctl delbr brSATEMU\n')
		interface = self.interface
		for n in range(1,self.nNodes+1):
			# Define an interface in a VLAN
			line_runtime = str('ip link add link %s name %s.%d type vlan id %d\n'%(interface,interface,n,n))
			w_runtime.write(line_runtime)
			line_runtime = str('ip link set dev %s.%d up\n'%(interface,n))
			w_runtime.write(line_runtime)
			line_runtime = str('brctl addif brSATEMU %s.%d\n'%(interface,n))
			w_runtime.write(line_runtime)
			line_runtime = str('tc qdisc add dev %s.%d root handle %d: htb\n'%(interface,n,n))
			w_runtime.write(line_runtime)
			line_shutdown = str('tc qdisc del dev %s.%d root handle %d: htb\n'%(interface,n,n))
			w_shutdown.write(line_shutdown)
			# Delete the interface associated with the VLAN 
			line_shutdown = str('ip link del link %s name %s.%d type vlan id %d\n'%(interface,interface,n,n))
			w_shutdown.write(line_shutdown)
		for n in range(1,self.nNodes+1):
			for j in range(1,self.nNodes+1):
				line_runtime = str('tc class add dev %s.%d parent %d: classid %d:%d htb rate 100mbit\n'%(interface,n,n,n,j))
				w_runtime.write(line_runtime)
				# Add the conditions of the channel
				#delay = self.channel_matrix[n-1][j-1]
				delay = self.channel.get_channel(n-1,j-1)
				if delay == -1:
					line_runtime = str('tc qdisc add dev %s.%d parent %d:%d handle %d%d: netem loss 100'%(interface,n,n,j,n,j))
					line_runtime = line_runtime + '%\n'
				else:
					line_runtime = str('tc qdisc add dev %s.%d parent %d:%d handle %d%d: netem delay %fms\n'%(interface,n,n,j,n,j,delay))
				w_runtime.write(line_runtime)
				# Define filters according to iptables marks 
				line_runtime = str('tc filter add dev %s.%d protocol ip parent %d:0 prio 1 handle %d fw flowid %d:%d\n'%(interface,n,n,n,n,j))
				line_runtime = str('tc filter add dev %s.%d protocol ip parent %d:0 prio 1 u32 match ip src 10.0.0.%d/32 flowid %d:%d\n'%(interface,n,n,j,n,j))
				w_runtime.write(line_runtime)
				# Delete the filters
				line_shutdown = str('tc filter del dev %s.%d protocol ip parent %d:0 prio 1 handle %d fw flowid %d:%d\n'%(interface,n,n,n,n,j))
				line_shutdown = str('tc filter del dev %s.%d protocol ip parent %d:0 prio 1 u32 match ip src 10.0.0.%d/32 flowid %d:%d\n'%(interface,n,n,j,n,j))
				#w_shutdown.write(line_shutdown)
		# Close opened files
		w_runtime.close()
		w_shutdown.close()
		# Make the files executable
		subprocess.run(['chmod', '+x', 'runtime_bash.sh'])
		subprocess.run(['chmod', '+x', 'shutdown_bash.sh'])
	def get_speed(self):
		return self.time_parameters.get_speed(self.channel.get_exist())
	def start_Network (self):
		exist_net = subprocess.run('virsh net-list | grep -c -w default', capture_output = True, text = True, shell = True).stdout
		if int(exist_net) == 0:
			subprocess.run(['virsh', 'net-start', 'default'])
	def run(self,stop_threads,EMU,CESIUM):
		print (self.time_parameters.get_date_time())
		print ('-Delay SAT1->SAT2: ',self.channel.get_channel(0,1))
		print ('-Delay SAT1->i2CAT: ',self.channel.get_channel(0,2))
		print ('-Delay SAT2->i2CAT: ',self.channel.get_channel(1,2))
		time.sleep(60*self.time_parameters.get_TimeInterval()/self.get_speed())
		while True:
			if stop_threads:
				break
			if self.step(EMU,CESIUM):
				print('The emulation is over: press enter to shutdown')
				break
			print (self.time_parameters.get_date_time())
			print ('-Delay SAT1->SAT2: ',self.channel.get_channel(0,1))
			print ('-Delay SAT1->i2CAT: ',self.channel.get_channel(0,2))
			print ('-Delay SAT2->i2CAT: ',self.channel.get_channel(1,2))
			#print (scenario.channel_matrix)
			time.sleep(60*self.time_parameters.get_TimeInterval()/self.get_speed())
		if EMU:subprocess.call('./shutdown_bash.sh')
	def delete_VMs (self):
		for n in range(0,self.nNodes):
			self.node_list[n].delete_VM()
	def Exist_Node(self,New_node):
		exist = False
		n = 0
		for Node in self.node_list:
			if type(New_node).__name__ == "Satellite" and type(Node).__name__ == "Satellite":
				if Node.ID == New_node.ID or Node.name == New_node.name:
					return True
			elif type(New_node).__name__ == "GroundStation" and type(Node).__name__ == "GroundStation":
				if Node.name == New_node.name:
					return True		
		return False	 		
