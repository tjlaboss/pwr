# Neutron Pad
#
# Class and functions for a PWR neutron pad

import math


# Simple functions for the necessary angles
def phi(th, radians = True):
	"""Angle on the XY plane at which the normal vector to a plane will be
	
	Inputs:
		:param th:          float; angle (degrees) of the plane itself on the XY plane
		:param radians:     Boolean; whether to return the answer in radians. If false,
							the answer will be returned in degrees.
							[Default: True]
	Output:
		:return angle:      float; angle (in radians, or degrees if radians == False)
	"""
	angle = th * math.pi/180 - math.pi/2
	if radians:
		return angle
	else:
		return angle * 180 / math.pi


def B(th):
	"""Coefficient 'A' for a plane equation

		Inputs:
			:param th:          float; angle (degrees) of the plane itself on the XY plane
		Output:
			:return A:          float
		"""
	return math.sin(phi(th))
	
	
def B(th):
	"""Coefficient 'B' for a plane equation

		Inputs:
			:param th:          float; angle (degrees) of the plane itself on the XY plane
		Output:
			:return B:          float
		"""
	B = math.cos(phi(th))
	return B


class Pad(object):
	"""Neutron pad as found in the reactor vessel of a PWR.
	
	Inputs:
		:param s_out:       instance of openmc.ZCylinder marking the outer radius
		:param s_in:        instance of openmc.ZCylinder marking the inner radius
		:param s_bot:       instance of openmc.ZPlane marking the bottom of the vessel
		:param s_top:       instance of openmc.ZPlane marking the top of the vessel
		:param pad_mat:     instance of openmc.Material that the neutron pad is made of
		:param mod_mat:     instance of openmc.Material that the space between the
							neutron pads is filled with (usually moderator)
		:param npads:       int; number of pads: one per steam generator (evenly placed)
							[Default: 4]
		:param arc_length:  float (degrees); arc length of a single neutron pad
		                    [Default: 32]
		:param angle:       float (degrees); angle from the x-axis at which the first pad starts
							[Default: 45]
		:param counter:     instance of pwr.Counter for surface and cell numbers.
							[optional--if not supplied, auto surface/cell id's will be assigned]
	
	Other parameters:
		:param material:    pad_mat; instance of openmc.Material
		:param mod:         mod_mat; instance of openmc.Material
		:param cells:       list of instances of openmc.Cell making up the neutron pad
							layer of the reactor vessel.
							[Empty until Pad.generate_cells() is executed.]
		:param planes:      list of instances of openmc.Plane created during the generation
		                    of the neutron pad
		                    [Empty until Pad.generate_cells() is executed.]
        :param generated:   Boolean; whether or not generate_cells() has been executed yet.
	"""
	def __init__(self, s_out, s_in, s_bot, s_top, pad_mat, mod_mat,
                       npads = 4, arc_length = 32, angle = 45, counter = None):
		self.s_out = s_out
		self.s_in = s_in
		self.s_bot = s_bot
		self.s_top = s_top
		self.material = pad_mat
		self.mod = mod_mat
		self.npads = npads
		self.arc_length = 32
		self.angle = 45
		
		self.cells = []
		self.planes = []
		self.counter = counter
		self.generated = False
	
	def __str__(self):
		rep = "Neutron pads:"
		rep += "\n\t" + str(self.npads) + " pads"
		rep += "\n\tArc length: " + str(self.arc_length) + " degrees"
		rep += "\n\tStarting angle: " + str(self.angle) + " degrees"
		return rep
	
