#!/usr/bin/env python3
from datetime import datetime,timedelta
import julian
import math
import numpy as np

#GLOBAL CONSTANTS
G = 6.67384e-11;            			# Gravitational constant [m3 kg-1 s-2]
M = 5.972e+24;              			# Earth mass [kg]
dOmegaEarth = 7.2921151467e-5			# Angular speed of Earth rotation [rad/s]
a_Earth = 6378137 				# Earth major semi axis [m]
e_2 = 0.00669437999014				# Square Earth eccentricity
c = 3e8					# Speed of light [m/s]
b = math.sqrt(a_Earth**2-(e_2*a_Earth**2))	# Earth menor semi axis [m]
MJ2022 = 59580.0 				# MJD on 1/1/2022 at 00:00 UTC (see http://leapsecond.com/java/cal.htm)


#Returns the parameters of interest of the TLE
def Read_TLE(L1 , L2):
		
	vL1 = L1.split()
	# Time of Applicability [days]
	ToAyear = int(vL1[3][:2])
	ToA = float(vL1[3][2:])
	vL2 = L2.split()
	
	# Orbit inclination [degrees]
	i0 = float(vL2[2])
	# Right ascension of the ascending node at ToA [degrees]
	Omega0 = float(vL2[3])
	# Orbit eccentricity times 10^7
	e = float(vL2[4])
	# Argument of the perigee at ToA [degrees]
	w = float(vL2[5])
	# Mean Anomaly at ToA [degrees]
	M0 = float(vL2[6])
	# Mean motion (satellite angular speed of rotation) in [Revolutions/day]
	n = float(vL2[7])
	return ToA,i0,Omega0,e,w,M0,n,ToAyear

#
def time2toa(ToA,date_time = None):
	# Computes elapsed time from ToA [days] and GAST [deg] at ToA
	# ToA must be given in days of current year
	
	if date_time == None:	#Find Julian Date now
		date_time = datetime.now()
	JD = julian.to_jd(date_time, fmt='jd')	# Julian Date in UTC
	# Compute current time in secs. from ToA
	
	MJ2022 = 59580.0; # MJD on 1/1/2022 at 00:00 UTC (see http://leapsecond.com/java/cal.htm)
	J2022 = MJ2022 + 2400000.5; 		# JD on 1/1/2022 at 00:00 UTC
	
	JToA = J2022 + ToA - 1; 		# ToA in JD
	esec = 86400 * (JD - JToA);  		# time elapsed since the ToA in secs.
	
	#Greenwich Mean Sidereal Time (GMST) is the hour angle of the average position of the vernal equinox,
	# neglecting short term motions of the equinox due to nutation. GAST is GMST corrected for
	# the shift in the position of the vernal equinox due to nutation.
	# GAST at a given epoch is the RA of the Greenwich meridian at that epoch (usually in time units).
	
	#Find GAST in degrees at ToA
	J2000 = 2451545.0					# epoch is 1/1/2000 at 12:00 UTC
	midnight = round(JToA) - 0.5				# midnight of JToA
	days_since_midnight = JToA - midnight;
	hours_since_midnight = days_since_midnight * 24;
	days_since_epoch = JToA - J2000;
	centuries_since_epoch = days_since_epoch / 36525;
	whole_days_since_epoch = midnight - J2000;
	GAST = 6.697374558 + 0.06570982441908 * whole_days_since_epoch + 1.00273790935 * hours_since_midnight + 0.000026 * centuries_since_epoch**2;  # GAST in hours from ?
	GASTh = GAST - 24 * math.floor(GAST/24) 	# GAST in hours at ToA
	GASTdeg = 15 * 1.0027855 * GASTh	# GAST in degrees at ToA (approx. 361º/24h)
	
	return esec,GASTdeg
	
#Return the GAST (Greenwich Apparent Sidereal Time) in radians
def gast (ToA,ToAyear):
	JYear = julian.to_jd(datetime.fromisoformat('20%d-01-01'%(ToAyear)), fmt='jd')	# JD on 1/1/year at 00:00 UTC
	JToA = JYear + ToA - 1							# ToA in JD
	JYear = julian.to_jd(datetime.fromisoformat('2022-01-01'), fmt='jd')
	
	# Greenwich Mean Sidereal Time (GMST) is the hour angle of the average position of the vernal equinox,
	# neglecting short term motions of the equinox due to nutation. GAST is GMST corrected for
	# the shift in the position of the vernal equinox due to nutation.
	# GAST at a given epoch is the RA of the Greenwich meridian at that epoch (usually in time units).
	
	#Find GAST in degrees at ToA
	J2000 = 2451545.0					# epoch is 1/1/2000 at 12:00 UTC
	midnight = round(JToA) - 0.5				# midnight of JToA
	days_since_midnight = JToA - midnight
	hours_since_midnight = days_since_midnight * 24
	days_since_epoch = JToA - J2000
	centuries_since_epoch = days_since_epoch / 36525
	whole_days_since_epoch = midnight - J2000
	GAST = 6.697374558 + 0.06570982441908 * whole_days_since_epoch + 1.00273790935 * hours_since_midnight + 0.000026 * centuries_since_epoch**2  # GAST in hours from ?
	GASTh = GAST - 24 * math.floor(GAST/24) 		# GAST in hours at ToA
	GASTdeg = 15 * 1.0027855 * GASTh			# GAST in degrees at ToA (approx. 361º/24h)
	GAST=GASTdeg*math.pi/180				# GAST in radians
	return GAST

