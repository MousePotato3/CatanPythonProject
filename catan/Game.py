"""
The base class for the Settlers of Catan board game. Creates an instance of each player
and the Settlers of Catan board,and calls each player's methods for taking its turn.
Does not have access to each player's hidden resources and development cards.

Created on Sep 2, 2022

@author: Andrew Hubbard
"""
from catan import Board
from catan import RandComp

class Game:
    def __init__(self):
        """ Initialize the variables for the Game class and call each player's constructor """
        self.players = []
        self.numPlayers = 4
        self.maxResources = 7
        self.pointsToWin = 10
        self.playerToMove = 1
        self.board = Board.Board(self.numPlayers)
        self.players.append(RandComp.RandComp(1, "red", "RandComp", self.numPlayers))
        self.players.append(RandComp.RandComp(2, "blue", "RandComp", self.numPlayers))
        self.players.append(RandComp.RandComp(3, "white", "RandComp", self.numPlayers))
        self.players.append(RandComp.RandComp(4, "orange", "RandComp", self.numPlayers))
        self.playerColors = ["red", "blue", "white", "orange"]

        """ Call the methods to set up the Settlers of Catan board """
        print("Shuffling and placing Catan tiles and ports")
        self.board.initTiles()
        self.board.initPorts()
        print("Finished setting up the board")

    """ Alternate turns between each player until some player wins, and then print the winner """
    def play(self):
        self.initPlacement()
        while self.board.winner == -1:
            self.takeTurn()
        print("Player", self.board.winner, "won with", self.players[self.board.winner - 1].score,
              "points at the end of turn", self.board.turnNumber, "!")

    """
    Place initial settlements and roads for each player and print the location of each settlement and 
    road chosen. Also print a message for any ports acquired by players in the initial settlement phase.
    """
    def initPlacement(self):
        """ Player 1 chooses its first settlement first """
        for i in range(self.numPlayers):
            playerToMove = i + 1
            settleLocation = self.players[i].chooseInitialSettlementLocation(self.board)
            self.board.addSettlement(settleLocation, self.playerColors[i], playerToMove, True)
            self.players[playerToMove - 1].updateResourcePoints(settleLocation)
            self.players[playerToMove - 1].score += 1
            print("Player", playerToMove, "placed its first settlement at",
                  int(settleLocation.x), int(settleLocation.y))
            newPortType = self.board.getPortType(settleLocation)
            if newPortType != "":
                self.players[i].gainPortPower(newPortType)
                print("Player", playerToMove, "just acquired a", newPortType, "port!")

            roadLocation = self.players[i].chooseInitialRoadLocation(settleLocation)
            self.board.addRoad(settleLocation, roadLocation, self.playerColors[i], playerToMove, True)
            print("Player", playerToMove, "placed its first road between", int(settleLocation.x),
                  int(settleLocation.y), "and", int(roadLocation.x), int(roadLocation.y))

        """ Player 1 chooses its second settlement last """
        """ Each player gains resources based on the tiles adjacent to their second settlement """
        for i in range(self.numPlayers):
            j = self.numPlayers - i - 1
            playerToMove = j + 1
            settleLocation = self.players[j].chooseInitialSettlementLocation(self.board)
            self.board.addSettlement(settleLocation, self.playerColors[i], playerToMove, True)
            self.players[playerToMove - 1].updateResourcePoints(settleLocation)
            self.players[playerToMove - 1].score += 1
            print("Player", playerToMove, "placed its second settlement at",
                  int(settleLocation.x), int(settleLocation.y))
            newPortType = self.board.getPortType(settleLocation)
            if newPortType != "":
                self.players[j].gainPortPower(newPortType)
                print("Player", playerToMove, "just acquired a", newPortType, "port!")

            """ Collect resources based on tiles adjacent to the player's second settlement """
            neighbors = self.board.getAdjacentHexes(settleLocation)
            for k in range(len(neighbors)):
                self.players[j].addResource(neighbors[k].hexType)

            roadLocation = self.players[j].chooseInitialRoadLocation(settleLocation)
            self.board.addRoad(settleLocation, roadLocation, self.playerColors[i], playerToMove, True)
            print("Player", playerToMove, "placed its second road between", int(settleLocation.x),
                  int(settleLocation.y), "and", int(roadLocation.x), int(roadLocation.y))

    def collectResources(self):
        """  Eventually players should have an option to play knight cards before rolling dice """
        diceRoll = self.board.rollDice()
        if diceRoll == 7:
            """
            Players with more than a certain number of resources (usually half of their hand) 
            discard half of their resources, rounded down, as specified in their player class
            """
            for i in range(self.numPlayers):
                if self.players[i].getTotalResources() > self.maxResources:
                    self.players[i].discard()

            """ The player whose turn it is moves the robber and steals from another player """
            playerToRob = self.players[self.playerToMove - 1].getPlayerToRob()
            self.board.robberLocation = self.players[self.playerToMove - 1].getPointToBlock(playerToRob)
            resourceNum = self.players[playerToRob - 1].getRandomResource()
            if resourceNum != -1:
                self.players[self.playerToMove - 1].gainResource(resourceNum)
                self.players[playerToRob - 1].loseResource(resourceNum)

        else:
            """
            Each player with a settlement or city next to a resource tile with a number 
            matching the dice roll gains resources: 1 for a settlement, or 2 for a city.
            These resources are not collected by the player if the tile is blocked by the robber.
            """
            for i in range(self.numPlayers):
                for j in range(len(self.board.settlements[i])):
                    neighbors = self.board.getAdjacentHexes(self.board.settlements[i][j].location)
                    for k in range(len(neighbors)):
                        if neighbors[k].number == diceRoll and neighbors[k].location != self.board.robberLocation:
                            self.players[i].addResource(neighbors[k].hexType)

                for j in range(len(self.board.cities[i])):
                    neighbors = self.board.getAdjacentHexes(self.board.cities[i][j].location)
                    for k in range(len(neighbors)):
                        if neighbors[k].number == diceRoll and neighbors[k].location != self.board.robberLocation:
                            self.players[i].addResource(neighbors[k].hexType)
                            self.players[i].addResource(neighbors[k].hexType)

    def takeTurn(self):
        """ Roll the dice, collect resources, and take the current player's turn """
        self.collectResources()
        self.board = self.players[self.playerToMove - 1].takeTurn(self.board)

        """ Check to see if the player won, and if so, update the winner """
        if self.players[self.playerToMove - 1].score >= self.pointsToWin:
            self.board.winner = self.playerToMove

        """ Advance to the next player's turn """
        if self.playerToMove == self.numPlayers:
            self.playerToMove = 1
            self.board.turnNumber += 1
        else:
            self.playerToMove += 1
