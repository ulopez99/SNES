#!/usr/bin/env python3
from Class.Functions import *
from Class.Node import Node

class GroundStation(Node):
	#Varibles
	#	ECEF
	#	LLA
		
	#Functions
	#	__init__
	#	ECEF
	#	LLA
	
	def __init__(self,name,line1,line2,nNodes,threshold=10e6):
		# Creates a GroundStation class object from three configuration lines
		vline1 = line1.split()
		vline2 = line2.split()
		self.LLA = np.array([float(vline1[0]),float(vline1[1]),float(vline1[2])])
		self.ECEF = LLA2ECEF(self.LLA)
		Node.__init__(self,name = name,nNodes = nNodes,threshold = threshold)
	def get_ECEF(self):
		# Return a array with the position in cartesian coordinates
		return self.ECEF
	def get_LLA(self):
		# Return a array with the position in geodesy coordinate system
		return self.LLA
	def update_position(self,date_time):
		pass
