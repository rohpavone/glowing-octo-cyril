from SocketChannel import SocketChannel, SocketChannelFactory
from TronProtocol_pb2 import *
from Enums import *
import sys
import datetime
import traceback
import logging
import os
from time import sleep
import time

class TronClient():

	channel=None
	game_map=None
	def __init__(self):
		self.channelFactory = SocketChannelFactory()

	def validateMessage(self, protobufMsg):
	  '''
	  Check the protobuf message
	  '''
	  if not protobufMsg.IsInitialized():
	    raise Exception("Message is missing required fields")

	# lists of lists which contains string of item on map
	def get_map_list(self, mapMessage, size):
          if self.game_map == None:
                self.game_map = [range(size.y) for x in range(size.x)]
          for mapentry in mapMessage:
                  self.game_map[mapentry.pos.x][mapentry.pos.y] = mapentry.mapItem
          return self.game_map

        def powerup_int_to_string(self, powerup_type):
            if powerup_type == 0:
                    return "INVINCIBILITY"
            elif powerup_type == 1:
                    return "BOMB"
            elif powerup_type == 2:
                    return "SPEED"
            elif powerup_type == 3:
                    return "LANDMINE"
            elif powerup_type == 4:
                    return "BONUSPOINTS"
            return
        
	def get_players(self, protobuf_players):
                players = {}
		for player in protobuf_players:
                    
                    if player.hasPowerup:
                            players[player.playerNumber] = {
                            'position':(player.pos.x, player.pos.y), 
                            'direction':player.dir, 
                            'playerNumber':player.playerNumber, 
                            'hasPowerup':True, 
                            'powerupType':self.powerup_int_to_string(player.powerUpType),
                            'isInvincible': player.activePowerup}
                    else:
                            players[player.playerNumber] = {
                            'position':(player.pos.x, player.pos.y), 
                            'direction':player.dir, 
                            'playerNumber':player.playerNumber, 
                            'hasPowerup':False,
                            'powerupType':"NONE",
                            'isInvincible':player.activePowerup}
		return players

	def runClient(self, ai, host="localhost", port=19999, playername="TronPlayr3000"):

		self.ai = ai
		if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
		  os.mkdir(os.path.join(os.getcwd(), 'logs'))
		logging.basicConfig(filename='logs/AI-{0}.log'.format(playername), level=logging.DEBUG)
		
		try:
		  self.channel = self.channelFactory.openChannel(host, port)
		except Exception as e: 
		  logging.exception("Unexcpected error when opening channel: ")
		  return
		teamNameMessage = ClientWrapperMessage()
		teamNameMessage.messageType = NAME_RESPONSE
		teamNameMessage.name = playername
		
		self.channel.write(teamNameMessage.SerializeToString())
		while self.channel.connected:
                        # throttle reading as to not overwhelm protobuf
			sleep(0.05)
			msg = TronMessage()
			try:
				read_data = self.channel.read()
			except Exception as e:
				self.channel.close()
				return
			msg.ParseFromString(read_data)
			self.validateMessage(msg)
			if msg.messageType == END_GAME:
				print 'End game message received. Closing connection'
				self.channel.close()
				return

			if msg.messageType == START_GAME:
				try:
					logging.info("=============STARTING A NEW GAME=============")
					gmap = self.get_map_list(msg.item, msg.mapSize)
					players = self.get_players(msg.players)
					if msg.playerNum == 0:
                                                self.ai.new_game(gmap, players[0], players[1])
                                        else:
                                                self.ai.new_game(gmap, players[1], players[0])
				except:
					logging.exception("Uh-oh")
				continue
			
			if msg.messageType == MOVE_REQUEST:
				starttime = datetime.datetime.now()
				map_info = self.get_map_list(msg.item, msg.mapSize)
				players = self.get_players(msg.players)

				try:
					logging.info("{0} calling getMove for turn {1} for player {2}".format(time.strftime("%d/%m/%Y %H:%M:%S"), msg.responseID, msg.playerNum))
					if msg.playerNum == 0:
                                                move = ai.get_move(map_info, players[0], players[1], msg.responseID)
                                        else:
                                                move = ai.get_move(map_info, players[1], players[0], msg.responseID)
				
				except Exception as e:
                                        print "\nERROR FROM PLAYER: " + playername
					print e
					print "\n"
					logging.exception("{0} Unexpected error during turn {1}:".format(time.strftime("%d/%m/%Y %H:%M:%S"), msg.responseID))
					move = SAME_DIRECTION
					logging.info("{0} writing response back for turn {1} for player {2}".format(time.strftime("%d/%m/%Y %H:%M:%S"), msg.responseID, msg.playerNum))
				wrapperMessage = ClientWrapperMessage()
				wrapperMessage.messageType = MOVE_RESPONSE			
				wrapperMessage.moveResponse.PlayerID = msg.playerID
				wrapperMessage.moveResponse.playerNum = msg.playerNum
                                wrapperMessage.moveResponse.response.move = move			
				wrapperMessage.moveResponse.responseID = msg.responseID
				
				self.channel.write(wrapperMessage.SerializeToString())
				diff = datetime.datetime.now() - starttime
				logging.info("{0} message sent for move {1}: took {2} milliseconds".format(time.strftime("%d/%m/%Y %H:%M:%S"), msg.responseID, diff.microseconds/1000))
				continue
                        if msg.messageType == NAME_REQUEST:
                                teamNameMessage = ClientWrapperMessage()
                                teamNameMessage.messageType = NAME_RESPONSE
                                teamNameMessage.name = playername
                                self.channel.write(teamNameMessage.SerializeToString())

			

		self.channel.close()
