# PWR Assembly
# 
# Module for the OpenMC Python API. Once developed, it should
# contain everything needed to generate an openmc.Universe containing
# a model of a Westinghouse-style PWR assembly

import openmc
from pwr.nozzle import Nozzle
from pwr.functions import get_plane
from pwr.settings import SURFACE, CELL, MATERIAL, UNIVERSE
from copy import copy
from math import sqrt



"""
def duplicate(orig):
	'''Copy an OpenMC object, except for a new id 
	
	Input:
		orig: instance of openmc.(Surface, Cell, Material, or Universe)
	
	Output:
		dupl: same, but with a different instance.id 
	'''
	dup = copy(orig)
	if isinstance(orig, openmc.Surface):
		dup.id = openmc.AUTO_SURFACE_ID
		openmc.AUTO_SURFACE_ID += 1
	elif isinstance(orig, openmc.Cell):
		dup.id = openmc.AUTO_CELL_ID
		openmc.AUTO_CELL_ID += 1
	elif isinstance(orig, openmc.Material):
		dup.id = openmc.AUTO_MATERIAL_ID
		openmc.AUTO_MATERIAL_ID += 1
	elif isinstance(orig, openmc.Universe):
		dup.id = openmc.AUTO_UNIVERSE_ID
		openmc.AUTO_UNIVERSE_ID += 1
	else:
		name = orig.__class__.__name__
		raise TypeError(str(orig) + " is an instance of " + name + 
					"; expected Surface, Cell, Material, or Universe")
	return dup
"""

def duplicate(orig, counter):
	'''Copy an OpenMC object, except for a new id 
	
	Input:
		orig: 		instance of openmc.(Surface, Cell, Material, or Universe)
		counter:	instance of Counter
	
	Output:
		dupl: 		same as 'orig', but with a different instance.id 
	'''
	dup = copy(orig)
	if isinstance(orig, openmc.Surface):
		dup.id = counter.count(SURFACE)
	elif isinstance(orig, openmc.Cell):
		dup.id = counter.count(CELL)
	elif isinstance(orig, openmc.Material):
		dup.id = counter.count(MATERIAL)
	elif isinstance(orig, openmc.Universe):
		dup.id = counter.count(UNIVERSE)
	else:
		name = orig.__class__.__name__
		raise TypeError(str(orig) + " is an instance of " + name + 
					"; expected Surface, Cell, Material, or Universe")
	return dup


class SpacerGrid(object):
	'''Object to hold properties of an assembly's spacer grids
	
	Parameters:
		key: 		string; unique name of this spacer grid
		height:		float; height (cm) of the spacer around the pins
		mass:		float; mass in g of the entire spacer grid's material
		material:	instance of class openmc.Material
		pitch:		float; pin pitch (cm) 
		npins:		number of pins across an assembly
	Attributes:
		(key, height, mass, material - as above)
		thickness:	float; thickness (cm) of the grid around each pin, 
					or half the total thickness between pins
		'''
	
	def __init__(self, key, height, mass, material, pitch, npins):
		self.key = key	
		self.height = height	
		self.mass = mass		
		self.material = material
		self.thickness = self.calculate_thickness(pitch, npins)
	
	def calculate_thickness(self, pitch, npins):
		'''Calculate the thickness of the spacer surrounding each pincell.
		Inputs:
			pitch:		float; pin pitch (cm)
			npins:		int; number of pins across Assembly (npinsxnpins)
		'''
		
		''' Method:
		
		Volume = mass / density;		Combined Area = Volume / height
			Therefore, [ A = m/rho/h ],		and the area around a single pincell:
												a = m/rho/h / npins^2
			
			The area of the spacer material around one cell can also be found:
				a = p^2 - (p - 2*t)^2,		where 't' is the thickness and 'p' is the pitch
			->  a = p^2 - [p^2 - 4*t*p + 4*t^2]
			->  a = 4*t*p - 4*t^2
				
			Equate the two expressions for a:
				m/rho/h / npins^2 = 4*t*p - 4*t^2
			Then solve for 't' using the quadratic equation:
			
			              [             (          m/rho/h   ) ]
				t = 0.5 * [ p  +/- sqrt ( p^2 -   ---------- ) ]
				          [             (          npins^2   ) ]
        '''
		
		A = self.mass / self.material.density / self.height
		t = 0.5*(pitch - sqrt(pitch**2 - A/npins**2))
		return t
		
	def __str__(self):
		name = self.key + ': ' + str(self.thickness) + " cm"
		return name


