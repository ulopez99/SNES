#!/usr/bin/env python3
from Class.Functions import *
from Class.Node import Node
from skyfield.api import wgs84

class GroundStation(Node):
	#Varibles
	#	ECEF
	#	LLA
		
	#Functions
	#	__init__
	#	ECEF
	#	LLA
	
	def __init__(self,TOML_GS,network,nNodes):
		# Creates a GroundStation class object from three configuration lines
		name = TOML_GS['name']
		latitude = TOML_GS['latitude']
		longitude = TOML_GS['longitude']
		height = TOML_GS['height']
		threshold = TOML_GS['threshold']
		clone_VM = TOML_GS['clone_VM']
		self.position = wgs84.latlon(latitude,longitude,height)
		self.LLA = np.array([float(latitude),float(longitude),float(height)])
		self.ECEF = LLA2ECEF(self.LLA)
		Node.__init__(self,name = name,nNodes = nNodes,threshold = threshold,cloneVM = clone_VM,network = network)
	'''def __init__(self,name,line1,line2,nNodes,threshold=10e6):
		# Creates a GroundStation class object from three configuration lines
		vline1 = line1.split()
		vline2 = line2.split()
		self.LLA = np.array([float(vline1[0]),float(vline1[1]),float(vline1[2])])
		self.ECEF = LLA2ECEF(self.LLA)
		Node.__init__(self,name = name,nNodes = nNodes,threshold = threshold)'''
	def get_ECEF(self):
		# Return a array with the position in cartesian coordinates
		return self.ECEF
	def get_LLA(self):
		# Return a array with the position in geodesy coordinate system
		return self.LLA
	def update_position(self,date_time):
		pass
