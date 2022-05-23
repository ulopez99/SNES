#!/usr/bin/env python3
import subprocess
from Class.Functions import Define_Channel
from skyfield.api import load

ts = load.timescale()

class channel:
	matrix = []
	exist_channel = False
	def __inint__(self):
		self.matrix=[]
		self.exist_channel = False
	def AddNode(self,node_list,nNodes,time_parameters):
		old_matrix = self.matrix
		self.matrix = []
		new_row = []
		for n in range(0,nNodes-1):
			vector = []
			vector = old_matrix [n]
			delay = Define_Channel(node_list[n],node_list[nNodes-1],time_parameters.get_date_time())
			if not(self.exist_channel) and delay != -1:
				self.exist_channel = True
			vector.append(delay)
			new_row.append(delay)
			self.matrix.append(vector)
		new_row.append(0)
		self.matrix.append(new_row)
	def update(self,node_list,nNodes,date_time,EMU,root_interface):
		old_matrix = self.matrix
		self.matrix = []
		self.exist_channel = False
		for n in range(0,nNodes):
			vector = []
			marker = 0
			for j in range(0,nNodes):
				if j >= marker:
					node_list[j].update_position(date_time)
					marker = j+1	
				if j < n :
					delay = self.matrix[j][n]
				elif n == j:
					delay = 0
				else:
					delay = Define_Channel(node_list[n],node_list[j],date_time)
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
	def Define_Channel(node, other,date_time = None):
		threshold = (node.threshold + other.threshold)/2	
		if type(node).__name__ == "Satellite" and type(other).__name__ == "Satellite":
			LoS, delay = Satellite2Satellite(node.ECEF,other.ECEF,threshold)
			 
		elif type(node).__name__ != "Satellite" and type(other).__name__ == "Satellite":
			LoS, delay = GroundBase2Satellite(other.ECEF,node.ECEF,node.LLA,0,threshold)
			
		elif type(node).__name__ == "Satellite" and type(other).__name__ != "Satellite":
			LoS, delay = GroundBase2Satellite(node.ECEF,other.ECEF,other.LLA,0,threshold)
		else:
			LoS = False
			delay = -1
		return delay
	def GroundBase2Satellite(ECEF_SAT,ECEF_GB,LLA_GB,Min,threshold):
		difference = satellite.Orbit.TLE - GS.position
		t = ts.from_datetime(date_time)
		topocentric = difference.at(t)
		alt, az, distance = topocentric.altaz()
		if (alt.degrees >= Min) and distance.m < threshold:
			LoS = True
			delay = distance.m/c*1e3
		else:
			LoS = False
			delay = -1
		return LoS, delay

	#Compute the delay between two SATs if the line between them not croos the earth and the distance is less than a maximum
	def Satellite2Satellite(ECEF1,ECEF2,threshold):
		#The point closest to the center of the earth of the line joining two satellites is calculated to determine if it crosses the earth, so there is no direct vision
		#(x,y,z) = (x0,y0,z0) + alpha*(vx,vy,vz) equation of the straight line in 3D
		#vx*x+vy*y+vz*z = 0 Plane perpendicular to the straight line passing through the point P(0,0,0)
		#The point where the line and the plane intersect is calculated and compared with the ellipsoid that defines the earth
		#(x²+y²)/a²+z²/b²= 1 If we increase the values of a and b we can discard sight passing through the atmosphere, in case it is considered to add too much attenuation.
		
		v = ECEF1 - ECEF2
		alpha = -(np.dot(ECEF1,v))/(np.dot(v,v))
		# If alpha is not between 0 and -1, the earth does not lie between the two satellites. 
		# alpha = (x-x0)/vx = (y-y0)/vy = (z-z0)/vz If v is not 0

		if -1 < alpha < 0:
			xyz = ECEF1+alpha*v
		else:
			xyz = np.array([a_Earth,a_Earth,b])
		d = math.sqrt(v[0]**2+v[1]**2+v[2]**2)
		if ((xyz[0]**2+xyz[1]**2)/a_Earth**2+xyz[2]**2/b**2>1) and d < threshold:
			LoS = True
			delay = d/c*1e3
		else:
			LoS = False
			delay = -1
		return LoS, delay
