#!/usr/bin/env python3
from Class.Orbit import Orbit
from Class.Node import Node


class Satellite(Node):
	# Varibles
	# 	ID
	#	Orbit
	#	ECEF
	#	LLA
	#	ECI
	
	#Functions
	# 	__init__
	#	ECEF
	#	LLA
	#	ECI
	def __init__(self,sat,constallation,network):
		# Creates a satellite class object from three configuration lines
		self.ID = sat.model.satnum
		self.Orbit = Orbit(sat)
		Node.__init__(self,name = sat.name,channels = constallation['channels'], cloneVM = constallation['clone_VM'],network = network)
	def get_ECI(self,esec = None,date_time=None):
		# Return a array in cartesion coordinate system with the current position or in a time diference in seconds with respect to the ToA (Time of Aplicability)
		return self.Orbit.ECI(date_time=date_time)[0]
	def update_position(self,t_skyfield):
		self.position = self.Orbit.get_position(t_skyfield)
