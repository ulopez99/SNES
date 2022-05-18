#!/usr/bin/env python3
import subprocess
# mother class of Satellite and GroundStation
class Node:
	# Varibles
	# 	name
	#	ip
	#	threshold
	
	# Function
	#	__inint__
	
	def __init__(self,name,nNodes,threshold,cloneVM = 'default'):
		self.name = name
		self.ip = '10.0.0.%d/24'%(nNodes+1)
		self.threshold = threshold
		self.default_VM = cloneVM
	def vlan_definition (self):
		node_numbre = int (self.ip.split('.')[-1].split('/')[0])
		while True:
			try:
				VM_ip = subprocess.run('virsh domifaddr %s'%(self.name), capture_output = True, text = True, shell = True).stdout.split('\n')[2].split()[3][:-3]
				break
			except IndexError:
				pass
		shell = "ssh -t ubuntu@%s 'sudo ip link add link enp1s0 name enp1s0.%d type vlan id %d;sudo ip addr add %s dev enp1s0.%d; sudo ip link set dev enp1s0.%d up'"%(VM_ip,node_numbre,node_numbre,self.ip, node_numbre,node_numbre)
		while True:
			errors = subprocess.run(shell, shell = True).returncode
			if int(errors) == 0:
				break
	def run_VM(self):
		name = self.name
		VM_status = subprocess.run('virsh list --all | grep -w %s'%(name), capture_output = True, text = True, shell = True).stdout
		if len(VM_status)>0:
			VM_status = VM_status.split()[2]
			if VM_status == 'shut':
				subprocess.run(['virsh', 'start', name])
			elif VM_status == 'paused':
				subprocess.run(['virsh', 'resume', name])
		else:
			default_VM = 'default'
			errors = 1
			shutdown = False
			while errors != 0:
				errors = subprocess.run(['virt-clone', '--original', default_VM, '--name', name, '--auto-clone'],capture_output = True).returncode
				if errors > 0 and not(shutdown):
					subprocess.run(['virsh', 'shutdown', default_VM])
					shutdown = True
			subprocess.run(['virsh', 'start', name])
		self.vlan_definition()
