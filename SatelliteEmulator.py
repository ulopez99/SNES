from Class.Scenario import scenario
from datetime import datetime,timedelta

import threading
import time
import subprocess
import toml
import sys
from collections import deque
stop_threads = False
def run(Scenario,EMU,CESIUM):
	global stop_threads
	time.sleep(1)
	n_connections = int(1+(Scenario.nNodes-1)*Scenario.nNodes/2)
	queue = deque([], n_connections)
	String = Scenario.time_parameters.get_date_time().strftime("%m/%d/%Y, %H:%M:%S")
	for _ in range(len(queue)):
		sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
	queue.append(String)
	for i in range(len(queue)):
		sys.stdout.write(queue[i] + "\n") # reprint the lines
	for n in range(Scenario.nNodes):
		for j in range(n+1,Scenario.nNodes):
			String =  '-Delay %s -> %s:	 %fms'%(Scenario.node_list[n].name,Scenario.node_list[j].name,Scenario.channel.get_channel(n,j))
			for _ in range(len(queue)):
				sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
			queue.append(String)
			for i in range(len(queue)):
				sys.stdout.write(queue[i] + "\n") # reprint the linesprint (String)
	time.sleep(60*Scenario.time_parameters.get_TimeInterval()/Scenario.get_speed())
	while True:
		if stop_threads:
			break
		if Scenario.step(EMU,CESIUM):
			print('The emulation is over: press enter to shutdown')
			break
			
		String = Scenario.time_parameters.get_date_time().strftime("%m/%d/%Y, %H:%M:%S")
		for _ in range(len(queue)):
			sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
		queue.append(String)
		for i in range(len(queue)):
			sys.stdout.write(queue[i] + "\n") # reprint the lines
		for n in range(Scenario.nNodes):
			for j in range(n+1,Scenario.nNodes):
				String =  '-Delay %s -> %s:	 %fms'%(Scenario.node_list[n].name,Scenario.node_list[j].name,Scenario.channel.get_channel(n,j))
				for _ in range(len(queue)):
					sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
				queue.append(String)
				for i in range(len(queue)):
					sys.stdout.write(queue[i] + "\n") # reprint the linesprint (String)
		time.sleep(60*Scenario.time_parameters.get_TimeInterval()/Scenario.get_speed())

	for _ in range(len(queue)+2):
		sys.stdout.write("\x1b[1A\x1b[2K") # move up cursor and delete whole line
	subprocess.call('./shutdown_bash.sh')
def main():
	print ("Hi, you have started the satellite network emulator.")
	#Open file
	fo = open('config.toml', "r")
	TOML = toml.load(fo, _dict=dict)
	Scenario = scenario(TOML)
	while True:
		inp = input("Insert the action you wish to perform (insert 'help' to see all available actions): ").strip().lower()
		if inp == "help":
			print ("- help: shows all available actions\n- scenario: show the load nodes and his type\n- run_all: run the emulation and Cesium\n- run_emulator: run only the emulation\n- run_CESIUM: run only the visulization at Cesium\n- exit: program execution ends")
		elif inp == "scenario":
			print("The scenario is formed by ",Scenario.nNodes," Nodes")
			if Scenario.time_parameters.get_date_time() == None:
				print ('The emulator is working at current time')
			else:
				print ('Initialize:',Scenario.time_parameters.get_initial_date_time(),'	Ends:',Scenario.time_parameters.end_date_time)
			for n in range(0,Scenario.nNodes):
				print ('Node',n+1,": ",Scenario.node_list[n].name,"	",type(Scenario.node_list[n]).__name__,"	IP:",Scenario.node_list[n].ip)
		elif inp == 'run' or inp == 'run_all' or inp == 'run all':
			Scenario.write_bash()
			subprocess.call('./runtime_bash.sh')
			global stop_threads
			stop_threads = False
			x = threading.Thread(target=run,args=(Scenario,True, False,))
			x.start()
			input("press enter to shutdown\n")
			stop_threads = True
			x.join()
			Scenario.reset()
		elif inp == 'write_bash':
			Scenario.write_bash()
		elif inp == 'ssh' or inp == 'ssh_connection':
			while True:
				ans = input('Which VM do you want to connect to?').strip()
				if ans.lower() == 'all':
					for n in range(0,Scenario.nNodes):
						Scenario.node_list[n].ssh_connection()
					break
				else:
					Exist = False
					for n in range(0,Scenario.nNodes):
						if ans == Scenario.node_list[n].name:
							Scenario.node_list[n].ssh_connection()
							Exist = True
							break
					if Exist:
						break
		elif inp == "exit":
			while True:
				ans = input("Do you want delete all the VMs relete with the scenario?(Y/N):").strip().lower()
				if ans == 'y' or ans == 'yes':
					Scenario.delete_VMs()
					break
				elif ans == 'n' or ans == 'no':
					break
				else:
					print('ERROR: Invalid answer')
			break
		else:
			print (inp," is not one of the available actions")

if __name__ == "__main__":
	main()
