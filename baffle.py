# Baffle
#
# Function and class for generating a PWR baffle

class Baffle(object):
	"""Inputs:
		mat:	instance of Material
		thick:	thickness of baffle (cm)
		gap:	thickness of gap (cm) between the outside assembly
				(including the assembly gap) and the baffle itself
		"""
	def __init__(self, mat, thick, gap):
		self.mat = mat
		self.thick = thick
		self.gap = gap
	def __str__(self):
		return "Baffle (" + self.thick + " cm thick)"

