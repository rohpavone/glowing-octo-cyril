EMPTY = 'empty'
LIGHTCYCLE = 'lightCycle'
WALL = 'wall'
TRAIL = 'trail'
POWERUP = 'powerup'

class PlayerActions: SAME_DIRECTION, MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT,  ACTIVATE_POWERUP, ACTIVATE_POWERUP_MOVE_UP, ACTIVATE_POWERUP_MOVE_DOWN, ACTIVATE_POWERUP_MOVE_LEFT, ACTIVATE_POWERUP_MOVE_RIGHT = range (10)


class Direction: 
	UP, RIGHT, DOWN, LEFT = range(4)
	@classmethod
	def to_string(cls, val):
		for k,v in vars(cls).iteritems():
			if v == val:
				return k


