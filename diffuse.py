import numpy as np
import math as math

class AntMap:
	
	def __init__(self, width, height, neighbor_factor = .15, self_factor = .2, foodval = 100000, diffuse_type = 'linear'):
		self.NEIGHBOR_FACTOR = neighbor_factor
		self.SELF_FACTOR = self_factor
		self.FOODVAL = foodval
		self.width = width
		self.height = height

		if diffuse_type == 'linear':
			self.DIFFUSETYPE = 'linear'
			self.grid = np.zeros([width,height])
		elif diffuse_type == 'exp':
			self.DIFFUSETYPE = 'exp'
			self.EXP_FACTOR = (.2*foodval)/math.log(foodval)
			self.grid = np.ones([width,height])
		elif diffuse_type == 'max':
			self.DIFFUSETYPE = 'max'
			self.FACTOR = neighbor_factor
			self.grid = np.zeros([width,height])
		else:
			self.DIFFUSETYPE = 'linear'
			
	def printGrid(self):
		width=len(self.grid)
		length=len(self.grid[0])
		printerGrid = self.grid[18:25,:5].round()
	

		for i in range (0,width):
			for j in range (0, length):
				print str(printerGrid[i,j]) + '\t',
			print
			
	def setAntiTile(self, tile_loc):
		self.grid[tile_loc[0],tile_loc[1]] = -(self.FOODVAL / 100)
	
	def diffuseGrid(self):
		if (self.DIFFUSETYPE == 'linear'):
			self.linearDiffuseGrid()
		elif (self.DIFFUSETYPE == 'exp'):
			self.expDiffuseGrid()
		elif (self.DIFFUSETYPE == 'max'):
			self.maxDiffuseGrid()
		else:
			self.linearDiffuseGrid()
	
	def maxDiffuseGrid(self):
		self.grid = self.FACTOR*np.maximum(np.maximum(np.roll(self.grid,shift=1,axis=1), np.roll(self.grid,shift=-1,axis=1)),
											np.maximum(np.roll(self.grid,shift=1,axis=0),np.roll(self.grid,shift=-1,axis=0)))
	
	def expDiffuseGrid(self):
		self.grid = self.EXP_FACTOR*(np.log(np.roll(self.grid,shift=1,axis=1)) + np.log(np.roll(self.grid,shift=-1,axis=1)) +
											np.log(np.roll(self.grid,shift=1,axis=0)) + np.log(np.roll(self.grid,shift=-1,axis=0)))
		self.grid[self.grid==0] = 1	#accounts for log(0) = -inf 
		
	def linearDiffuseGrid(self):
		#TODO: replace with np.take?
		self.grid = self.NEIGHBOR_FACTOR*((np.roll(self.grid,shift=1,axis=1)) + (np.roll(self.grid,shift=-1,axis=1)) + 
			(np.roll(self.grid,shift=1,axis=0)) + (np.roll(self.grid,shift=-1,axis=0))) + self.SELF_FACTOR*self.grid
			
	def setGridObjects(self, objects):
		for location in objects:
			self.grid[location[0],location[1]] = self.FOODVAL
			
	def setGridObjectsFromArray(self, array):
			self.grid[array == True] = self.FOODVAL
			
	def zeroGrid(self):
		if self.DIFFUSETYPE == 'linear':
			self.grid = np.zeros([self.width,self.height])
		elif self.DIFFUSETYPE == 'exp':
			self.grid = np.ones([self.width,self.height])
		elif self.DIFFUSETYPE == 'max':
			self.grid = np.zeros([self.width,self.height])			
			
	def setGridWalls(self, walls):
		for location in walls:
			self.setGridWall(location)
				
	def setGridWall(self, wall):
		if self.DIFFUSETYPE=='exp':
			self.grid[wall[0],wall[1]] = 1
		elif self.DIFFUSETYPE == 'linear':
			self.grid[wall[0],wall[1]] = 0
		else:
			self.grid[wall[0],wall[1]] = 0
