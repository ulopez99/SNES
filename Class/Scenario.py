#!/usr/bin/env python3
from Class.Functions import *
from Class.Satellite import Satellite
from Class.Ground_Station import GroundStation
from Class.Time_parameters import time_parameters
from Class.Channel import channel
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
	
	def __init__(self,TOMLfile):
		self.time_parameters = time_parameters(TOMLfile['Time'])
		self.node_list = []
		self.channel = channel()
		self.nNodes = 0
		network = TOMLfile['Network']['network']
		self.interface = TOMLfile['Network']['interface']
		for n in range(0,TOMLfile['SatelliteConstellations']['number_constellations']):
			Constellation = TOMLfile['SatelliteConstellations'][str(n)]
			config_file = Constellation['config_file']
			#Open file
			fo = open(config_file, "r")
			line0 = fo.readline()
			line1 = fo.readline()
			line2 = fo.readline()
			#Read all the line of the file and creates the scenario
			while (line0 != "" and line1 != "" and line2 != ""):
				self.AddSatellite(line0,line1,line2,Constellation['threshold'],Constellation['clone_VM'],network)
				line0 = fo.readline()
				line1 = fo.readline()
				line2 = fo.readline()
			# Close opened file
			fo.close()
		for n in range(0,TOMLfile['GroundStations']['number_GS']):
			GS = TOMLfile['GroundStations'][str(n)]
			self.AddGroundStation(GS,network)
	def AddSatellite(self,line0,line1,line2,threshold,clone_VM,network):
		if self.nNodes < 254:
			try:
				name = line0.split()[0]
				SAT = Satellite(name,line1,line2,threshold,clone_VM,network,self.nNodes)
			except ValueError:
				print ("Node not accepted: Error in the format of the file")
				pass
			except IndexError:
				print ("Node not accepted: Error in the format of the file")
				pass
			if Exist_Node(self.node_list,SAT,self.nNodes):
				print ("- Satellite %s: NOT ACCEPTED"%(SAT.name))
			else:
				self.node_list.append(SAT)
				print ("- Satellite %s: ADDED"%(SAT.name))
				self.node_list[self.nNodes].update_position(self.time_parameters.get_date_time())	
				self.nNodes += 1
				self.channel.AddNode(self.node_list,self.nNodes,self.time_parameters)
		else:
			print ('Maximum number of nodes exceeded: Node NOT ACCEPTED')
	def AddGroundStation(self,TOML_GS,network):
		if self.nNodes < 254:
			try:
				GS = GroundStation(TOML_GS = TOML_GS, network = network, nNodes = self.nNodes)
			except ValueError:
				print ("Node not accepted: Error in the format of the file")
				return None
			except IndexError:
				print ("Node not accepted: Error in the format of the file")
				return None
		
			if Exist_Node(self.node_list,GS,self.nNodes):
				print ("- Ground Station %s: NOT ACCEPTED"%(GS.name))
				return None
			else:
				self.node_list.append(GS)
				print ("- Ground Station %s: ADDED"%(GS.name))
				self.node_list[self.nNodes].update_position(self.time_parameters.get_date_time())	
				self.nNodes += 1
				self.channel.AddNode(self.node_list,self.nNodes,self.time_parameters)
		else:
			print ('Maximum number of nodes exceeded: Node NOT ACCEPTED')	
	'''def __init__(self,TotalTime = 24,TimeInterval = 1,date_time: str = None, speed = 1):
		self.time_parameters = time_parameters(TotalTime,TimeInterval,date_time,speed)
		self.node_list = []
		self.channel = channel()
		self.nNodes = 0
		self.interface = 'virbr0'''
		
	def AddNode (self,line0:str ,line1:str,line2:str):
		# From the three lines of the configuration file a new node is created and added to a list. Subsequently, the channel matrix is updated with the delay information of each link.
		if self.nNodes < 254:
			vline0 = line0.split()
			if len(vline0) > 1:
				if vline0[0] == "SAT":
					try:
						SAT = Satellite(vline0[1],line1,line2,self.nNodes)
					except ValueError:
						print ("Node not accepted: Error in the format of the file")
						return None
					except IndexError:
						print ("Node not accepted: Error in the format of the file")
						return None
					if Exist_Node(self.node_list,SAT,self.nNodes):
						print ("- Satellite %s: NOT ACCEPTED"%(SAT.name))
						return None
					else:
						self.node_list.append(SAT)
						print ("- Satellite %s: ADDED"%(SAT.name))
					
				else:
					try:
						GS = GroundStation(vline0[1],line1,line2,self.nNodes)
					except ValueError:
						print ("Node not accepted: Error in the format of the file")
						return None
					except IndexError:
						print ("Node not accepted: Error in the format of the file")
						return None
				
					if Exist_Node(self.node_list,GS,self.nNodes):
						print ("- Satellite %s: NOT ACCEPTED"%(GS.name))
						return None
					else:
						self.node_list.append(GS)
						print ("- Satellite %s: ADDED"%(GS.name))
			else:
				print ("Node not accepted: Error in the format of the file")
				return None
			self.node_list[self.nNodes].update_position(self.time_parameters.get_date_time())	
			self.nNodes += 1
			self.channel.AddNode(self.node_list,self.nNodes,self.time_parameters)
		else:
			print ('Maximum number of nodes exceeded: Node NOT ACCEPTED')
			return None
		
	def update(self,date_time = None,EMU = False):
		# channel_matrix is updated with the delay at one precise time instant.
		# EMU equals True, update the rules of the interfaces to represent the delay
		if date_time == None:
			date_time = self.time_parameters.get_date_time()
		self.channel.update(self.node_list,self.nNodes,date_time,EMU,self.interface)
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
		
	def set_TotalTime(self,TotalTime):
		# change the parameter TotalTime
		return self.time_parameters.set_TotalTime(TotalTime)
	def set_TimeInterval(self,TimeInterval):
		# change the parameter TimeInterval
		return self.time_parameters.set_TimeInterval(TimeInterval)	
	def set_date_time(self,date_time):
		# change the parameter date_time and initial_date_time
		if self.time_parameters.set_date_time(date_time):
			self.update()
			return True
		else:
			return False
	def set_speed(self,speed):
		# change the parameter speed
		return self.time_parameters.set_speed(speed)
	def get_speed(self):
		return self.time_parameters.get_speed(self.channel.get_exist())
	def start_VMs (self):
		exist_net = subprocess.run('virsh net-list | grep -c -w default', capture_output = True, text = True, shell = True).stdout
		if int(exist_net) == 0:
			subprocess.run(['virsh', 'net-start', 'default'])
		for n in range(0,self.nNodes):
			self.node_list[n].run_VM()
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