def add_spacer_to(pincell, pitch, t, material, counter, surflist):# = []):
	'''Given a pincell to be placed in a lattice, add
	the spacer grid to the individual cell.
	
	Inputs:
		pincell:	instance of openmc.Universe describing the pincell
					and its concentric rings of instances of openmc.Cell
		pitch:		float; pin pitch in cm
		t:			float; thickness in cm of one edge of the spacer between
					two pincells (HALF the total thickness)
		material:	instance of openmc.Material from which the spacer is made
		counter:	instance of Counter to keep track of universe numbers
		surflist:	list of existing OpenMC surfaces. [Default: empty list]
					This is optional, but strongly recommended if you are adding
					spacers to more than one pin cell.
	
	Output:
		new_cell:	instance of openmc.Universe describing the pincell
					surrounded by the spacer
	'''
	assert isinstance(pincell, openmc.Universe), str(pincell) + "must be an openmc.Universe (not a Cell)"
	assert isinstance(material, openmc.Material), str(material) + "is not an instance of openmc.Material" 
	
	orig_list = list(pincell.cells.values())
	
	# Create necessary planes
	p = pitch / 2.0
	top_out = get_plane(surflist, counter, 'y',  p)
	top_in  = get_plane(surflist, counter, 'y',  p - t)
	bot_in  = get_plane(surflist, counter, 'y', -p + t)
	bot_out = get_plane(surflist, counter, 'y', -p)
	left_out  = get_plane(surflist, counter, 'x', -p)		# He feels left out
	left_in   = get_plane(surflist, counter, 'x', -p + t)
	right_in  = get_plane(surflist, counter, 'x',  p - t)
	right_out = get_plane(surflist, counter, 'x',  p)
	
	# Get the outermost (mod) Cell of the pincell
	mod_cell = duplicate(orig_list[-1], counter)
	
	# Make a cell encompassing the 4 sides of the spacer
	spacer = openmc.Cell(counter.add_cell(), name = pincell.name + " spacer")
	spacer.region = (+left_out	& +top_in 	& -top_out	&	-right_out) | \
					(+right_in	& -right_out& +bot_in	& 	-top_in)	| \
					(+left_out	& -left_in	& +bot_in	&	-top_in)	| \
					(+bot_out 	& -bot_in	& +left_out	&	-right_out )  
					#& mod_cell.region	# top; bottom; right; left; #outside cylinder	 
	spacer.fill = material
	
	# Then fix the moderator cell to be within the bounds of the spacer
	mod_cell.region = mod_cell.region & \
					(+bot_in	& +left_in	& -top_in	& -right_in )
	
	new_cell = openmc.Universe(counter.add_universe(), name = pincell.name + " gridded")
	# Add all of the original cells except the old mod cell
	for i in range(len(orig_list) - 1):
		new_cell.add_cell(orig_list[i])
	new_cell.add_cell(mod_cell) 	# the new mod cell
	new_cell.add_cell(spacer)
	
	return new_cell


def add_grid_to(lattice, pitch, npins, spacergrid, counter, griddict, surflist):# = []):
	'''Add a spacer to every pincell in the lattice.
	FIXME: Determine 'pitch' and 'npins' from the attributes of 'lattice'

	Inputs:
		lattice:		instance of openmc.RectLattice
		pitch:			float; its pitch (cm)
		npins:			int; number of pins across
		spacergrid:		instance of SpacerGrid
		counter:		instance of Counter
		griddict:		dictionary of pincells and their gridded variants.
						Will be directly modified. Optional, but strongly recommended.
		surflist:		list of instances of openmc.Surface to check against.
						Optional, but strongly recommended.
	Output:
		gridded:		instance of openmc.RectLattice with the grid applied
						to every cell'''
	
	assert isinstance(lattice, openmc.RectLattice), "'lattice' must be a RectLattice."
	assert isinstance(spacergrid, SpacerGrid), "'spacergrid' must be an instance of SpacerGrid."
	n = int(npins)
	new_universes = [[None,]*n,]*n
	
	for j in range(n):
		row = new_universes[j]
		for i in range(n):
			old_cell = lattice.universes[j][i]
			key = str(old_cell.id)
			
			#debug
			if lattice.name == "PLUG":
				if key not in griddict:
					print("Cell", key, "is not in griddict...generating")
				
			
			if key in griddict:
				new_cell = griddict[key]
			else:
				new_cell = add_spacer_to(old_cell, pitch, spacergrid.thickness, spacergrid.material,
										  counter, surflist)
				griddict[key] = new_cell
				print("Just added pincell", key, ":", new_cell.id)
			row[i] = new_cell
		new_universes[j] = row
	
	if lattice.name:
		new_name = lattice.name + "-gridded"
	else:
		new_name = str(lattice.id) + "-gridded"
	gridded = openmc.RectLattice(counter.add_universe(), name = new_name)
	gridded.pitch = (pitch, pitch)
	gridded.lower_left = [-pitch * npins / 2.0] * 2
	gridded.universes = new_universes
	return gridded
	


