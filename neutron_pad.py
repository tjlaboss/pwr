# Neutron Pad
#
# Class and functions for a PWR neutron pad

import openmc
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


class Neutron_Pads(object):
	"""Neutron pads as found in the reactor vessel of a PWR.
	
	Inputs:
		:param region:      instance of openmc.Intersection defining the region in which the
							neutron pads will exist. This should be an intersection of two
							ZCylinders (inner and outer radius). If 3D, the region should also
							intersect with two ZPlanes (bottom and top).
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
							[Empty until Neutron_Pads.generate_cells() is executed.]
		:param planes:      list of instances of openmc.Plane created during the generation
		                    of the neutron pad
		                    [Empty until Neutron_Pads.generate_cells() is executed.]
        :param generated:   Boolean; whether or not generate_cells() has been executed yet.
	"""
	def __init__(self, region, pad_mat, mod_mat,
                npads = 4, arc_length = 32, angle = 45, counter = None):
		assert arc_length * npads <= 360, "The combined arclength must be less than 360 degrees."
		self.region = region
		self.material = pad_mat
		self.mod = mod_mat
		self.npads = npads
		self.arc_length = arc_length
		self.angle = angle
		self.counter = counter
		
		self.cells = []
		self.planes = []
		self.generated = False
	
	def __str__(self):
		rep = "Neutron pads:"
		rep += "\n\t" + str(self.npads) + " pads"
		rep += "\n\tArc length: " + str(self.arc_length) + " degrees"
		rep += "\n\tStarting angle: " + str(self.angle) + " degrees"
		if self.generated:
			rep += "\n\tThese neutron pads have been generated."
		else:
			rep += "\n\tThe neutron pads have NOT been generated."
		return rep
	
	def get_cells(self):
		"""Get the cells and planes necessary for modeling these neutron pads in openmc.
		If the required cells and surfaces exist, return them. If not, instantiate them.
		
		Output:
			:return cells:    list of the cells generated
		"""
		if not self.generated:
			# Write this function
			self.generated = True
		
		return self.cells

