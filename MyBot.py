from ants import *
from diffuse import *
import numpy as np
import random



class MyBot:
	def __init__(self):
		pass
		
	def do_setup(self, ants):

		self.orders = {}
		self.enemy_hills = []
		self.dead_enemy_hills = []
		self.defensive_matrix = {}
		self.unseen_object_value = 1000
		self.food_object_value = 100000
		self.enemy_object_value = 10000
		self.food_map = AntMap(ants.rows,ants.cols,.2,.2,self.food_object_value,'linear')
		self.unseen_map = AntMap(ants.rows,ants.cols,.9,.2,self.unseen_object_value,'max')
		self.explore_map = np.ones([ants.rows, ants.cols])
		self.enemy_map = AntMap(ants.rows,ants.cols,.9,0,self.enemy_object_value,'max')
		self.turn_counter = 1
		self.time_avg = []
		self.enemy_hill_attack_radius = min(3000, (min(ants.rows, ants.cols))/5)
	def do_turn(self, ants):
		#track all moves, prevent collisions
		self.orders = {}

		def do_move_direction(loc, direction):
			new_loc = ants.destination(loc, direction)
			if (ants.unoccupied(new_loc) and new_loc not in self.orders and new_loc not in ants.water_list):
				ants.issue_order((loc, direction))
				self.orders[new_loc] = loc
				self.explore_map[new_loc] *= .55
				return True
			else:
				return False

		targets = {}
		def do_move_location(loc, dest):
			directions = ants.direction(loc, dest)
			for direction in directions:
				if do_move_direction(loc, direction):
					targets[dest] = loc
					return True
			return False
		
		def get_neighbors(antmap,loc):
			x = ant_loc[0]
			y = ant_loc[1]
			neighbors = [(antmap.grid[(x+1)%ants.rows,y],((x+1)%ants.rows,y)),
						 (antmap.grid[(x-1)%ants.rows,y],((x-1)%ants.rows,y)),
						 (antmap.grid[x,(y+1)%ants.cols],(x,(y+1)%ants.cols)),
						 (antmap.grid[x,(y-1)%ants.cols],(x,(y-1)%ants.cols))]
			neighbors.sort(reverse=True)
			return neighbors
			
		def get_explore_neighbors(loc):
			x = loc[0]
			y = loc[1]
			neighbors = [(self.explore_map[(x+1)%ants.rows,y],((x+1)%ants.rows,y)),
						 (self.explore_map[(x-1)%ants.rows,y],((x-1)%ants.rows,y)),
						 (self.explore_map[x,(y+1)%ants.cols],(x,(y+1)%ants.cols)),
						 (self.explore_map[x,(y-1)%ants.cols],(x,(y-1)%ants.cols))]
			neighbors.sort(reverse=True)
			return neighbors
	
		def do_move_neighbors(neighbors, ant_loc):
			for loc in neighbors:
				#if (loc[1] not in targets and ants.passable(loc[1])):
				if do_move_location(ant_loc, loc[1]):
					break

		def should_defend(loc):
			if loc in ants.my_hills_corners:
				hill_loc = (0,0)
				for hill in ants.my_hills():
					if ants.distance(loc, hill) == 2:
						hill_loc = hill
						break
				my_ants = len(ants.my_ants())
				if my_ants > 35:
					return True
				elif my_ants > 27 and ants.num_corners_occupied(hill_loc) < 4:
					return True
				elif my_ants > 22 and ants.num_corners_occupied(hill_loc) < 3:
					return True
				elif my_ants > 13 and ants.num_corners_occupied(hill_loc) < 2:
					return True
				else:
					return False
		self.defensive_matrix = {}			
		def should_move_to_defend(loc):
			if loc in ants.my_hills_cross:
				hill_loc = (0,0)
				for hill in ants.my_hills():
					if ants.distance(loc, hill) == 1:
						hill_loc = hill
						break
				my_ants = len(ants.my_ants())
				
				# based on number of ants we have, build a basic defensive structure around our hill
				if  (my_ants > 35 and ants.num_corners_occupied(hill_loc) < 4) or \
					(my_ants > 27 and ants.num_corners_occupied(hill_loc) < 3) or \
					(my_ants > 22 and ants.num_corners_occupied(hill_loc) < 2) or \
					(my_ants > 13 and ants.num_corners_occupied(hill_loc) < 1):
						if abs(hill_loc[0] - loc[0]) == 1:
							x = loc[0]
							y = loc[1]
							for corner in [ (x,(y+1)%ants.cols),(x,(y-1)%ants.cols), ((x+1)%ants.rows,y),((x-1)%ants.rows,y)]:
								if do_move_location(loc, corner):
									return True
						else:
							x = loc[0]
							y = loc[1]
							for corner in [ ((x+1)%ants.rows,y),((x-1)%ants.rows,y),(x,(y+1)%ants.cols),(x,(y-1)%ants.cols)]:
								if do_move_location(loc, corner):
									return True							
			return False
				
				
		def diffuse_unseen():

			iterations = 2*ants.turntime / 3
			
			for i in range(50):
				self.unseen_map.diffuseGrid()
				self.unseen_map.setGridWalls(ants.water_list)
				self.unseen_map.setGridObjectsFromArray(ants.unseen)
		
		self.unseen_map.grid[ants.vision == True] += 
		
		for hill_loc in ants.my_hills():
			self.orders[hill_loc] = hill_loc
		
		#find new enemy hills
		for hill_loc, hill_owner in ants.enemy_hills():
			if hill_loc not in self.enemy_hills and hill_loc not in self.dead_enemy_hills:
				self.enemy_hills.append(hill_loc)
				self.enemy_map.setGridObjects(self.enemy_hills)

		
		#increment explore map
		self.explore_map += 10
		for loc in ants.water_list:
			self.explore_map[loc] = 0
		for loc in ants.my_hills():
			self.explore_map[loc] = 0
		
		#diffuse unseen grid
		diffuse_unseen()
		
		#reset food grid
		self.food_map.zeroGrid()
		#diffuse food map
		for i in range(15):
			self.food_map.setGridObjects(ants.food())

			self.food_map.diffuseGrid()
			self.food_map.setGridWalls(ants.water_list)
		#diffuse enemy map
		for i in range(8):
			self.enemy_map.diffuseGrid()
			self.enemy_map.setGridWalls(ants.water_list)
			self.enemy_map.setGridObjects(self.enemy_hills)
			for ant_loc in ants.my_ants():
				self.food_map.setGridWall(ant_loc)
			for hill_loc in ants.my_hills():
				self.food_map.setGridWall(hill_loc)
			
		for ant_loc in ants.my_ants():
			x = ant_loc[0]
			y = ant_loc[1]
			if ant_loc in self.enemy_hills:
				self.enemy_hills.remove(ant_loc)
				self.dead_enemy_hills.append(ant_loc)
				self.enemy_map.grid = np.zeros([ants.rows,ants.cols])
				if len(self.enemy_hills) > 0:
					self.enemy_map.setGridObjects(self.enemy_hills)
					for i in range(20):
						self.enemy_map.diffuseGrid()
						self.enemy_map.setGridWalls(ants.water_list)
	
			food_neighbors = get_neighbors(self.food_map, ant_loc)
			enemy_neighbors = get_neighbors(self.enemy_map, ant_loc)
			explore_neighbors = get_explore_neighbors(ant_loc)
			unseen_neighbors = get_neighbors(self.unseen_map, ant_loc)
			
			
			#check defensive matrix, a common simple defensive tactic used by other players
			if ant_loc in ants.my_hills() and food_neighbors[0][0] < 1:
					directions = [(x,y-1),(x,y+1),(x-1,y),(x+1,y)]
					random.shuffle(directions, random.random)
					for direction in directions:
						do_move_location(ant_loc, direction)
						break
			
			elif should_defend(ant_loc):
				pass
			elif should_move_to_defend(ant_loc):
				pass
			else:

				if (enemy_neighbors[0][0] > self.enemy_hill_attack_radius):
					do_move_neighbors(enemy_neighbors, ant_loc)
				
				elif (food_neighbors[0][0] > 50):
					do_move_neighbors(food_neighbors, ant_loc)
				elif (unseen_neighbors[3][0] > 0):
					do_move_neighbors(unseen_neighbors, ant_loc)
				else:
					do_move_neighbors(explore_neighbors, ant_loc)
				
				
					


if __name__ == '__main__':
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass
		
	try:
		Ants.run(MyBot())
	except KeyboardInterrupt:
		print('ctrl-c, leaving ...')