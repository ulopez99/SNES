#!/usr/bin/env python3
from Class.Functions import *
class time_parameters:
	
	TotalTime = 24			#[h]
	TimeInterval = 1		#[min]
	min_speed = 1
	date_time = None
	initial_date_time = None
	
	def __init__(self,TOMLTime):
		TotalTime = TOMLTime['TotalTime']
		TimeInterval = TOMLTime['TimeInterval']
		speed = TOMLTime['MinSpeed']
		date_time = TOMLTime['datetime']
		UTC = int(TOMLTime['UTC'])
		if float(TotalTime) > 0:
			self.TotalTime = float(TotalTime)
		else:
			print ('ERROR: invalid parameter, TotalTime cannot be negative or equal to 0')
			self.TotalTime = 24
		if float(TimeInterval) > 0: 
			self.TimeInterval = float(TimeInterval)
		else:
			print ('ERROR: invalid parameter, TimeInterval cannot be negative or equal to 0')
			self.TimeInterval = 1
		if float(speed) > 0:
			self.min_speed = float(speed)
		else: 
			print ('ERROR: invalid parameter, speed cannot be negative or equal to 0')
			self.speed = 1
		if UTC <= 24 and UTC >= -24:
			self.UTC = UTC
		else:
			print ('ERROR: invalid parameter, UTC cannot be greater than 24 or less than -24')
			self.UTC = 0
		if date_time == None:
			self.date_time = date_time
		else:
			if self.UTC >= 10:
				date_time = '%s+%d:00'%(date_time,self.UTC)
			elif  self.UTC >= 0:
				date_time = '%s+0%d:00'%(date_time,self.UTC)
			elif self.UTC > -10:
				date_time = '%s-0%d:00'%(date_time,self.UTC)
			else:
				date_time = '%s-%d:00'%(date_time,self.UTC)
			self.date_time = datetime.fromisoformat(date_time)
		self.initial_date_time = self.date_time
	'''def __init__(self,TotalTime = 24,TimeInterval = 1,date_time: str = None, speed = 1):
		if float(TotalTime) > 0:
			self.TotalTime = float(TotalTime)
		else:
			print ('ERROR: invalid parameter, TotalTime cannot be negative or equal to 0')
			self.TotalTime = 24
		if float(TimeInterval) > 0: 
			self.TimeInterval = float(TimeInterval)
		else:
			print ('ERROR: invalid parameter, TimeInterval cannot be negative or equal to 0')
			self.TimeInterval = 1
		if float(speed) > 0:
			self.min_speed = float(speed)
		else: 
			print ('ERROR: invalid parameter, speed cannot be negative or equal to 0')
			self.speed = 1
		if date_time == None:
			self.date_time = date_time
		else:
			self.date_time = datetime.fromisoformat(date_time)
		self.initial_date_time = self.date_time'''
	def get_speed (self,channel = True):
		if channel:
			return self.min_speed
		else:
			return 60
	def get_initial_date_time(self):
		return self.initial_date_time
	def get_date_time(self):
		return self.date_time
	def get_TimeInterval(self):
		return self.TimeInterval
	def get_TotalTime(self):
		return self.TotalTime
	def set_TotalTime(self,TotalTime):
		# change the parameter TotalTime
		try:
			if float(TotalTime) > 0:
				self.TotalTime = float(TotalTime)
				return True
			else:
				print ('ERROR: invalid parameter, TotalTime cannot be negative or equal to 0')
				return False
		except ValueError:
			print ('ERROR: Invalid format, the modification of TotalTime parameter has not been carried out.')
			return False
	def set_TimeInterval(self,TimeInterval):
		# change the parameter TimeInterval
		try:
			if float(TimeInterval) > 0:
				self.TimeInterval = float(TimeInterval)
				return True
			else:
				print ('ERROR: invalid parameter, TimeInterval cannot be negative or equal to 0')
				return False
				
		except ValueError:
			print ('ERROR: Invalid format, the modification of TimeInterval parameter has not been carried out.')
			return False		
	def set_date_time(self,date_time):
		# change the parameter date_time and initial_date_time
		
		if date_time == None:
			self.date_time = date_time
			
		else:
			try:
				self.date_time = datetime.fromisoformat(date_time)
				self.initial_date_time = self.date_time
				return True
			except ValueError:
				print ('ERROR: Invalid format, the modification of date_time parameter has not been carried out.')
				return False
	def set_speed(self,speed):
		# change the parameter speed
		try:
			if float(speed) > 0:
				self.min_speed = float(speed)
				return True
			else:
				print ('ERROR: invalid parameter, speed cannot be negative or equal to 0')
				return False
		except ValueError:
			print ('ERROR: Invalid format, the modification of speed parameter has not been carried out.')
			return False
	def reset(self):
		# restart the parameters of simulatión, put date_time equal to initial_date_time and update de scenario
		self.date_time = self.initial_date_time
	def step(self):
		# change date_time and update the scenario
		if self.date_time != None:
			self.date_time += timedelta(minutes=self.TimeInterval)
			if self.date_time > self.initial_date_time+timedelta(hours=self.TotalTime):
				return True
			else:
				return False
		else:
			return False
			
