#!/usr/bin/env python3
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
	
	def __init__(self,TOML_GS,network):
		# Creates a GroundStation class object from three configuration lines
		name = TOML_GS['name']
		latitude = TOML_GS['latitude']
		longitude = TOML_GS['longitude']
		height = TOML_GS['height']
		channels = TOML_GS['channels']
		clone_VM = TOML_GS['clone_VM']
		self.position = wgs84.latlon(latitude,longitude,height)
		Node.__init__(self,name = name,channels = channels,cloneVM = clone_VM,network = network)
	'''def get_ECEF(self):
		# Return a array with the position in cartesian coordinates
		return self.ECEF
	def get_LLA(self):
		# Return a array with the position in geodesy coordinate system
		return self.LLA'''
	def update_position(self,date_time):
		pass
