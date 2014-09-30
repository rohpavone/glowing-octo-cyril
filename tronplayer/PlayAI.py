from tronclient.Client import *

class Node():

	def __init__(self, p=[0,0], c=0, t=[0,0], pr=[], dir="up"):
		self.c = c;
		self.x = p[0]
		self.y = p[1]
		self.active = True
		self.opt = []
		self.prev = pr
		self.tx = t[0]
		self.ty = t[1]
		self.d = dir
		
	def find_target(self, map):
		dy = self.ty - self.y
		dx = self.tx - self.x
		adx = abs(dx)
		ady = abs(dy)
		
		p1 = Node(p=[self.x, self.y -1], c=self.c+1, t=[self.tx, self.ty], pr=self, dir="up") # up
		p2 = Node(p=[self.x, self.y +1], c=self.c+1, t=[self.tx, self.ty], pr=self, dir="down") # down
		p3 = Node(p=[self.x - 1, self.y], c=self.c+1, t=[self.tx,self.ty], pr=self, dir="left") # left
		p4 = Node(p=[self.x + 1, self.y], c=self.c+1, t=[self.tx,self.ty], pr=self, dir="right") # right			
		
		
		if ady >= adx:
			if dy < 0:
				self.opt.append(p1)
				if dx > 0:
					self.opt.append(p4)
					self.opt.append(p3)
				else:
					self.opt.append(p3)
					self.opt.append(p4)
				self.opt.append(p2)
			elif dy > 0:
				self.opt.append(p2)
				if dx > 0:
					self.opt.append(p4)
					self.opt.append(p3)
				else:
					self.opt.append(p3)
					self.opt.append(p4)
				self.opt.append(p1)
			else:
				if dx > 0:
					self.opt.append(p4)
					self.opt.append(p3)
				else:
					self.opt.append(p3)
					self.opt.append(p4)
				self.opt.append(p1)
				self.opt.append(p2)
		else:
			if dx > 0:
				self.opt.append(p4)
				if dy > 0:
					self.opt.append(p1)
					self.opt.append(p2)
				else:
					self.opt.append(p2)
					self.opt.append(p1)
				self.opt.append(p3)
			elif dx < 0:
				self.opt.append(p3)
				if dy > 0:
					self.opt.append(p1)
					self.opt.append(p2)
				else:
					self.opt.append(p2)
					self.opt.append(p1)
				self.opt.append(p4)
			else:
				if dy > 0:
					self.opt.append(p1)
					self.opt.append(p2)
				else:
					self.opt.append(p2)
					self.opt.append(p1)
				self.opt.append(p3)
				self.opt.append(p4)

