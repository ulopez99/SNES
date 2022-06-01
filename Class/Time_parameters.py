#!/usr/bin/env python3
from skyfield.api import load
from datetime import datetime,timedelta
ts = load.timescale()

class time_parameters:
	

	TimeInterval = 1		#[min]
	min_speed = 1
	date_time = None
	initial_date_time = None
	
	def __init__(self,TOMLTime):
		TimeInterval = TOMLTime['TimeInterval']
		Min_speed = TOMLTime['MinSpeed']
		Max_speed = TOMLTime['MaxSpeed']
		start_date_time = TOMLTime['start_datetime']
		end_date_time = TOMLTime['end_datetime']
		if float(TimeInterval) > 0: 
			self.TimeInterval = float(TimeInterval)
		else:
			print ('ERROR: invalid parameter, TimeInterval cannot be negative or equal to 0')
			self.TimeInterval = 1
		if float(Min_speed) > 0:
			self.min_speed = float(Min_speed)
		else: 
			print ('ERROR: invalid parameter, speed cannot be negative or equal to 0')
			self.min_speed = 1
		if float(Max_speed) > 0:
			self.max_speed = float(Max_speed)
		else: 
			print ('ERROR: invalid parameter, speed cannot be negative or equal to 0')
			self.max_speed = 1
		if start_date_time == None:
			self.date_time = start_date_time
			date_time = datetime.now(timezone(timedelta(0)))
			self.t_skyfield = ts.from_datetime(date_time)
		else:
			date_time = start_date_time+'+00:00'
			self.date_time = datetime.fromisoformat(date_time)
			self.t_skyfield = ts.from_datetime(self.date_time)
		self.initial_date_time = self.date_time
		str_date_time = end_date_time+'+00:00'
		date_time = datetime.fromisoformat(str_date_time)
		if date_time >= self.initial_date_time:
			 self.end_date_time = date_time
		else:
			self.end_date_time = self.initial_date_time
			self.initial_date_time = date_time
	def get_speed (self,channel = True):
		if channel:
			return self.min_speed
		else:
			return self.max_speed
	def get_initial_date_time(self):
		return self.initial_date_time
	def get_date_time(self):
		return self.date_time
	def get_TimeInterval(self):
		return self.TimeInterval
	def get_t_skyfield(self):
		return self.t_skyfield
	
	def reset(self):
		# restart the parameters of simulatión, put date_time equal to initial_date_time and update de scenario
		self.date_time = self.initial_date_time
		self.t_skyfield = ts.from_datetime(self.date_time)
	def step(self):
		# change date_time and update the scenario
		if self.date_time != None:
			self.date_time += timedelta(minutes=self.TimeInterval)
			self.t_skyfield = ts.from_datetime(self.date_time)
			if self.date_time > self.end_date_time:
				return True
			else:
				return False
		else:
			date_time = datetime.now(timezone(timedelta(hours=0)))
			self.t_skyfield = ts.from_datetime(date_time)
			return False
