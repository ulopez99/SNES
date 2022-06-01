#!/usr/bin/env python3
import subprocess
from Class.Functions import Satellite2Satellite,GroundBase2Satellite
from Class.channel_threshold import threshold
from skyfield.api import load
import math

#GLOBAL CONSTANTS
G = 6.67384e-11;            			# Gravitational constant [m3 kg-1 s-2]
M = 5.972e+24;              			# Earth mass [kg]
dOmegaEarth = 7.2921151467e-5			# Angular speed of Earth rotation [rad/s]
a_Earth = 6378137 				# Earth major semi axis [m]
e_2 = 0.00669437999014				# Square Earth eccentricity
c = 3e8					# Speed of light [m/s]
b = math.sqrt(a_Earth**2-(e_2*a_Earth**2))	# Earth menor semi axis [m]
MJ2022 = 59580.0 				# MJD on 1/1/2022 at 00:00 UTC (see http://leapsecond.com/java/cal.htm)
ts = load.timescale()

class channel:
	matrix = []
	exist_channel = False
	def __init__(self,channel):
		self.matrix=[]
		self.threshold_vector = []
		self.exist_channel = False
		channel_thresholds = channel['threshold']
		for channel_threshold in channel_thresholds:
			self.threshold_vector.append(threshold(channel_threshold))
	def AddNode(self,node_list,nNodes,t_skyfield):
		old_matrix = self.matrix
		self.matrix = []
		new_row = []
		for n in range(0,nNodes-1):
			vector = []
			vector = old_matrix [n]
			delay = self.Define_Channel(node_list[n],node_list[nNodes-1],t_skyfield)
			if not(self.exist_channel) and delay != -1:
				self.exist_channel = True
			vector.append(delay)
			new_row.append(delay)
			self.matrix.append(vector)
		new_row.append(0)
		self.matrix.append(new_row)
	def update(self,node_list,nNodes,t_skyfield,EMU,root_interface):
		old_matrix = self.matrix
		self.matrix = []
		self.exist_channel = False
		for n in range(0,nNodes):
			vector = []
			marker = 0
			for j in range(0,nNodes):
				if j >= marker:
					node_list[j].update_position(t_skyfield)
					marker = j+1	
				if j < n :
					delay = self.matrix[j][n]
				elif n == j:
					delay = 0
				else:
					delay = self.Define_Channel(node_list[n],node_list[j],t_skyfield)
					if delay != -1 and not(self.exist_channel):
						self.exist_channel = True
				vector.append(delay)
				if EMU and old_matrix[n][j]!=delay:
					interface = '%s.%d'%(root_interface,n+1)
					n_j = '%d:%d' %(n+1,j+1)
					nj = '%d%d:' %(n+1,j+1)
					if delay == -1:
						subprocess.run(['tc','qdisc','change','dev',interface,'parent',n_j,'handle',nj,'netem','loss','100%'])
					elif delay != 0:
						
						str_delay = '%fms' % (delay)
						subprocess.run(['tc','qdisc','change','dev',interface,'parent',n_j,'handle',nj,'netem','delay',str_delay])
			self.matrix.append(vector)
			
	def delete(self):
		self.matrix = []
		self.exist_channel = False
	def get_channel(self,node1 = None,node2 = None):
		if (node1 == None and node2 == None):
			return self.matrix
		elif node2 == None:
			return self.matrix[node1]
		elif node1 == None:
			return self.matrix[:][node2]
		return self.matrix[node1][node2]
	def get_exist(self):
		return self.exist_channel
	def search_channel(self,ID):
		cont = 0
		for threshold in self.threshold_vector:
			if ID == threshold.get_id():
				return cont
			cont +=1
	
	def Define_Channel(self,node, other,t_skyfield):
		n = 0
		found = False
		while n < len(node.channels) and not(found):
			j = 0
			while n < len(node.channels) and not(found):
				if node.channels[n] == other.channels[j]:
					found = True
					ID = node.channels[n]
				else: 
					j +=1
			n += 1
		threshold_pos = self.search_channel(ID)
		if type(node).__name__ == "Satellite" and type(other).__name__ == "Satellite":
			threshold = self.threshold_vector[threshold_pos].get_Satellite2Satellite()
			LoS, delay = self.Satellite2Satellite(node.get_ECEF(),other.get_ECEF(),threshold)
			 
		elif type(node).__name__ != "Satellite" and type(other).__name__ == "Satellite":
			threshold = self.threshold_vector[threshold_pos].get_Ground2Satellite()
			LoS, delay = self.GroundBase2Satellite(other,node,0,threshold,t_skyfield)
			
		elif type(node).__name__ == "Satellite" and type(other).__name__ != "Satellite":
			threshold = self.threshold_vector[threshold_pos].get_Ground2Satellite()
			LoS, delay = self.GroundBase2Satellite(node,other,0,threshold,t_skyfield)
		else:
			LoS = False
			delay = -1
		return delay
	def GroundBase2Satellite(self, SAT ,GS ,MinAngle,threshold,t_skyfield):
		difference = SAT.Orbit.TLE - GS.position
		topocentric = difference.at(t_skyfield)
		alt, az, distance = topocentric.altaz()
		if (alt.degrees >= MinAngle) and distance.m < threshold:
			LoS = True
			delay = distance.m/c*1e3
		else:
			LoS = False
			delay = -1
		return LoS, delay
	def Satellite2Satellite(self,ECEF1,ECEF2,threshold):
		#Find the angle of the cone
		#Note: it can never be greater than 90 º provided that earth_radius <
		#norm (src)
		Er = a_Earth
		norm1 = math.sqrt(ECEF1[0]**2+ECEF1[1]**2+ECEF1[2]**2)
		ECEF1_norm = ECEF1/norm1
		theta = math.asin(Er/norm1)
		diff_vec = ECEF1 - ECEF2
		diff_norm = math.sqrt(diff_vec[0]**2+diff_vec[1]**2+diff_vec[2]**2)
		diff_vec_norm = diff_vec/diff_norm
		dot_res = diff_vec_norm[0] * ECEF1_norm [0] + diff_vec_norm[1] * ECEF1_norm [1] + diff_vec_norm[2] * ECEF1_norm [2]
		diff_angle = math.acos(abs(dot_res))
		if diff_angle > theta and threshold > diff_norm:
			delay = diff_norm/c*1e3
			return True,delay
		else:
			h = norm1-Er
			if diff_norm > h:
				return False,-1
			elif threshold > diff_norm:
				delay = diff_norm/c*1e3
				return True,delay