class PlayerAI():

	def __init__(self):
		return

	def new_game(self, game_map, player_lightcycle, opponent_lightcycle): #INITIATES ON NEWGAME
		global location, Direction, Safe, Movelist, Circling, CircPos,iSafe
		position = player_lightcycle['position']
		Direction = player_lightcycle['direction']
		Safe = ['empty','powerup']
		iSafe = ['empty', 'powerup','trail']
		location = [0,0]
		location[0] = position[0]
		location[1] = position[1]
		Circling = []
		CircPos = []
		return

	def find_direction(self, map, node, target, i):
		flag = True
		if node.x == target[0] and node.y == target[1]:
			# works, return true
			node.active = True
			return True
		elif node.active == False:
			return False
		else:
			mindex = 0
			if node.c > 10:
				return node.opt[mindex].d
			node.find_target(map)
			opt = node.opt;
			for i in range(len(opt)):
				if not(self.dir_safe(map, [node.x, node.y], opt[i].d, i=i)):
					node.opt[i].active = False
					
			for l in node.opt:
				node.active = (flag or self.find_direction(map, l, target)) and len(node.opt)
			
			if node.active:
				mindex = 0
				for i in range(len(node.opt)):
					if node.opt[i].c < node.opt[mindex].c and node.opt[i].active:
						mindex = i
			
			return node.opt[mindex].d
		
	def get_move(self, game_map, player_lightcycle, opponent_lightcycle, moveNumber): # ACTUAL MOVE FUNCTION
		global location
		position = player_lightcycle['position']
		t = self.targeting(game_map, player_lightcycle, opponent_lightcycle)
		opp = t[0]
		node = Node(p=position, c=0, t=opp)
		dir = self.find_direction(game_map, node, opp, player_lightcycle['isInvincible'])
		directions = {};
		directions["up"] = PlayerActions.MOVE_UP
		directions["down"] = PlayerActions.MOVE_DOWN
		directions["left"] = PlayerActions.MOVE_LEFT
		directions["right"] = PlayerActions.MOVE_RIGHT
		if (self.dir_safe(game_map, position, dir, i=player_lightcycle['isInvincible'])):
			return directions[dir] + 5*t[1]
		if (self.dir_safe(game_map, position, 'up')):
			return PlayerActions.MOVE_UP 
		elif self.dir_safe(game_map, position, 'right'):
			return PlayerActions.MOVE_RIGHT
		elif self.dir_safe(game_map, position, 'down'):
			return PlayerActions.MOVE_DOWN
		elif self.dir_safe(game_map, position, 'left'):
			return PlayerActions.MOVE_LEFT
		else:
			#try:
			#	print(player_lightcycle.position)
			#except:
			#	print("Dead!")
			return PlayerActions.ACTIVATE_POWERUP

	def dir_safe(self, game_map, location, direction, counter=0, i=False):
		global Safe, Position, iSafe
		safe = Safe 
		locations ={}
		locations["up"] = location[0], location[1]-1
		locations["down"]= location[0], location[1]+1
		locations["left"] = location[0]-1, location[1]
		locations["right"] = location[0]+1, location[1]

		if counter < 12:
			if (direction == 'up'):
				A = game_map[location[0]][location[1]-1]
				return (A in safe) and (self.dir_safe(game_map, locations[direction], "left", counter+1) or self.dir_safe(game_map, locations[direction], "up", counter+1) or self.dir_safe(game_map, locations[direction], "right", counter+1))
			elif (direction == 'left'):
				A = game_map[location[0]-1][(location[1])]
				return (A in safe) and (self.dir_safe(game_map, locations[direction], "left",  counter+1) or self.dir_safe(game_map, locations[direction],"down", counter+1) or self.dir_safe(game_map, locations[direction], "up",counter+1))
			elif (direction == 'right'):
				A = game_map[location[0]+1][(location[1])]
				return (A in safe) and (self.dir_safe(game_map, locations[direction], "up",counter+1) or self.dir_safe(game_map, locations[direction], "right", counter+1) or self.dir_safe(game_map, locations[direction], "down", counter+1))
			elif (direction == 'down'):
				A = game_map[(location[0])][location[1]+1]	
				return (A in safe) and (self.dir_safe(game_map, locations[direction], "left", counter+1) or self.dir_safe(game_map, locations[direction], "right",counter+1) or self.dir_safe(game_map, locations[direction],"down", counter+1))
			#print(direction + ': ' + str(A))
		else:
			return True

	def circle(self, game_map, player_lightcycle, opponent_lightcycle, power):
		global Movelist, Circling, CircPos
		A = opponent_lightcycle['position']
		B = player_lightcycle['position']	
		
		encircle = 4
		circ = 5
		
		target = []
		target.append(A[0])
		target.append(A[1])
		powerup = 0
		if ((abs(A[0] - B[0]) > 4) or (abs(A[1] - B[0]) > 4)):
			
			D = opponent_lightcycle['direction']
			if (D == 0):
				target[1] -= circ
			elif (D == 1):
				target[0] += circ
			elif (D == 2):
				target[1] += circ
			elif (D == 3):
				target[0] -= circ
		elif (not Circling):
			CircPos.append(A[0])
			CircPos.append(A[1])
			if (A[0] > B[0]):
				target[0] += encircle
				Circling.append(0) # Going right
			else:
				target[0] -= encircle
				Circling.append(1)
		else:
			if (len(Circling) == 1):
				if (A[0] > B[0]):
					if (not Circling[0]):
						if (A[1] > B[1]):
							target[1] -= encircle
							Circling.append(0) # Going up
						else:
							target[1] += encircle
							Circling.append(1) # Going down
					else:
						target[0] += encircle
				else:
					if (Circling[0]):
						if (A[1] > B[1]):
							target[1] -= encircle
							Circling.append(0) # Going up
						else:
							target[1] += encircle
							Circling.append(1) # Going down
					else:
						target[0] -= encircle
			else:
				if (((not Circling[1]) and (A[1] > B[1])) or ((Circling[1]) and (A[1] < B[1]))):
					target = CircPos
				else:
					target.append(A[0])
					target.append(A[1])
					if (A[1] > B[1]):
						target[1] -= encircle
						Circling.append(0) # Going up
					else:
						target[1] += encircle
						Circling.append(1) # Going down
				if (power):
					E = player_lightcycle['direction']
					if (E == 0): # Note, this will trigger whenever it 'sees' a light trail
						powerup = (not self.dir_safe(game_map, B, 'up'))
					elif (E == 1):
						powerup = (not self.dir_safe(game_map, B, 'right'))
					elif (E == 2):
						powerup = (not self.dir_safe(game_map, B, 'down'))
					elif (E == 3):
						powerup = (not self.dir_safe(game_map, B, 'right'))
		
		return [target,powerup]

	def targeting(self, game_map, player_lightcycle, opponent_lightcycle):
		'''
		Hierarchy:
		Find powerup
		If invincibility, (and opponent doesn't have) then aim at opponent and try to encircle.
			Otherwise get opponent to use it up
		If bomb, save for a rainy day. Could attempt the invincibility method
		
		Targeting:
		During a regular run: Avoid tricky spaces, shield powerups, get nearby powerups, 
		'''
		global Movelist, Circling, CircPos
		
		escape = 3
		dead = 1
		A = (0,0)
		try:
			dead = 0
			A = opponent_lightcycle['position']
		except:
			dead = 1
		B = player_lightcycle['position']
		
		target = []
		if (not dead):
			if (player_lightcycle["isInvincible"]):
				# Gotta go fast! (Head away!)
				target.append(B[0])
				target.append(B[1])
				
				if (A[0] > len(game_map)//2):
					target[0] -= escape
					if (A[1] > len(game_map[0])//2):
						target[1] -= escape
					else:
						target[1] += escape
				else:
					target[0] += escape
					
				return [target,0]
						
			
			elif (player_lightcycle["hasPowerup"]):
				if ((player_lightcycle["powerupType"] == "INVINCIBILITY") or (player_lightcycle["powerupType"] == 'BOMB') or (player_lightcycle["powerupType"] == "LANDMINE")):
					# Target player and prep to encircle. Check to see if opponent has invincibility, or bomb, deal with it
					# Keep track of invincibility counter
					# Go to 4 in front of opposing player?
					return self.circle(game_map, player_lightcycle, opponent_lightcycle, 1)

			else:
				# Defensive
				Circling = []
				CircPos = []
				for row in range(len(game_map)):

					try:

						A = game_map[row].index('powerup')

						return [[A,row],0]
						
					except:
						continue
				return self.circle(game_map, player_lightcycle, opponent_lightcycle, 0)

		else:
			# Gather points. Head to powerups, blast through your own stuff if needed, head to the most space, and capitalize on it
			for row in range(len(game_map)):

				try:

					A = game_map[row].index('powerup')

					return [[A,row],0]
				except:
					continue
			
			# Add more stuff?

		return [[0,0],0]
		
'''

8888888 8888888888 8 888888888o.      ,o888888o.     b.             8 
      8 8888       8 8888    `88.  . 8888     `88.   888o.          8 
      8 8888       8 8888     `88 ,8 8888       `8b  Y88888o.       8 
      8 8888       8 8888     ,88 88 8888        `8b .`Y888888o.    8 
      8 8888       8 8888.   ,88' 88 8888         88 8o. `Y888888o. 8 
      8 8888       8 888888888P'  88 8888         88 8`Y8o. `Y88888o8 
      8 8888       8 8888`8b      88 8888        ,8P 8   `Y8o. `Y8888 
      8 8888       8 8888 `8b.    `8 8888       ,8P  8      `Y8o. `Y8 
      8 8888       8 8888   `8b.   ` 8888     ,88'   8         `Y8o.` 
      8 8888       8 8888     `88.    `8888888P'     8            `Yo
      
                                Quick Guide
                --------------------------------------------
                      Feel free to delete this comment.

        1. THIS IS THE ONLY .PY OR .BAT FILE YOU SHOULD EDIT THAT CAME FROM THE ZIPPED STARTER KIT

        2. Any external files should be accessible from this directory

        3. new_game is called once at the start of the game if you wish to initialize any values

        4. get_move is called for each turn the game goes on

        5. game_map is a 2-d array that contains values for every board position.
                example call: game_map[2][3] == POWERUP would evaluate to True if there was a powerup at (2, 3)

        6. player_lightcycle is your lightcycle and is what the turn you respond with will be applied to.
                It is a dictionary with corresponding keys: "position", "direction", "hasPowerup", "isInvincible", "powerupType"
                position is a 2-element int array representing the x, y value
                direction is the direction you are travelling in. can be compared with Direction.DIR where DIR is one of UP, RIGHT, DOWN, or LEFT
                hasPowerup is a boolean representing whether or not you have a powerup
                isInvincible is a boolean representing whether or not you are invincible
                powerupType is what, if any, powerup you have

        7. opponent_lightcycle is your opponent's lightcycle. Same keys and values as player_lightcycle

        8. You ultimately are required to return one of the following:
                                                PlayerAction.SAME_DIRECTION
                                                PlayerAction.MOVE_UP
                                                PlayerAction.MOVE_DOWN
                                                PlayerAction.MOVE_LEFT
                                                PlayerAction.MOVE_RIGHT
                                                PlayerAction.ACTIVATE_POWERUP
                                                PlayerAction.ACTIVATE_POWERUP_MOVE_UP
                                                PlayerAction.ACTIVATE_POWERUP_MOVE_DOWN
                                                PlayerAction.ACTIVATE_POWERUP_MOVE_LEFT
                                                PlayerAction.ACTIVATE_POWERUP_MOVE_RIGHT
                
        9. If you have any questions, contact challenge@orbis.com

        10. Good luck! Submissions are due Sunday, September 21 at noon. You can submit multiple times and your most recent submission will be the one graded.
 
'''