#
def esec2days (ToA,esec):
	Day = ToA + esec/86400
	return Day
	
#Return the diference of time between the ToA and the current instant
def compute_esec (ToA,ToAyear,date_time = None,):
	# Computes elapsed time from ToA [s] and GAST [deg] at ToA
	# ToA must be given in days of current year
	
	if date_time == None:	#Find Julian Date now
		dt = datetime.now()
		
	else:
		dt = date_time
		
	JD = julian.to_jd(dt, fmt='jd')	# Julian Date now in UTC
	# Compute current time in secs. from ToA
	JYear = julian.to_jd(datetime.fromisoformat('20%d-01-01'%(ToAyear)), fmt='jd')	# JD on 1/1/year at 00:00 UTC
	JToA = JYear + ToA - 1							# ToA in JD
	esec = 86400 * (JD - JToA)  		# time elapsed since the ToA in secs.
	return esec

# Return the Keplerian parameters in a format that can be operated on from the data extracted from the TLE.
def Keplerian_parameters(i0,Omega0,e,w,M0,n,GAST):	#Normalizes the Keplerian parameters for later use.
	i0=i0*math.pi/180; 				# Orbit inclination [rad]
	Omega0=Omega0*math.pi/180			# Right ascention [rad]
	e = e / (10**7)				# Orbit eccentricity
	w=w*math.pi/180;				# Argument of the perigee at ToA [rad]
	M0=M0*math.pi/180 				# Mean Anomaly at ToA [rad]
	n=n*2*math.pi/(24*3600)			# Mean motion [rad/s]
	
	a=(G*M/(n**2))**(1/3)  		# Orbit major semi axis [m]
	Omega=Omega0-GAST			# Longitude of the ascending node at the ToA
	d_Omega=0				# Rate of change of the right ascension [rad/s]
	return a,i0,e,Omega, d_Omega,w, M0, n

#Return the ECEF position of a satellite 
def Kepler2ECEF(a,i0,e,Omega, d_Omega,w, M0, n, dt):
	Mk = M0 + n * dt		# Mean anomaly computation
	Ek = []
	i = 1
	Ek.append(Mk)
	Ek.append(Mk + e * math.sin(Ek[i-1]))
	#Eccentric anomaly computation
	while abs(Ek[i]-Ek[i-1]) >= (1e-8):
		i += 1
		Ek.append(Mk + e * math.sin(Ek[i-1]))
	Sin_v = (math.sqrt(1-e**2)*math.sin(Ek[i]))/(1-e*math.cos(Ek[i]))	
	Cos_v = (math.cos(Ek[i])-e)/(1-e*math.cos(Ek[i]))
	v = math.atan2(Sin_v,Cos_v)	# True Anomaly
	u = v +w 			# Argument of latitude
	r_k = a*(1-e*math.cos(Ek[i]))	# Orbit radius (current distance to Earth center)
	Omegak = Omega+d_Omega * dt-dOmegaEarth*dt	# Current longitude of the ascending node
	x_p = r_k*math.cos(u)		# x coordinate within the orbital plane
	y_p = r_k*math.sin(u)		# y coordinate within the orbital plane
	
	x = x_p * math.cos(Omegak)-y_p*math.cos(i0)*math.sin(Omegak)	# ECEF x-coordinate [m]
	y = x_p * math.sin(Omegak)+y_p*math.cos(i0)*math.cos(Omegak)	# ECEF y-coordinate [m]
	z = y_p*math.sin(i0)						# ECEF z-coordinate [m]
	
	ECEF = []
	ECEF = np.array([x,y,z])
	return ECEF

#Return the position in ECI from the position in ECEF
def ECEF2ECI(ECEF,GAST):

	#		(cos(GAST)	sin(GAST)	0)
	# 	P_ECI=	(-sin(GAST)	cos(GAST)	0) P_ECEF
	#		(0		0		1)
	x_ECEF = ECEF[0]
	y_ECEF = ECEF[1]
	
	x = math.cos(GAST) * x_ECEF + math.sin(GAST) * y_ECEF
	y = -math.sin(GAST)* x_ECEF + math.cos(GAST) * y_ECEF
	z = ECEF[2]
	ECI = np.array([x,y,z])
	return ECI
	
