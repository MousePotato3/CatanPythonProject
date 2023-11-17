'''
Stores a copy of the player's game board which is passed back to the Game class
after any changes are made. Also keeps track of player resource types, player
development cards, and the number of points this player has (including hidden
development cards). If the player wins the game, the turn ends and the player
returns this information to the game class.

Includes abstract methods that the class for each player type must override.

Created on Dec 1, 2022

@author: Andrew Hubbard
'''
from abc import ABC, abstractmethod
from catan import Board
from random import randrange


class Player(ABC):
    ''' Abstract class to hold each player in the Settlers of Catan game '''

    ''' Initialize all of the data that the player class will use '''

    def __init__(self, playerNum, color, playerType, numPlayers):
        self.playerNum = playerNum
        self.color = color
        self.playerType = playerType
        self.numPlayers = numPlayers
        self.currentBoard = Board.Board(numPlayers)
        self.resources = [0, 0, 0, 0, 0]
        self.tradeRates = [4, 4, 4, 4, 4]
        self.tempTradeRates = [4, 4, 4, 4, 4]
        ''' Keeps track of the number of probability "dots" the player has on each resource '''
        self.resourcePoints = [0, 0, 0, 0, 0]
        ''' Player will need to keep track of its own score because of hidden victory point cards '''
        self.score = 0

    ''' Add a resource by index for the player, and add 1 to the player's number of resources '''

    def gainResource(self, resourceIndex):
        if (resourceIndex >= 0 and resourceIndex <= 4):
            self.resources[resourceIndex] += 1
            self.currentBoard.numResources[self.playerNum - 1] += 1
        else:
            print("ERROR: Player", self.playerNum, "tried to collect resource number",
                  resourceIndex, "which is not a valid resource")

    ''' Remove a resource by index for the player, and subtract 1 from the player's number of resources '''

    def loseResource(self, resourceIndex):
        if (resourceIndex >= 0 and resourceIndex <= 4):
            self.resources[resourceIndex] -= 1
            self.currentBoard.numResources[self.playerNum - 1] -= 1
        else:
            print("ERROR: Player", self.playerNum, "tried to discard resource number",
                  resourceIndex, "which is not a valid resource")

    ''' Return the text corresponding to a resource index '''

    def getResourceType(self, resourceIndex):
        match (resourceIndex):
            case 0:
                return "ore"
            case 1:
                return "wheat"
            case 2:
                return "sheep"
            case 3:
                return "brick"
            case 4:
                return "wood"
            case _:
                return ""

    ''' Return the index corresponding to a resource text '''

    def getResourceIndex(self, resourceType):
        match (resourceType):
            case "ore":
                return 0
            case "wheat":
                return 1
            case "sheep":
                return 2
            case "brick":
                return 3
            case "wood":
                return 4
            case _:
                return -1

    ''' Add a resource by text for the player, and add 1 to the player's number of resources '''

    def addResource(self, resourceType):
        if (self.getResourceIndex(resourceType) != -1):
            self.gainResource(self.getResourceIndex(resourceType))

    ''' Trade a resource for another resource with the bank '''

    def portResource(self, oldResource, newResource):
        if (oldResource < 0 or oldResource > 4):
            print("ERROR: Player", self.playerNum, "tried to port away resource number",
                  oldResource, "which is not a valid resource")
        elif (newResource < 0 or newResource > 4):
            print("ERROR: Player", self.playerNum, "tried to port for resource number",
                  newResource, "which is not a valid resource")
        elif (self.resources[oldResource] < self.tradeRates[oldResource]):
            ''' Print an error message indicating an invalid attempt to trade resources '''
            if (self.tradeRates[oldResource] < 4):
                print("ERROR: Player", self.playerNum, "tried to trade", oldResource.getResourceType(),
                      "using a port. This player has", self.resources[oldResource], "and needs at least",
                      self.tradeRates[oldResource], "to make this trade.")
            else:
                print("ERROR: Player", self.playerNum, "tried to trade", oldResource.getResourceType(),
                      "with the bank. This player has", self.resources[oldResource], "and needs at least",
                      self.tradeRates[oldResource], "to make this trade.")
        else:
            ''' Trade the old resource of the player for the new resource '''
            self.resources[newResource] += 1
            self.resources[oldResource] -= self.tradeRates[oldResource]

            ''' Print a message indicating which resources where traded and whether a port was used '''
            if (self.tradeRates[oldResource] < 4):
                print("Player", self.playerNum, "just traded", self.tradeRates[oldResource],
                      self.getResourceType(oldResource), "for 1",
                      self.getResourceType(newResource), "using a port")
            else:
                print("Player", self.playerNum, "just traded", self.tradeRates[oldResource],
                      self.getResourceType(oldResource), "for 1",
                      self.getResourceType(newResource), "from the bank")

    ''' Count the total number of resources owned by a player '''

    def getTotalResources(self):
        totalResources = 0
        for i in range(len(self.resources)):
            totalResources += self.resources[i]
        return totalResources

    ''' Update the player's resource access based on a new settlement or city '''

    def updateResourcePoints(self, location):
        adjacentHexes = self.currentBoard.getAdjacentHexes(location)
        for i in range(len(adjacentHexes)):
            resourceIndex = self.getResourceIndex(adjacentHexes[i].hexType)
            self.resourcePoints[resourceIndex] += adjacentHexes[i].value

    ''' Adjust the trade rates of the player based on a newly acquired port '''

    def gainPortPower(self, portType):
        match (portType):
            case "general":
                for i in range(len(self.tradeRates)):
                    if (self.tradeRates[i] == 4):
                        self.tradeRates[i] = 3
            case "ore":
                self.tradeRates[0] = 2
            case "wheat":
                self.tradeRates[1] = 2
            case "sheep":
                self.tradeRates[2] = 2
            case "brick":
                self.tradeRates[3] = 2
            case "wood":
                self.tradeRates[4] = 2
            case _:
                print("ERROR: Invalid port power gained by player", self.playerNum)

    ''' Temporarily adjust the trade rates of the player based on a port location being considered '''

    def tempGainPortPower(self, portType):
        match (portType):
            case "general":
                for i in range(len(self.tempTradeRates)):
                    if (self.tempTradeRates[i] == 4):
                        self.tempTradeRates[i] = 3
            case "ore":
                self.tempTradeRates[0] = 2
            case "wheat":
                self.tempTradeRates[1] = 2
            case "sheep":
                self.tempTradeRates[2] = 2
            case "brick":
                self.tempTradeRates[3] = 2
            case "wood":
                self.tempTradeRates[4] = 2
            case _:
                print("ERROR: Invalid port power gained by player", self.playerNum)

    ''' Choose a random resource to be stolen or discarded '''

    def getRandomResource(self):
        total = self.getTotalResources()
        if (total > 0):
            resourceNum = randrange(total)
        else:
            return -1

        if (0 <= resourceNum and resourceNum < self.resources[0]):
            return 0
        elif (resourceNum < self.resources[0] + self.resources[1]):
            return 1
        elif (resourceNum < self.resources[0] + self.resources[1] + self.resources[2]):
            return 2
        elif (resourceNum < self.resources[0] + self.resources[1] + self.resources[2] + self.resources[3]):
            return 3
        elif (resourceNum < total):
            return 4
        else:
            print("ERROR: Invalid attempt to choose resource", resourceNum, "out of", total, "resources")
            return -1

    ''' Print the player's current resources to the screen '''

    def printResources(self):
        print("Player", self.playerNum, "has", self.score, "points, and", self.resources[0], "ore,", self.resources[1],
              "wheat,", self.resources[2], "sheep,", self.resources[3], "brick, and", self.resources[4], "wood")

    @abstractmethod
    def getPlayerToRob(self):
        pass

    @abstractmethod
    def getPointToBlock(self, playerToRob):
        pass

    @abstractmethod
    def chooseInitialSettlementLocation(self, board):
        pass

    @abstractmethod
    def chooseInitialRoadLocation(self, settleLocation):
        pass

    @abstractmethod
    def discard(self):
        pass

    @abstractmethod
    def takeTurn(self, currentBoard):
        pass
