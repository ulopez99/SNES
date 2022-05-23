from Class.Scenario import scenario
from datetime import datetime,timedelta

import threading
import time
import subprocess
import toml
stop_threads = False
def insertNodes(Scenario):
	while True:
		try:
			configuration_file = input("Insert the name of the configuration file: ")
			#Open file
			fo = open(configuration_file, "r")
			break
		except FileNotFoundError:
			print ("The file doesn't exist or is not found in the current folder.")
	line0 = fo.readline()
	if line0 != '' and line0 != None and line0 != '\n':
		vline0 = line0.split()
		if vline0[0] != "SAT" and vline0[0] != "GS":
			vline0 = line0.split(';')
			for n in range(0,len(vline0)):
				configuration_parameter = vline0[n].split('=')
				if configuration_parameter[0].strip() == 'TotalTime':
					Scenario.set_TotalTime(configuration_parameter[1].strip())
				elif configuration_parameter[0].strip() == 'TimeInterval':
					Scenario.set_TimeInterval(configuration_parameter[1].strip())
				elif configuration_parameter[0].strip() == 'date_time':
					Scenario.set_date_time(configuration_parameter[1].strip())
				elif configuration_parameter[0].strip() == 'speed':
					Scenario.set_speed(configuration_parameter[1].strip())
			line0 = fo.readline()
		line1 = fo.readline()
		line2 = fo.readline()
		#Read all the line of the file and creates the scenario
		while (line0 != "" and line1 != "" and line2 != ""):
			Scenario.AddNode(line0,line1,line2)
			line0 = fo.readline()
			line1 = fo.readline()
			line2 = fo.readline()
	else:
		print ('ERROR:Error in the format of the file, the first line can not be empty')
	# Close opened file
	fo.close()
def run(Scenario,EMU,CESIUM):
	global stop_threads
	time.sleep(1)
	SAT1 = Scenario.node_list[0].name
	SAT2 = Scenario.node_list[1].name
	i2CAT = Scenario.node_list[2].name
	print (Scenario.time_parameters.get_date_time())
	print ('-Delay',SAT1,'->',SAT2,': ',Scenario.channel.get_channel(0,1))
	print ('-Delay',SAT1,'->',i2CAT,': ',Scenario.channel.get_channel(0,2))
	print ('-Delay',SAT2,'->',i2CAT,': ',Scenario.channel.get_channel(1,2))
	time.sleep(60*Scenario.time_parameters.get_TimeInterval()/Scenario.get_speed())
	while True:
		if stop_threads:
			break
		if Scenario.step(EMU,CESIUM):
			print('The emulation is over: press enter to shutdown')
			break
		print (Scenario.time_parameters.get_date_time())
		print ('-Delay',SAT1,'->',SAT2,': ',Scenario.channel.get_channel(0,1))
		print ('-Delay',SAT1,'->',i2CAT,': ',Scenario.channel.get_channel(0,2))
		print ('-Delay',SAT2,'->',i2CAT,': ',Scenario.channel.get_channel(1,2))
		#print (Scenario.channel_matrix)
		time.sleep(60*Scenario.time_parameters.get_TimeInterval()/Scenario.get_speed())
	subprocess.call('./shutdown_bash.sh')
def main():
	print ("Hi, you have started the satellite network emulator.")
	#Open file
	fo = open('config.toml', "r")
	TOML = toml.load(fo, _dict=dict)
	Scenario = scenario(TOML)
	while True:
		inp = input("Insert the action you wish to perform (insert 'help' to see all available actions): ")
		if inp == "help":
			print ("- help: shows all available actions\n- scenario: show the load nodes and his type\n- change_scenario: deletes the current configuration and loads a new one\n- add_new_nodes: adds new nodes to the current scenario\n- change_date_time: changes the instant on which the emulation is performed\n- change_speed: changes the execution speed of the emulator\n- change_duration: changes the duration of the emulate scenario\n- change_intervals: changes the elapsed time at each step\n- run_all: run the emulation and Cesium\n- run_emulator: run only the emulation\n- run_CESIUM: run only the visulization at Cesium\n- exit: program execution ends")
		elif inp == "scenario":
			print("The scenario is formed by ",Scenario.nNodes," Nodes")
			if Scenario.time_parameters.get_date_time() == None:
				print ('The emulator is working at current time')
			else:
				print ('Initialize:',Scenario.time_parameters.get_initial_date_time(),'	Ends:',Scenario.time_parameters.get_initial_date_time() + timedelta(hours=Scenario.time_parameters.get_TotalTime()))
			for n in range(0,Scenario.nNodes):
				print ('Node',n+1,": ",Scenario.node_list[n].name,"	",type(Scenario.node_list[n]).__name__,"	IP:",Scenario.node_list[n].ip)
		elif inp == "change_scenario" or inp == "change scenario":
			Scenario.delate()
			insertNodes(scenario)
		elif inp == "add_new_nodes" or inp == "add new nodes":
			insertNodes(scenario)
		elif inp == "change_date_time" or inp == "change date time":
			if Scenario.time_parameters.get_date_time() == None:
				print ('The emulator is working at current time')
			else:
				print ('The emulator start in the datetime:',Scenario.time_parameters.get_date_time())
			while True:
				YoN = input('Do you want to work at current time? (Y/N) ')
				if YoN == 'Y' or YoN == 'y' or YoN == 'yes' or YoN == 'Yes' or YoN == 'yes':
					Scenario.set_date_time(None)
					break
				elif YoN == 'N' or YoN == 'n' or YoN == 'no' or YoN == 'No' or YoN == 'NO':
					Bool_date_time = False
					while not(Bool_date_time):
						date_time = input('Introduce the new data time (correct format yyyy-mm-dd hh:mm:ss): ')
						Bool_date_time = Scenario.set_date_time(date_time)
					break
				else:
					print ('Invalid answer ')
		elif inp == 'change_speed' or inp == 'change speed':
			Bool_speed = False
			while not(Bool_speed):
				speed = input('Introduce the new executio speed of emulation: x')
				Bool_speed = Scenario.set_speed(speed)
		elif inp == 'change_duration' or inp == 'change duration':
			Bool_duration = False
			while not(Bool_duration):
				TotalTime = input('Introduce the new duration (in hours) of the emulation: ')
				Bool_duration = Scenario.set_TotalTime(TotalTime)
		elif inp == 'change_intervals' or inp == 'change intervals':
			Bool_interval = False
			while not(Bool_interval):
				TimeInterval = input('Introduce the new duration (in minutes) of the every step: ')
				Bool_interval = Scenario.set_TimeInterval(TimeInterval)
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
		elif inp == "exit":
			
			while True:
				ans = input("Do you want delete all the VMs relete with the scenario?(Y/N):")
				if ans == 'Y' or ans == 'y' or ans == 'Yes' or ans == 'YES' or ans == 'yes':
					Scenario.delete_VMs()
					break
				elif ans == 'N' or ans == 'n' or ans == 'No' or ans == 'NO' or ans == 'no':
					break
				else:
					print('ERROR: Invalid answer')
			break
		else:
			print (inp," is not one of the available actions")

if __name__ == "__main__":
	main()
