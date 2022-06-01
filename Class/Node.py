#!/usr/bin/env python3
import subprocess
import paramiko
import time
# mother class of Satellite and GroundStation
path = '/var/lib/libvirt/images/'
class Node:
	# Varibles
	# 	name
	#	ip
	#	threshold
	
	# Function
	#	__inint__
	
	def __init__(self,name,channels,cloneVM,network):
		self.name = name
		self.ip = network
		self.channels = channels
		self.clone_VM = cloneVM['name_VM']
		self.username = cloneVM['username']
		self.password = cloneVM['password']
	def get_VM_ip(self):
		while True:
			try:
				VM_ip = subprocess.run('virsh domifaddr %s'%(self.name), capture_output = True, text = True, shell = True).stdout.split('\n')[2].split()[3][:-3]
				return VM_ip
			except IndexError:
				pass
	def vlan_definition (self):
		node_numbre = int (str(self.ip).split('.')[-1].split('/')[0])
		VM_ip = self.get_VM_ip()
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		while True:
			try:
				ssh.connect(VM_ip,22, self.username, self.password)
				command = 'echo %s|sudo -S ip link add link enp1s0 name enp1s0.%d type vlan id %d;sudo ip addr add %s dev enp1s0.%d; sudo ip link set dev enp1s0.%d up' %(self.password,node_numbre,node_numbre,str(self.ip), node_numbre,node_numbre)
				ssh.exec_command(command)
				command = 'echo %s|sudo -S hostnamectl set-hostname %s'%(self.password,self.name)
				ssh.exec_command(command)
				break
			except paramiko.ssh_exception.NoValidConnectionsError:
				pass
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
			clone_VM = self.clone_VM
			errors = 1
			shutdown = False
			while errors != 0:
				errors = subprocess.run(['virt-clone', '--original', clone_VM, '--name', name, '--auto-clone']).returncode
				if errors > 0 and not(shutdown):
					subprocess.run(['virsh', 'shutdown', clone_VM])
					shutdown = True
			subprocess.run(['virsh', 'start', name])
		self.vlan_definition()
	def delete_VM(self):
		shell = 'virsh shutdown %s'%(self.name)
		subprocess.run(shell, capture_output = True, shell = True)
		shell = 'virsh undefine %s'%(self.name)
		subprocess.run(shell, capture_output = True, shell = True)
		shell = 'virsh destroy %s'%(self.name)
		subprocess.run(shell, shell = True)
		shell = 'find %s -type f -name %s*.qcow2 -delete'%(path,self.name)
		subprocess.run(shell, shell = True)
	def ssh_connection(self):
		Terminals = subprocess.run('ls /dev/pts', capture_output = True, text = True, shell = True).stdout.split()
		nTerminals_before = len(Terminals)
		VM_ip = self.get_VM_ip()
		shell = 'gnome-terminal -t %s -- sshpass -p %s ssh %s@%s'%(self.name,self.password,self.username,VM_ip)
		subprocess.run(shell, shell = True)
		time.sleep(0.1)
		Terminals = subprocess.run('ls /dev/pts', capture_output = True, text = True, shell = True).stdout.split()
		nTerminals = len(Terminals)
		if nTerminals_before == nTerminals:
			shell = 'gnome-terminal -t %s -- ssh %s@%s'%(self.name,self.username,VM_ip)
			subprocess.run(shell, shell = True)
	def get_ECEF(self):
		return self.position.itrs_xyz.m
	def get_LLA(self):
		return [self.position.latitude.degrees,self.position.longitude.degrees,self.position.elevation.m]
