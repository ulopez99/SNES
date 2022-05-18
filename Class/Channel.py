#!/usr/bin/env python3
from Class.Functions import Define_Channel
import subprocess
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
	
