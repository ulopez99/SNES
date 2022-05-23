#!/usr/bin/env python3
from Class.Functions import *
from skyfield.api import EarthSatellite, load, wgs84
from datetime import datetime,timedelta,timezone
class Orbit:
	#Varibles
	# 	Keplerian elements: ToA a i0 e Omega w M0 n ToAyear

	#Functions
	#	__init__
	#	ECEF
	#	LLA
	#	ECI
	
	def __init__(self,sat):
		# Creates a Orbit class object from a TLE
		self.TLE = sat
	def time_vector(self,TotalTime,TimeInterval,date_time,UTC = 0):
		if date_time == None:
			date_time = datetime.now(timezone(timedelta(hours=UTC)))
		n_intervals = round(TotalTime*60/TimeInterval)
		intervall = timedelta(minutes = TimeInterval)
		timelist = []
		for i in range(n_intervals):
			timelist.append(date_time + i*intervall)
		return timelist
	def ECEF(self,TotalTime = 1,TimeInterval = 60,esec = None,date_time = None):
		# Return a list of arrays in cartesian coordinates with the current position or in a time diference in seconds with respect to the ToA (Time of Aplicability)
		'''ECEF = []
		if esec == None:
			esec = compute_esec(self.ToA,self.ToAyear,date_time)
		n_intervals = round(TotalTime*60/TimeInterval)
		for i in range(0,n_intervals):
			ECEF.append(Kepler2ECEF(self.a,self.i0,self.e,self.Omega, 0,self.w, self.M0, self.n, esec))
			esec = esec + TimeInterval*60
		return ECEF
		'''
		ECEF = []
		timelist = self.time_vector(TotalTime,TimeInterval,date_time)
		for t in timelist:
			ts = load.timescale().from_datetime(t)
			geocentric = self.TLE.at(ts)
			position = wgs84.geographic_position_of(geocentric)
			ECEF.append(position.itrs_xyz.m)
		return ECEF
	def LLA(self,TotalTime = 1,TimeInterval = 60,esec = None,date_time = None):
		# Return a list of arrays in geographic coordinate system with the current position or in a time diference in seconds with respect to the ToA (Time of Aplicability)
		'''if esec == None:
			esec = compute_esec(self.ToA,self.ToAyear,date_time)
		print (esec/(24*3600))
		n_intervals = round(TotalTime*60/TimeInterval)
		LLA = []
		for i in range(0,n_intervals):
			ECEF = Kepler2ECEF(self.a,self.i0,self.e,self.Omega, 0,self.w, self.M0, self.n, esec)
			LLA.append(ECEF2LLA(ECEF))
			esec = esec + TimeInterval*60
		return LLA
		'''
		LLA = []
		timelist = self.time_vector(TotalTime,TimeInterval,date_time)
		for t in timelist:
			ts = load.timescale().from_datetime(t)
			geocentric = self.TLE.at(ts)
			position = wgs84.geographic_position_of(geocentric)
			LLA.append([position.latitude.degrees,position.longitude.degrees,position.elevation.m])
		return LLA
	def ECI(self,TotalTime = 1,TimeInterval = 60,esec = None,date_time = None):
		# Return a list of arrays in geographic coordinate system with the current position or in a time diference in seconds with respect to the ToA (Time of Aplicability)
		'''if esec == None:
			esec = compute_esec(self.ToA,self.ToAyear,date_time)
		n_intervals = round(TotalTime*60/TimeInterval)
		ECI = []
		for i in range(0,n_intervals):
			ECEF = Kepler2ECEF(self.a,self.i0,self.e,self.Omega, 0,self.w, self.M0, self.n, esec)
			Day = esec2days(self.ToA,esec)
			GAST = gast(Day,self.ToAyear)
			ECI.append(ECEF2ECI(ECEF,GAST))
			esec = esec + TimeInterval*60
		return ECI'''
		ECI = []
		timelist = self.time_vector(TotalTime,TimeInterval,date_time)
		for t in timelist:
			ts = load.timescale().from_datetime(t)
			geocentric = self.TLE.at(ts)
			ECI.append(geocentric.position.m)
		return ECI
	def getAll(self,date_time = None):
		ts = load.timescale().from_datetime(date_time)
		geocentric = self.TLE.at(ts)
		ECI = geocentric.position.m
		position = wgs84.geographic_position_of(geocentric)
		LLA = [position.latitude.degrees,position.longitude.degrees,position.elevation.m]
		ECEF = position.itrs_xyz.m
		
		return ECEF,LLA,ECI