#Return the position in LLA from the position in ECEF
def ECEF2LLA(ECEF):
	
	x = ECEF[0]
	y = ECEF[1]
	z = ECEF[2]
	
	r = math.sqrt(x**2 + y**2)
	E_2 = a_Earth**2 - b**2
	F = 54 * b**2 *z**2
	G = r**2 + (1-e_2)*z**2 - e_2*E_2
	C = (e_2**2 * F * r**2)/G**3
	s = (1+C+math.sqrt(C**2+2*C))**(1/3)
	P = F/(3*(s+1/s+1)**2*G**2)
	Q = math.sqrt(1+2*e_2**2*P)
	r0 = -(P * e_2 * r)/(1+Q)+math.sqrt(1/2 * a_Earth**2 * (1+1/Q) - (P * (1-e_2) * z**2)/(Q*(1+Q))-1/2 * P * r**2)
	U = math.sqrt(z**2+(r-r0*e_2)**2)
	V = math.sqrt(z**2*(1-e_2)+(r-r0*e_2)**2)
	z0 = b**2*z/(a_Earth*V)
	
	h = U*(1 - b**2/(a_Earth*V))				# Height [m]
	lat = math.atan2 ((z + (e_2*(a_Earth/b)**2 * z0)),r)	# Latitude [rad]
	long = math.atan2(y,x)					# Longitude [rad]
	
	LLA = np.array([lat*180/math.pi,long*180/math.pi,h])
	return LLA
	
#Return the position in ECEF from the position in LLA	
def LLA2ECEF(LLA):
	lat = LLA[0] * math.pi/180
	long = LLA[1] * math.pi/180
	h = LLA[2]
	
	x = (a_Earth/math.sqrt(1-e_2*math.sin(lat)**2)+h)*math.cos(lat)*math.cos(long)	# ECEF x-coordinate [m]
	y = (a_Earth/math.sqrt(1-e_2*math.sin(lat)**2)+h)*math.cos(lat)*math.sin(long)	# ECEF y-coordinate [m]
	z = ((a_Earth*(1-e_2))/math.sqrt(1-e_2*math.sin(lat)**2)+h)*math.sin(lat)		# ECEF z-coordinate [m]
	
	ECEF = np.array([x,y,z])
	return ECEF

#Return a array in NED (Nord,East,Down) relative of GS from a vector in ECEF
def ECEF2NED(pseudoDistance,LLA):
	x = pseudoDistance[0]
	y = pseudoDistance[1]
	z = pseudoDistance[2]
	lat = LLA[0] * math.pi/180
	long = LLA[1] * math.pi/180
	N = -math.sin(lat)*math.cos(long)*x - math.sin(lat)*math.sin(long)*y + math.cos(lat) * z
	E = -math.sin(long)*x + math.cos(long)*y
	D = -math.cos(lat)*math.cos(long)*x - math.cos(lat)*math.sin(long)*y - math.sin(lat)*z
	NED = np.array([N,E,D])
	return NED

#Compute azimuth and elevation angles and the distantce from NED Cartesian coordinates
def NED2AzimuthElevationDistance(NED):
	# Computation of the pointing angles and the distance to each of the satellites
	
	d=math.sqrt(NED[0]**2+NED[1]**2+NED[2]**2)	#Distance
	alpha=math.atan(NED[1]/NED[0])*180/math.pi	#Azimuth
	beta=math.asin(-NED[2]/d)*180/math.pi		#Elevation
	return alpha,beta,d
#Compute the delay between a GS and SAT if the elevation angle and distance if the angle of elevation is positive or greater than a parameter and the distance is less than a maximum
def GroundBase2Satellite(ECEF_SAT,ECEF_GB,LLA_GB,Min,threshold):
	p = ECEF_SAT-ECEF_GB
	NED = ECEF2NED(p,LLA_GB)
	alpha,beta,d = NED2AzimuthElevationDistance(NED)
	if (beta >= Min) and d < threshold:
		LoS = True
		delay = d/c*1e3
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
	b = a_Earth
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
def LineOfSight(ECEF1,ECEF2,threshold):
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
	
def Exist_Node(node_list,node,nNodes):
	exist = False
	n = 0 
	while not(exist) and n < nNodes:
		if type(node).__name__ == "Satellite" and type(node_list[n]).__name__ == "Satellite":
			if node_list[n].ID == node.ID or node_list[n].name == node.name:
				return True
		elif type(node).__name__ == "GroundStation" and type(node_list[n]).__name__ == "GroundStation":
			if node_list[n].name == node.name:
				return True
		n +=1
	return False
