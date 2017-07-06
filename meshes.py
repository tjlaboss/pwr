# Meshes
#
# Module for tally meshes

import openmc
import math

_len_err_str = "The length of `nzs` must match the length of `dzs`."

class MeshError(Exception):
	""" Class for errors involving mesh structure. """
	pass


class Mesh_Group(object):
	"""Container for multiple uniform meshes to cover a 3D assembly.
	Must have the same (x, y) pitch, but may have multiple layers
	with different z-pitches (dz).
	
	Meshes must be stacked sequentially.
	
	Parameters:
	-----------
	pitch:          float, or tuple of (xpitch, ypitch); cm
	nx:             int; number of cuts in the x-direction
	ny:             int; number of cuts in the y-direction
	lower_left:     tuple of (x0, y0, z0); the lower left coordinate (cm)
					of all the meshes
					[Default: (0, 0, 0)]
	id0:            int; the ID number of the lowest mesh. Each additional
					mesh increases by 1.
					[Default: 1]
	"""
	
	def __init__(self, pitch, nx, ny, lower_left = (0.0, 0.0, 0.0), id0 = 1):
		if isinstance(pitch, (int, float)):
			self._dx, self._dy = pitch, pitch
		elif len(pitch) in (2, 3):
			self._dx, self._dy = pitch[0:2]
		else:
			raise IndexError("`pitch` must be of length 1, 2, or 3")
		self._nx = nx
		self._ny = ny
		self._meshes = []
		self._mesh_filters = []
		self._tallies = []
		self.x0, self.y0, self.z0 = lower_left
		self._z = self.z0
		self._id0 = id0
		self._nzs = None
		self._dzs = None
	
	@property
	def meshes(self):
		return self._meshes
	
	@property
	def tallies(self):
		return self._tallies
	
	@property
	def id0(self):
		return self._id0
	
	@property
	def height(self):
		return self._z
	
	@property
	def nx(self):
		return self._nx
	
	@property
	def ny(self):
		return self._ny
	
	@property
	def nzs(self):
		return self._nzs
	
	@property
	def dzs(self):
		return self._dzs
	
	@property
	def n(self):
		if self._dzs and self._nzs:
			return len(self._nzs)
		else:
			return 0
	
	@property
	def mesh_filters(self):
		return self._mesh_filters
	
	
	@nzs.setter
	def nzs(self, nzs_in):
		if self._dzs:
			if len(nzs_in) != len(self._dzs):
				raise IndexError(_len_err_str)
		self._nzs = nzs_in
	
	@dzs.setter
	def dzs(self, dzs_in):
		if self._nzs:
			if len(dzs_in) != len(self._nzs):
				raise IndexError(_len_err_str)
		self._dzs = dzs_in


	def add_mesh(self, z1 = None, nz = None, dz = None):
		"""Add a mesh to the group. You must supply two of the
		three parameters. If all three are supplied,
		`dz` will be ignored.
		
		Parameters:
		-----------
			z1:         float (cm); top of this mesh
			dz:         float (cm); height of a mesh cut
			nz:         int; number of mesh cuts
		"""
		# z1 may be 0
		if z1 is not None:
			assert z1 > self._z, "z1 must be larger than " + str(self._z)
			ztrue = True
		else:
			ztrue = False
		
		if nz and ztrue:
			dz = (z1 - self._z)/nz
		elif nz and dz:
			z1 = self._z + nz*dz
		elif dz and ztrue:
			nz = int(round(z1/dz))
			if not math.isclose(nz, z1/dz):
				# Then there's no way to slice this up right
				delta_z = z1 - self._z
				errstr = "Cannot cut {delta_z} cm into slices of {dz} cm.".format(**locals())
				raise MeshError(errstr)
			
		new_mesh = openmc.Mesh(self.id0)
		new_mesh.type = "regular"
		new_mesh.lower_left = (self.x0, self.y0, self._z)
		new_mesh.dimension = (self._nx, self._ny, nz)
		new_mesh.width = (self._dx, self._dy, dz)
		
		new_filter = openmc.MeshFilter(new_mesh)
		new_tally = openmc.Tally(self.id0)
		new_tally.filters = [new_filter]
		new_tally.scores = ["fission"]
		
		self._meshes.append(new_mesh)
		self._mesh_filters.append(new_filter)
		self._tallies.append(new_tally)
		self._id0 += 1
		self._z = z1
	
	
	def build_group(self):
		"""Use the `nzs` and `dzs` attributes to autobuild the mesh group"""
		assert self._nzs, "Mesh_group.nzs has not been set."
		assert self._dzs, "Mesh_group.dzs has not been set."
		for i in range(self.n):
			self.add_mesh(nz = self._nzs[i], dz = self._dzs[i])
	


# Test
if __name__ == "__main__":
	
	test_group = Mesh_Group(1.26, 17, 17, lower_left = (-17/1.26, -17/1.26, 11.951))
	test_group.nzs = [1, 7, 1, 6, 1, 6, 1, 6, 1, 6, 1, 6, 1, 5]
	test_group.dzs = [3.866, 8.2111429, 3.81, 8.065, 3.81, 8.065, 3.81, 8.065, 3.81, 8.065, 3.81, 8.065, 3.81, 7.9212]
	test_group.build_group()
	print(test_group.meshes)