class Assembly(object):
	'''Constructor for an OpenMC Universe containing:
		cells for the upper/lower nozzles,
		lattices (with and without spacer grids),
		and the surrounding moderator.
	
	Parameters (all optional except "key"):
		key:				str; short, unique name of this Assembly as will appear in the core lattice.
		name:				str; more descriptive name of this Assembly, if desired
							[Default: same as key]
		universe_id:		int; unique integer identifier for its OpenMC universe
							[Default: None, and will be assigned automatically at instantiation of openmc.Universe]
		pitch:				float; pitch (cm) between pincells in the lattices
							[Default: 0.0]
		npins:				int; number of pins across the assembly
							[Default: 0]
		walls:				list of instances of openmc.Surface: [min_x, max_x, min_y, max_y] 
							Used to create the 2D region within the assembly.
							[Will be generated automatically if not provided.]
		lattices:			list of instances of openmc.RectLattice, in the axial order they appear in the assembly
							(bottom -> top).
							[Default: empty list]
		lattice_elevs:		list of floats describing the elevations (cm) of each boundary in 'lattices',
							relative to the bottom core plate. The next lattice starts where the last leaves off.
							**Must contain exactly len(lattices)+1 entries**
							[Default: empty list] 
		spacers:			list of instances of SpacerGrid, in the axial order they appear in the assembly
							(bottom -> top). 
							[Default: empty list]
		spacer_mids:		list of floats describing the elevations (cm) of the midpoint of each spacer grid
							in 'spacers', relative to the bottom core plate. Gaps are expected.
							***Must contain exactly len(spacers) entries**
							[Default: empty list]
		lower_nozzle:		instance of Nozzle, starting at z=0 and terminating at min(lattice_elevs)
							[Default: None]
		upper_nozzle:		instance of Nozzle, starting at max(lattice_elevs) and terminating at z += Nozzle.height
							[Default: None]
		mod:				instance of openmc.Material describing  moderator surrounding the assembly.
							[Default: None] 
		counter:			instance of pwr.Counter used for keeping track of surface/cell/material/universe IDs.
							[Default: None] 
	
	Attributes:
		All the above, plus the following created at self.build():
		spacer_elevs:		list of the elevations of the tops/bottoms of all spacer grids
		all_elevs:			list of all axial elevations, created when (lattice_elevs + spacer_elevs)
							have been concatenated, sorted, and checked for duplicates
		openmc_surfs:		list of instances of openmc.Surface used in the construction of this assembly
		openmc_cells:		list of all instances of openmc.Cell used in the construction of this assembly
		gridded_pincells:	dictionary of pincells which have a gridded version, in the following format:
							{'orig. universe id': gridded instance of openmc.Universe}
		gridded_lattices:	dictionary of lattices  which have a gridded version, in the following format:
							{'orig. universe id': gridded instance of openmc.RectLattice}
		assembly:			instance of openmc.Universe.
							the whole reason you instantiated THIS object.
							the OpenMC representation of the fuel assembly
	'''

	def __init__(self, 	key = "", 		name = "", 			universe_id = None,
						pitch = 0.0, 	npins = 0,			walls = [],
						lattices = [], 	lattice_elevs = [],	spacers = [], 	spacer_mids = [],
						lower_nozzle = None, 				upper_nozzle = None, 
						mod = None,		counter = None):
		self.key = key
		self.name = name
		self.universe_id = universe_id
		self.pitch = pitch;					self.npins = npins
		self.lattices = lattices;			self.lattice_elevs = lattice_elevs
		self.spacers = spacers;				self.spacer_mids = spacer_mids
		self.lower_nozzle = lower_nozzle;	self.upper_nozzle = upper_nozzle
		self.walls = walls;
		self.mod = mod
		self.counter = counter
	
	
	def __str__(self):
		return self.name
	
	
	def __get_plane(self, dim, plane, boundary_type = None, name = "", eps = None):
		'''Shorthand for pwr.functions.get_plane() specific to this assembly'''
		if not boundary_type:
			boundary_type = "transmission"
		if not eps:
			eps = 5
		return get_plane(self.openmc_surfaces, self.counter, dim, plane, boundary_type, name, eps)
		
	
	
	def __prebuild(self):
		'''Check that all the required properties are there.
		If not, error out. Otherwise, do a few operations prior to build().'''
		
		if not self.name:
			self.name = self.key
		blank_allowable = ['universe_id', 'spacers', 'spacer_mids', 'upper_nozzle', 'walls']
		if min(self.lattice_elevs) == 0:
			blank_allowable.append('lower_nozzle')
		
		# Check that all necessary parameters are present.
		err_str = "Error: the following parameters need to be set:\n"
		errs = 0
		for attr in self.__dict__:
			if not self.__dict__[attr]:
				if attr not in blank_allowable:
					errs += 1
					err_str += '\t- ' + attr + '\n'
		if errs:
			raise TypeError(err_str)
		
		# Check that the number of entries in the lists is correct
		assert (len(self.lattice_elevs) == len(self.lattices) +1), \
			"Error: number of entries in lattice_elevs must be len(lattices) + 1"
		assert (len(self.spacers) == len(self.spacer_mids)), \
			"Error: number of entries in spacer_elevs must be len(spacers)"
		
		# Initialize the openmc list attributes
		self.openmc_cells = []
		self.openmc_surfaces = []
		
		
		# Combine spacer_elevs and lattice_elevs into one list to rule them all
		if self.spacer_mids:
			self.spacer_elevs = []
			for i in range(len(self.spacers)):
				spacer = self.spacers[i]
				mid = self.spacer_mids[i]
				s_bot = mid - spacer.height / 2.0
				s_top = mid + spacer.height / 2.0
				self.spacer_elevs += (s_bot, s_top)
			elevs = self.spacer_elevs + self.lattice_elevs
			self.all_elevs = list(set(elevs))	# Remove the duplicates
			self.all_elevs.sort()
		else:
			self.all_elevs = self.lattice_elevs
		
		# Dictionaries to keep track of which pincells and lattices have had spacer grids generated  
		# The key is the (string of the) original pincell/lattice, and the value is the gridded cell/lattice.
		self.gridded_pincells = {}
		self.gridded_lattices = {}
		
		
		# Finally, create the xy bounding planes
		half = self.pitch*self.npins/2.0
		
		if self.walls:
			[min_x, max_x, min_y, max_y] = self.walls
		else:
			min_x = self.__get_plane('x', -half, name = self.name + ' - min_x') 
			max_x = self.__get_plane('x', +half, name = self.name + ' - max_x') 
			min_y = self.__get_plane('y', -half, name = self.name + ' - min_y') 
			max_y = self.__get_plane('y', +half, name = self.name + ' - max_y') 
			self.walls = [min_x, max_x, min_y, max_y]
		
		self.openmc_surfaces = [min_x, max_x, min_y, max_y]
		self.wall_region = openmc.Intersection(+min_x & +min_y & -max_x & -max_y)
		self.openmc_cells = []
	
	
	
		
	
	def test_prebuild(self):
		'''Temporary method--to be removed once this class is complete'''
		self.__prebuild()
	
	
	def build(self):
		'''Construct the assembly from the ground up.
		
		Output:
			instance of openmc.Universe'''
		
		self.__prebuild()
		
		# Start at the bottom
		surf0 = openmc.ZPlane(self.counter.add_surface(), name="bottom", z0 = 0)
		last_s = surf0
		self.openmc_surfaces.append(surf0)
		
		if self.lower_nozzle:
			lnoz = openmc.Cell(self.counter.add_cell(), "lower nozzle")
			nozzle_top = self.__get_plane('z', self.lower_nozzle.height)
			lnoz.region = (self.wall_region & +last_s & -nozzle_top)
			lnoz.fill = self.lower_nozzle.material
			self.openmc_cells.append(lnoz)
			last_s = nozzle_top
		
		
		'''
		# The convention used here to avoid creating extra lattices when applying grids:
		# When a grid is added by calling add_grid_to(), the lattice's name becomes "oldname-gridded".
		gridded_lattices = {}
		'''
		
		for z in self.all_elevs[1:]:
			s = self.__get_plane('z', z)
			# See what lattice we are in
			for i in range(len(self.lattices)):
				#if z > self.lattice_elevs[i]:
				if z <= self.lattice_elevs[i] and z > self.lattice_elevs[i-1]:
					break
			lat = self.lattices[i-1]
			# Check if there is a spacer grid
			if self.spacer_mids:
				for g in range(len(self.spacer_mids)):
					#if z > self.spacer_mids[g]:
					if z == self.spacer_elevs[g]:
						break
				# Even numbers are bottoms, odds are top
				grid = False
				if (g-1) % 2 == 0:
					# Then the last one was a bottom: a grid is present
					grid = self.spacers[g-1]
					#debug
					print("\n\n", "z=",z, lat.name, grid.key)
				
				# OK--now we know what the current lattice is, and whether there's a grid here.
				if grid:
					g_id = str(lat.id)
					if g_id in self.gridded_lattices:
						# Then this one has been done before
						lat = self.gridded_lattices[g_id]
						print("Success: looked up", lat.name)
					else:
						# We need to add the spacer grid to this one, and then add it to the index
						lat = add_grid_to(lat, self.pitch, self.npins, grid, self.counter,
											self.gridded_pincells, self.openmc_surfaces)
						self.gridded_lattices[g_id] = lat
						print("Unable to find", lat.name, "; generated.")
						print(self.gridded_lattices.keys())
				
			# Now, we have the current lattice, for the correct level, with or with a spacer
			# grid as appropriate. Time to make the layer.
			layer = openmc.Cell(self.counter.add_cell(), name = lat.name)
			layer.region = (self.wall_region & +last_s & -s)
			layer.fill = lat
			self.openmc_cells.append(layer)
			
			# And then prepare for the next loop around
			last_s = s
		
		# Great, we've done all the layers now!
		# Add the top nozzle if necessary:
		if self.upper_nozzle:
			unoz = openmc.Cell(self.counter.add_cell(), "upper nozzle")
			nozzle_top = self.__get_plane('z', self.upper_nozzle.height)
			unoz.region = (self.wall_region & +last_s & -nozzle_top)
			unoz.fill = self.upper_nozzle.material
			self.openmc_cells.append(lnoz)
			last_s = nozzle_top
		
		# Finally, surround the whole assembly with moderator
		mod_cell = openmc.Cell(self.counter.add_cell(), name = self.name + " mod")
		mod_cell.region = (~self.wall_region | +last_s | -surf0)
		mod_cell.fill = self.mod
		self.openmc_cells.append(mod_cell)
		
		# And we're done!! Zip it all up in a universe.
		if self.universe_id:
			uid = self.universe_id
		else:
			uid = self.counter.add_universe()
		self.assembly = openmc.Universe(uid, name = self.name)
		self.assembly.add_cells(self.openmc_cells)
		
		print(self.gridded_pincells)#debug
		return self.assembly




