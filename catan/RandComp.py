"""
An instance of the abstract Player class that makes many of its decisions
with limited intelligence by randomly choosing one of several possible moves

Created on Dec 1, 2022

@author: Andrew Hubbard
"""
from catan.Player import Player
from random import randrange

class RandComp(Player):
    def __init__(self, playerNum, color, playerType, numPlayers):
        super().__init__(playerNum, color, playerType, numPlayers)

    """
    Calculate the expected value of a possible settlement or city location, based on
    total and variety of resources and available ports (including newly acquired ports)
    """
    def getHexValue(self, location):
        tempResourcePoints = [0, 0, 0, 0, 0]
        hexValue = 0
        for i in range(len(self.resourcePoints)):
            tempResourcePoints[i] = self.resourcePoints[i]
            self.tempTradeRates[i] = self.tradeRates[i]
        adjacentHexes = self.currentBoard.getAdjacentHexes(location)
        for j in range(len(adjacentHexes)):
            resourceIndex = self.getResourceIndex(adjacentHexes[j].hexType)
            tempResourcePoints[resourceIndex] += adjacentHexes[j].value
            newPortType = self.currentBoard.getPortType(location)
            if newPortType != "":
                self.tempGainPortPower(newPortType)
        for k in range(len(tempResourcePoints)):
            hexValue += 4.0 * (
                        tempResourcePoints[k] / self.tempTradeRates[k] - self.resourcePoints[k] / self.tradeRates[k])
        self.tempTradeRates = [4, 4, 4, 4, 4]
        return hexValue

    """ 
    Choose the best possible settlement location based on resource 
    probability, resource diversity, access to ports, and a random factor
    """
    def chooseInitialSettlementLocation(self, board):
        self.currentBoard = board
        maxValue = -1
        maxIndex = -1

        for i in range(len(self.currentBoard.hexIntersections)):
            if self.currentBoard.legalPlacement(self.currentBoard.hexIntersections[i]):
                random = randrange(20) / 10.0
                hexValue = self.getHexValue(self.currentBoard.hexIntersections[i]) + random
                if hexValue > maxValue:
                    maxValue = hexValue
                    maxIndex = i

        return self.currentBoard.hexIntersections[maxIndex]

    """
    Create a list of every intersection that a road can connect to the initial 
    settlement location, and choose an intersection from the list at random
    """
    def chooseInitialRoadLocation(self, settleLocation):
        possibleRoadPoints = self.currentBoard.getAdjacentIntersections(settleLocation)
        roadPointIndex = randrange(len(possibleRoadPoints))
        return possibleRoadPoints[roadPointIndex]

    """ Discard resources from the player at random """
    def discard(self):
        numDiscardResources = int(self.getTotalResources() / 2)

        for _ in range(numDiscardResources):
            resourceType = self.getRandomResource()
            if resourceType != -1:
                self.resources[resourceType] -= 1
            else:
                print("ERROR: Player", self.playerNum, "discarded resources incorrectly")

        self.currentBoard.numResources[self.playerNum - 1] -= numDiscardResources

    """
    Generate a random number between 0 and 2 and add it to each player's score, 
    to somewhat randomly choose a player who is close to the lead to rob from.
    Only choose a player that has a resource to steal, if possible.
    """
    def getPlayerToRob(self):
        maxPoints = 0.0
        playerToRob = -1
        cannotRob = 1

        """ Determine whether any player has a resource to steal """
        for i in range(len(self.currentBoard.numResources)):
            if i != (self.playerNum - 1) and self.currentBoard.numResources[i] > 0:
                cannotRob = 0

        """ Select a player to rob randomly who is leading or close to the lead """
        for i in range(len(self.currentBoard.playerScores)):
            random = randrange(20) / 10.0
            if (((cannotRob == 0 and self.currentBoard.numResources[i] > 0) or cannotRob == 1)
                    and i != (self.playerNum - 1) and self.currentBoard.playerScores[i] + random > maxPoints):
                maxPoints = self.currentBoard.playerScores[i] + random
                playerToRob = i + 1
        return playerToRob

    """ Identify the best location to block to slow down the progress of the player being robbed """
    def getPointToBlock(self, playerToRob):
        possibleBlockLocations = []
        """ Create a list of possible locations from which to block playerToRob """
        for i in range(len(self.currentBoard.settlements)):
            if len(self.currentBoard.settlements[i]) > 0:
                for j in range(len(self.currentBoard.settlements[i])):
                    if self.currentBoard.settlements[i][j].playerNum != playerToRob:
                        continue
                    neighbors = (self.currentBoard.getAdjacentHexes(self.currentBoard.settlements[i][j].location))
                    for k in range(len(neighbors)):
                        possibleBlockLocations.append(neighbors[k])

        for i in range(len(self.currentBoard.cities)):
            if len(self.currentBoard.cities[i]) > 0:
                for j in range(len(self.currentBoard.cities[i])):
                    if self.currentBoard.cities[i][j].playerNum != playerToRob:
                        continue
                    neighbors = (self.currentBoard.getAdjacentHexes(self.currentBoard.cities[i][j].location))
                    for k in range(len(neighbors)):
                        possibleBlockLocations.append(neighbors[k])

        """ Remove duplicates by converting to a Python set and back to a list """
        possibleBlockLocations = [*set(possibleBlockLocations)]

        maxValue = -100
        maxIndices = []

        """
        Assign a significant negative value if we are blocking ourselves. 
        Otherwise the value of a location to block is sum(playerPoints)*hexValue, 
        where playerPoints count double for a city compared to a settlement.
        """
        for i in range(len(possibleBlockLocations)):
            hexValue = 0
            checkPoints = self.currentBoard.getAdjacentIntersections(possibleBlockLocations[i].location)
            for j in range(len(checkPoints)):
                mySettlementIndex = self.currentBoard.findSettlementIndex(checkPoints[j], self.playerNum)
                myCityIndex = self.currentBoard.findCityIndex(checkPoints[j], self.playerNum)
                anySettlementIndex = self.currentBoard.findSettlementIndex(checkPoints[j], -1)
                anyCityIndex = self.currentBoard.findCityIndex(checkPoints[j], -1)

                """ 
                If a settlement is found and the player doesn't own the settlement, increase 
                the value of blocking the hexagon by the player's score. If the player does 
                own the settlement, decrease the value by 20 (to discourage a self-block)
                """
                if anySettlementIndex != -1:
                    if mySettlementIndex == -1:
                        hexValue += self.currentBoard.playerScores[self.playerNum - 1]
                    else:
                        hexValue -= 20

                """ 
                If a city is found and the player doesn't own the city, increase the value 
                of blocking the hexagon by twice the player's score. If the player does 
                own the city, decrease the value by 40 (to discourage a self-block)
                """
                if anyCityIndex != -1:
                    if myCityIndex == -1:
                        hexValue += (self.currentBoard.playerScores[self.playerNum - 1] * 2)
                    else:
                        hexValue -= 40

            hexValue *= possibleBlockLocations[i].value

            if hexValue > maxValue:
                maxValue = hexValue
                maxIndices = [i]
            elif hexValue == maxValue:
                maxIndices.append(i)

        """ Choose one of the best possible locations to block randomly """
        randomIndex = randrange(len(maxIndices))

        return possibleBlockLocations[maxIndices[randomIndex]].location

    """ Return a list of resources to trade to the bank in order to build a city """
    def cityPortResources(self, cityPoints):
        resourcesToTrade = []

        """ Create a copy of the player's current resources """
        tempResources = []
        for i in range(len(self.resources)):
            tempResources.append(self.resources[i])

        maxRemainingResources = 0
        """
        Return an empty list if the player already has the maximum number of cities, 
        or if there are no locations available for the player to build a city
        """
        if len(cityPoints) == 0 or len(self.currentBoard.cities[self.playerNum - 1]) >= 4:
            return []
        else:
            """
            Keep trying to trade resources to the bank via port until a city can be built.
            Store the resources that are traded to the bank in a list.
            """
            while maxRemainingResources >= 0:
                if tempResources[0] >= 3 and tempResources[1] >= 2:
                    return resourcesToTrade
                maxIndex = 0

                """ Consider trading ore to the bank to build a city """
                maxRemainingResources = tempResources[0] - 3 - self.tradeRates[0]

                """ Consider trading wheat to the bank to build a city """
                if ((tempResources[1] - 2 - self.tradeRates[1] > maxRemainingResources)
                        or (tempResources[1] - 2 - self.tradeRates[1] == maxRemainingResources
                            and self.tradeRates[1] >= self.tradeRates[maxIndex])):
                    maxIndex = 1
                    maxRemainingResources = tempResources[1] - 2 - self.tradeRates[1]

                """ Consider trading sheep to the bank to build a city """
                if ((tempResources[2] - self.tradeRates[2] > maxRemainingResources)
                        or (tempResources[2] - self.tradeRates[2] == maxRemainingResources
                            and self.tradeRates[2] >= self.tradeRates[maxIndex])):
                    maxIndex = 2
                    maxRemainingResources = tempResources[2] - self.tradeRates[2]

                """ Consider trading brick to the bank to build a city """
                if ((tempResources[3] - self.tradeRates[3] > maxRemainingResources)
                        or (tempResources[3] - self.tradeRates[3] == maxRemainingResources
                            and self.tradeRates[3] >= self.tradeRates[maxIndex])):
                    maxIndex = 3
                    maxRemainingResources = tempResources[3] - self.tradeRates[3]

                """ Consider trading wood to the bank to build a city """
                if ((tempResources[4] - self.tradeRates[4] > maxRemainingResources)
                        or (tempResources[4] - self.tradeRates[4] == maxRemainingResources
                            and self.tradeRates[4] >= self.tradeRates[maxIndex])):
                    maxIndex = 4
                    maxRemainingResources = tempResources[4] - self.tradeRates[4]

                """
                Within the player's temporary resources, port the resource chosen to the 
                bank to get a resource needed to build a city. Add the ported resource to 
                the list of resources that need to be ported to the bank to build a city.
                """
                if maxRemainingResources >= 0:
                    if tempResources[0] < 3:
                        tempResources[0] += 1
                    elif tempResources[1] < 2:
                        tempResources[1] += 1
                    else:
                        print("ERROR: Invalid attempt to trade resources to build a city")
                    resourcesToTrade.append(maxIndex)
                    tempResources[maxIndex] -= self.tradeRates[maxIndex]

            """ Can't build a city; return an empty list """
            return []

    """ Return a list of resources to trade to the bank in order to build a settlement """
    def settlementPortResources(self, settlementPoints):
        resourcesToTrade = []

        """ Create a copy of the player's current resources """
        tempResources = []
        for i in range(len(self.resources)):
            tempResources.append(self.resources[i])

        maxRemainingResources = 0
        """
        Return a blank list if the player already has the maximum number of settlements, 
        or if there are no locations available for the player to build a settlement
        """
        if len(settlementPoints) == 0 or len(self.currentBoard.settlements[self.playerNum - 1]) >= 5:
            return []
        else:
            """
            Keep trying to trade resources to the bank via port until a settlement can be built.
            Store the resources that are traded to the bank in a list.
            """
            while maxRemainingResources >= 0:
                if tempResources[1] > 0 and tempResources[2] > 0 and tempResources[3] > 0 and tempResources[4] > 0:
                    return resourcesToTrade
                maxIndex = 0

                """ Consider trading ore to the bank to build a settlement """
                maxRemainingResources = tempResources[0] - self.tradeRates[0]

                """ Consider trading wheat to the bank to build a settlement """
                if ((tempResources[1] - 1 - self.tradeRates[1] > maxRemainingResources)
                        or (tempResources[1] - 1 - self.tradeRates[1] == maxRemainingResources
                            and self.tradeRates[1] >= self.tradeRates[maxIndex])):
                    maxIndex = 1
                    maxRemainingResources = tempResources[1] - 1 - self.tradeRates[1]

                """ Consider trading sheep to the bank to build a settlement """
                if ((tempResources[2] - 1 - self.tradeRates[2] > maxRemainingResources)
                        or (tempResources[2] - 1 - self.tradeRates[2] == maxRemainingResources
                            and self.tradeRates[2] >= self.tradeRates[maxIndex])):
                    maxIndex = 2
                    maxRemainingResources = tempResources[2] - 1 - self.tradeRates[2]

                """ Consider trading brick to the bank to build a settlement """
                if ((tempResources[3] - 1 - self.tradeRates[3] > maxRemainingResources)
                        or (tempResources[3] - 1 - self.tradeRates[3] == maxRemainingResources
                            and self.tradeRates[3] >= self.tradeRates[maxIndex])):
                    maxIndex = 3
                    maxRemainingResources = tempResources[3] - 1 - self.tradeRates[3]

                """ Consider trading wood to the bank to build a settlement """
                if ((tempResources[4] - 1 - self.tradeRates[4] > maxRemainingResources)
                        or (tempResources[4] - 1 - self.tradeRates[4] == maxRemainingResources
                            and self.tradeRates[4] >= self.tradeRates[maxIndex])):
                    maxIndex = 4
                    maxRemainingResources = tempResources[4] - 1 - self.tradeRates[4]

                """
                Within the player's temporary resources, port the resource chosen to the 
                bank to get a resource needed to build a settlement. Add the ported resource to 
                the list of resources that need to be ported to the bank to build a settlement.
                """
                if maxRemainingResources >= 0:
                    if tempResources[1] < 1:
                        tempResources[1] += 1
                    elif tempResources[2] < 1:
                        tempResources[2] += 1
                    elif tempResources[3] < 1:
                        tempResources[3] += 1
                    elif tempResources[4] < 1:
                        tempResources[4] += 1
                    else:
                        print("ERROR: Invalid attempt to trade resources to build a settlement")
                    resourcesToTrade.append(maxIndex)
                    tempResources[maxIndex] -= self.tradeRates[maxIndex]

            """ Can't build a settlement; return an empty list """
            return []

    """ Return a list of resources to trade to the bank in order to build a road """
    def roadPortResources(self, roadPoints):
        resourcesToTrade = []

        """ Create a copy of the player's current resources """
        tempResources = []
        for i in range(len(self.resources)):
            tempResources.append(self.resources[i])

        maxRemainingResources = 0
        """
        Return a blank list if the player already has the maximum number of cities, 
        or if there are no locations available for the player to build a city
        """
        if len(roadPoints) == 0 or len(self.currentBoard.roads[self.playerNum - 1]) >= 15:
            return []
        else:
            """
            Keep trying to trade resources to the bank via port until a road can be built.
            Store the resources that are traded to the bank in a list.
            """
            while maxRemainingResources >= 0:
                if tempResources[3] > 0 and tempResources[4] > 0:
                    return resourcesToTrade
                maxIndex = 0

                """ Consider trading ore to the bank to build a road """
                maxRemainingResources = tempResources[0] - self.tradeRates[0]

                """ Consider trading wheat to the bank to build a road """
                if ((tempResources[1] - self.tradeRates[1] > maxRemainingResources)
                        or (tempResources[1] - self.tradeRates[1] == maxRemainingResources
                            and self.tradeRates[1] >= self.tradeRates[maxIndex])):
                    maxIndex = 1
                    maxRemainingResources = tempResources[1] - self.tradeRates[1]

                """ Consider trading sheep to the bank to build a road """
                if ((tempResources[2] - self.tradeRates[2] > maxRemainingResources)
                        or (tempResources[2] - self.tradeRates[2] == maxRemainingResources
                            and self.tradeRates[2] >= self.tradeRates[maxIndex])):
                    maxIndex = 2
                    maxRemainingResources = tempResources[2] - self.tradeRates[2]

                """ Consider trading brick to the bank to build a road """
                if ((tempResources[3] - 1 - self.tradeRates[3] > maxRemainingResources)
                        or (tempResources[3] - 1 - self.tradeRates[3] == maxRemainingResources
                            and self.tradeRates[3] >= self.tradeRates[maxIndex])):
                    maxIndex = 3
                    maxRemainingResources = tempResources[3] - 1 - self.tradeRates[3]

                """ Consider trading wood to the bank to build a road """
                if ((tempResources[4] - 1 - self.tradeRates[4] > maxRemainingResources)
                        or (tempResources[4] - 1 - self.tradeRates[4] == maxRemainingResources
                            and self.tradeRates[4] >= self.tradeRates[maxIndex])):
                    maxIndex = 4
                    maxRemainingResources = tempResources[4] - 1 - self.tradeRates[4]

                """
                Within the player's temporary resources, port the resource chosen to the 
                bank to get a resource needed to build a road. Add the ported resource to 
                the list of resources that need to be ported to the bank to build a road.
                """
                if maxRemainingResources >= 0:
                    if tempResources[3] < 1:
                        tempResources[3] += 1
                    elif tempResources[4] < 1:
                        tempResources[4] += 1
                    else:
                        print("ERROR: Invalid attempt to trade resources to build a road")
                    resourcesToTrade.append(maxIndex)
                    tempResources[maxIndex] -= self.tradeRates[maxIndex]

            """ Can't build a road; return an empty list """
            return []

    """ Build a city for the player, if it is possible to do so """
    def placeCity(self, cityPoints):
        """
        Return -1 if the player already has the maximum number of cities,
        or if there are no locations available for the player to build a city
        """
        if len(cityPoints) == 0 or len(self.currentBoard.cities[self.playerNum - 1]) >= 4:
            return -1
        resourcesToTrade = self.cityPortResources(cityPoints)

        if len(resourcesToTrade) > 0:
            """ Trade resources with the bank until a city can be built """
            for i in range(len(resourcesToTrade)):
                if self.resources[0] < 3 and resourcesToTrade[i] != 0:
                    resourceReceived = 0
                elif self.resources[1] < 2 and resourcesToTrade[i] != 1:
                    resourceReceived = 1
                else:
                    print("ERROR: Invalid attempt to trade", self.getResourceType(resourcesToTrade[i]),
                          "by player", self.playerNum, "while trying to build a city")
                    continue
                self.portResource(resourcesToTrade[i], resourceReceived)

        """ Build a city, if possible """
        if self.resources[0] >= 3 and self.resources[1] >= 2:
            cityIndex = -1
            maxValue = -10
            for i in range(len(cityPoints)):
                random = randrange(20) / 10.0
                cityValue = self.getHexValue(cityPoints[i])
                if cityValue + random > maxValue:
                    maxValue = cityValue
                    cityIndex = i

            if cityIndex != -1:
                self.resources[0] -= 3
                self.resources[1] -= 2
                self.currentBoard.addCity(cityPoints[cityIndex], self.color, self.playerNum, False)
                self.currentBoard.playerScores[self.playerNum - 1] += 1
                self.updateResourcePoints(cityPoints[cityIndex])
                self.score += 1
                return cityIndex
        return -1

    """ Build a settlement for the player, if it is possible to do so """
    def placeSettlement(self, settlementPoints):
        """
        Return -1 if the player already has the maximum number of settlements,
        or if there are no locations available for the player to build a settlement
        """
        if len(settlementPoints) == 0 or len(self.currentBoard.settlements[self.playerNum - 1]) >= 5:
            return -1
        resourcesToTrade = self.settlementPortResources(settlementPoints)

        if len(resourcesToTrade) > 0:
            """ Trade resources with the bank until a settlement can be built """
            for i in range(len(resourcesToTrade)):
                if self.resources[1] < 1 and resourcesToTrade[i] != 1:
                    resourceReceived = 1
                elif self.resources[2] < 1 and resourcesToTrade[i] != 2:
                    resourceReceived = 2
                elif self.resources[3] < 1 and resourcesToTrade[i] != 3:
                    resourceReceived = 3
                elif self.resources[4] < 1 and resourcesToTrade[i] != 4:
                    resourceReceived = 4
                else:
                    print("ERROR: Invalid attempt to trade", self.getResourceType(resourcesToTrade[i]),
                          "by player", self.playerNum, "while trying to build a settlement")
                    continue
                self.portResource(resourcesToTrade[i], resourceReceived)

        """ Build a settlement """
        if self.resources[1] > 0 and self.resources[2] > 0 and self.resources[3] > 0 and self.resources[4] > 0:
            settlementIndex = -1
            maxValue = -10
            for i in range(len(settlementPoints)):
                random = randrange(20) / 10.0
                settlementValue = self.getHexValue(settlementPoints[i])
                if settlementValue + random > maxValue:
                    maxValue = settlementValue
                    settlementIndex = i

            if settlementIndex != -1:
                self.resources[1] -= 1
                self.resources[2] -= 1
                self.resources[3] -= 1
                self.resources[4] -= 1
                self.currentBoard.addSettlement(settlementPoints[settlementIndex], self.color, self.playerNum, False)
                newPortType = self.currentBoard.getPortType(settlementPoints[settlementIndex])
                if newPortType != "":
                    self.gainPortPower(newPortType)
                    print("Player", self.playerNum, "just acquired a", newPortType, "port!")
                self.currentBoard.playerScores[self.playerNum - 1] += 1
                self.updateResourcePoints(settlementPoints[settlementIndex])
                self.score += 1
                return settlementIndex
        return -1

    """ Build a road for the player, if it is possible to do so """
    def placeRoad(self, roadPoints):
        """
        Return -1 if the player already has the maximum number of roads,
        or if there are no locations available for the player to build a road
        """
        if len(roadPoints) == 0 or len(self.currentBoard.roads[self.playerNum - 1]) >= 15:
            return -1
        resourcesToTrade = self.roadPortResources(roadPoints)

        if len(resourcesToTrade) > 0:
            """ Trade resources with the bank until a road can be built """
            for i in range(len(resourcesToTrade)):
                if self.resources[3] < 1 and resourcesToTrade[i] != 3:
                    resourceReceived = 3
                elif self.resources[4] < 1 and resourcesToTrade[i] != 4:
                    resourceReceived = 4
                else:
                    print("ERROR: Invalid attempt to trade", self.getResourceType(resourcesToTrade[i]),
                          "by player", self.playerNum, "while trying to build a road")
                    continue
                self.portResource(resourcesToTrade[i], resourceReceived)

        """ Build a road """
        if self.resources[3] > 0 and self.resources[4] > 0:
            self.resources[3] -= 1
            self.resources[4] -= 1
            roadIndex = randrange(len(roadPoints))
            self.currentBoard.addRoad(roadPoints[roadIndex].p1, roadPoints[roadIndex].p2, self.color, self.playerNum,
                                      False)
            return roadIndex
        return -1

    """
    First build a city at a random legal location and repeat until no cities more can be built.
    Then build a settlement at a random legal location and repeat until no settlements more can be built.
    Then build a road at a random legal location and repeat until no more roads can be built.
    """
    def takeTurn(self, currentBoard):
        self.currentBoard = currentBoard

        while True:
            cityPoints = self.currentBoard.getPossibleCityLocations(self.playerNum)
            cityIndex = self.placeCity(cityPoints)
            if len(cityPoints) != 0:
                cityPoints.remove(cityPoints[cityIndex])
            if cityIndex == -1:
                break

        while True:
            settlementPoints = self.currentBoard.getPossibleSettlementLocations(self.playerNum)
            settlementIndex = self.placeSettlement(settlementPoints)
            if len(settlementPoints) != 0:
                settlementPoints.remove(settlementPoints[settlementIndex])
            if settlementIndex == -1:
                break

        while True:
            roadPoints = self.currentBoard.getPossibleRoadLocations(self.playerNum)
            roadIndex = self.placeRoad(roadPoints)
            if len(roadPoints) != 0:
                roadPoints.remove(roadPoints[roadIndex])
            if roadIndex == -1:
                break

        return self.currentBoard
