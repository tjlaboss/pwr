# Functions
#
# Container for useful functions for the pwr module

from pwr.settings import SURFACE, CELL, MATERIAL, UNIVERSE
import openmc


def get_plane(surface_list, counter, dim, val, boundary_type = "transmission", name = "", eps = 5):
	'''Return an instance of openmc.(X/Y/Z)Plane. Check if it exists, within
	a precision of 'eps'. If so, return it. Otherwise, create it.
	
	Inputs:
		surface_list:	list of instances of openmc.Surface; the list to check for
						surfaces in. WILL BE MODIFIED. 
		counter:		function that keeps track of your surface/cell numbers
						(such as pwr.Counter.count)
		dim:			str; 'x', 'y', or 'z'
		val:			float; value for x0, y0, or z0
		boundary_type:	"transmission", "vacuum", or "reflective".
						[Default: "transmission"]
		name:			str; creative name of surface
						[Default: empty string]
		eps:			int; number of decimal places after which two planes
						are considered to be the same.
						[Default: 5]	'''
	dim = dim.lower()
	valid = ("x", "xplane", "y", "yplane", "z", "zplane")
	assert (dim in valid), "You must specify one of " + str(valid)
	
	if dim in ("x", "xplane"):
		for xplane in surface_list:
			if isinstance(xplane, openmc.XPlane):
				if val == round(xplane.x0, eps):
					return xplane
		xplane =  openmc.XPlane(counter(SURFACE),
					boundary_type = boundary_type, x0 = val, name = name)
		surface_list.append(xplane)
		return xplane
	elif dim in ("y", "yplane"):
		for yplane in surface_list:
			if isinstance(yplane, openmc.YPlane):
				if val == round(yplane.y0, eps):
					return yplane
		yplane =  openmc.YPlane(counter(SURFACE),
					boundary_type = boundary_type, y0 = val, name = name)
		surface_list.append(yplane)
		return yplane
	elif dim in ("z", "zplane"):
		for zplane in surface_list:
			if isinstance(zplane, openmc.ZPlane):
				if val == round(zplane.z0, eps):
					return zplane
		zplane =  openmc.ZPlane(counter(SURFACE),
					boundary_type = boundary_type, z0 = val, name = name)
		surface_list.append(zplane)
		return zplane