# Test
if __name__ == '__main__':
	from pwr.mixture import Mixture
	# Define a global test moderator
	mod = openmc.Material(1, "mod")
	mod.set_density("g/cc", 1.0)
	mod.add_nuclide("h1", 2.0/3, 'ao')
	mod.add_nuclide("o16", 1.0/3, 'ao')
	
	# Define a simple test material
	iron = openmc.Material(2, "iron")
	iron.set_density("g/cc", 7.8)
	iron.add_element("Fe", 1, 'ao', expand=True)
	
	mix1 = Mixture([mod, iron], [0.5,0.5], 33, 'watery iron')
	assert isinstance(mix1, openmc.Material)	
	noz1 = Nozzle(10, 6250, iron, mod, 1, 10)

	# Test a pincell
	cyl0 = openmc.ZCylinder(10, R = 0.300) 
	cyl1 = openmc.ZCylinder(11, R = 0.333)
	cyl2 = openmc.ZCylinder(12, R = 0.350)
	ring0 = openmc.Cell(100, fill = iron, region = -cyl0)
	ring1 = openmc.Cell(101, fill = mod, region = (-cyl1 & +cyl0) )
	ring2 = openmc.Cell(102, fill = mix1, region = (-cyl2 & +cyl1) )
	outer = openmc.Cell(199, fill = mod, region = +cyl2)
	uni = openmc.Universe(cells = (ring0, ring1, ring2, outer), name = "test pincell")
	print(uni)
	gridded = add_spacer_to(uni, 1.0, 0.10, iron)
	print(gridded)
	#print(duplicate(uni))

