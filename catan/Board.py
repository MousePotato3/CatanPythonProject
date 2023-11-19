"""
Keeps track of the location and number for each resource on the Settlers of Catan board, 
along with the settlements, cities, roads, and number of resources and development cards 
for each player, as well as the owner (if any) of longest road and largest army.
Also keeps track of the winner of the game and returns this information to the Game class.
Does not keep track of player resource types, player development cards, or the number 
of points each player has (since this could be affected by hidden development cards).

Created on Sep 2, 2022

@author: Andrew Hubbard
"""
from catan import City
from catan import Hexagon
from catan import Point
from catan import DoublePoint
from catan import Port
from catan import Settlement
from catan import Road
from ctypes import windll
from math import sqrt
from random import shuffle, randrange
import PySimpleGUI

""" Structure to hold the coordinates of each intersection on the Catan board """
class Board:

    def __init__(self, numPlayers):
        """ Identify the coordinates of the center of the screen """
        self.robberLocation = None
        user32 = windll.user32
        self.centerX = user32.GetSystemMetrics(0) / 2.0
        self.centerY = user32.GetSystemMetrics(1) / 2.0

        """ Assign the width and height of each hexagon that makes up the Catan board """
        self.height = self.centerY / 5.6
        self.width = self.height * 1.15
        self.smallWidth = self.width / 2.0

        """ Initialize all of the data that the Board class will use """
        self.hexNumbers = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
        self.hexIntersections = []
        self.tiles = []
        self.hexCenters = []
        self.ports = []
        self.portPoint1Locations = []
        self.portPoint2Locations = []
        self.settlements = [[]]
        self.cities = [[]]
        self.roads = [[]]
        self.numResources = []
        self.playerScores = []
        self.numPlayers = numPlayers
        for _ in range(numPlayers):
            self.settlements.append([])
            self.cities.append([])
            self.roads.append([])
            self.numResources.append(0)
            self.playerScores.append(0)
        self.turnNumber = 1
        self.winner = -1
        self.isVisible = True

    """ This may not working currently """
    def drawBoard(self):
        if not self.isVisible:
            return

        layout = [
            [
                PySimpleGUI.Graph(
                    canvas_size=(self.centerX * 2, self.centerY * 2),
                    graph_bottom_left=(0, 0),
                    graph_top_right=(self.centerX * 2, self.centerY * 2),
                    key="graph"
                )
            ]
        ]

        window = PySimpleGUI.Window("Catan Game", layout)
        window.Finalize()

        myIcon = window.Element("Catan Tile")

        for i in range(len(self.tiles)):
            x = int(self.tiles[i].location.x)
            y = int(self.tiles[i].location.y)

            if self.tiles[i].hexType == "wood":
                myIcon.DrawImage(filename="forest.jpg", location=(x, y))
            elif self.tiles[i].hexType == "brick":
                myIcon.DrawImage(filename="hill.jpg", location=(x, y))
            elif self.tiles[i].hexType == "ore":
                myIcon.DrawImage(filename="mountain.jpg", location=(x, y))
            elif self.tiles[i].hexType == "sheep":
                myIcon.DrawImage(filename="pasture.jpg", location=(x, y))
            elif self.tiles[i].hexType == "wheat":
                myIcon.DrawImage(filename="plain.jpg", location=(x, y))
            else:
                myIcon.DrawImage(filename="desert.jpg", location=(x, y))

    """ Roll 2 6-sided dice and return the result """
    @staticmethod
    def rollDice():
        diceRoll = randrange(6) + randrange(6) + 2
        return diceRoll

    def setRobberLocation(self, robberLocation):
        self.robberLocation = robberLocation

    """
    Verify that the player is placing on a legal location and has a settlement available to place. 
    If these checks pass, add the settlement at the specified location and increment the player's score.
    """
    def addSettlement(self, point, color, playerNum, initialPlacement):
        if not (self.legalPlacement(point)):
            print("ERROR: Player", playerNum, "tried to place a settlement at location",
                  int(point.x), int(point.y), "which is too close to existing settlements")
        elif len(self.settlements[playerNum - 1]) >= 5:
            print("ERROR: Player", playerNum, "has the maximum number of settlements and cannot place any more")
        else:
            if not initialPlacement:
                print("Player", playerNum, "scored a point on turn", self.turnNumber,
                      "by placing a settlement at", int(point.x), int(point.y))
            self.settlements[playerNum - 1].append(Settlement.Settlement(point, color, playerNum))
            self.playerScores[playerNum - 1] += 1

    """
    Verify that the player has a settlement and the specified location and has a city available to place. 
    If these checks pass, replace the settlement with a city and increment the player's score.
    """
    def addCity(self, point, color, playerNum, initialPlacement):
        settlementIndex = self.findSettlementIndex(point, playerNum)
        if settlementIndex == -1:
            print("ERROR: Player", playerNum, "tried to place a city at location",
                  int(point.x), int(point.y), "but does not have a settlement at this location")
        elif len(self.cities[playerNum - 1]) >= 4:
            print("ERROR: Player", playerNum, "has the maximum number of cities and cannot place any more")
        else:
            if not initialPlacement:
                print("Player", playerNum, "scored a point on turn", self.turnNumber,
                      "by placing a city at", int(point.x), int(point.y))
            self.cities[playerNum - 1].append(City.City(point, color, playerNum))
            del self.settlements[playerNum - 1][settlementIndex]
            self.playerScores[playerNum - 1] += 1

    """
    Verify that the player is placing a road on an unoccupied location and the player 
    already has a road connected to the location (or a settlement for initial placements),
    and the player does not have the maximum number of roads placed already.
    If these checks pass, add a road connecting the points specified to the player's roads.
    """
    def addRoad(self, point1, point2, color, playerNum, initialPlacement):
        roadIndex = self.findRoadIndex(point1, point2, -1)
        if roadIndex != -1:
            print("ERROR: Player", playerNum, "tried to place a road between", int(point1.x), int(point1.y),
                  "and", int(point2.x), int(point2.y), "but there is already a road connecting these points")
        elif len(self.roads[playerNum - 1]) >= 15:
            print("ERROR: Player", playerNum, "has the maximum number of roads and cannot place any more")
        else:
            if not initialPlacement:
                print("Player", playerNum, "placed a road between", int(point1.x), int(point1.y),
                      "and", int(point2.x), int(point2.y), "on turn", self.turnNumber)
            self.roads[playerNum - 1].append(Road.Road(point1, point2, color, playerNum))

    """ Set up all of the resource tiles on the Catan game board """
    def initTiles(self):
        """ Create Hexagon objects for each Hexagon on the Catan board and put them in a random order """
        self.tiles.append(Hexagon.Hexagon("desert"))
        for _ in range(3):
            self.tiles.append(Hexagon.Hexagon("ore"))
        for _ in range(3):
            self.tiles.append(Hexagon.Hexagon("brick"))
        for _ in range(4):
            self.tiles.append(Hexagon.Hexagon("sheep"))
        for _ in range(4):
            self.tiles.append(Hexagon.Hexagon("wheat"))
        for _ in range(4):
            self.tiles.append(Hexagon.Hexagon("wood"))

        shuffle(self.tiles)
        """ Assign locations of the center of each Hexagon on the Catan board """
        self.hexCenters.append(Point.Point(self.centerX, self.centerY - 2 * self.height * 2))
        self.hexCenters.append(
            Point.Point(self.centerX - (self.width + self.smallWidth), self.centerY - 3 * self.height))
        self.hexCenters.append(
            Point.Point(self.centerX - (self.width * 2 + self.smallWidth * 2), self.centerY - self.height * 2))
        self.hexCenters.append(Point.Point(self.centerX - (self.width * 2 + self.smallWidth * 2), self.centerY))
        self.hexCenters.append(
            Point.Point(self.centerX - (self.width * 2 + self.smallWidth * 2), self.centerY + self.height * 2))
        self.hexCenters.append(
            Point.Point(self.centerX - (self.width + self.smallWidth), self.centerY + 3 * self.height))
        self.hexCenters.append(Point.Point(self.centerX, self.centerY + 2 * self.height * 2))
        self.hexCenters.append(
            Point.Point(self.centerX + (self.width + self.smallWidth), self.centerY + 3 * self.height))
        self.hexCenters.append(
            Point.Point(self.centerX + (self.width * 2 + self.smallWidth * 2), self.centerY + self.height * 2))
        self.hexCenters.append(Point.Point(self.centerX + (self.width * 2 + self.smallWidth * 2), self.centerY))
        self.hexCenters.append(
            Point.Point(self.centerX + (self.width * 2 + self.smallWidth * 2), self.centerY - self.height * 2))
        self.hexCenters.append(
            Point.Point(self.centerX + (self.width + self.smallWidth), self.centerY - 3 * self.height))
        self.hexCenters.append(Point.Point(self.centerX, self.centerY - self.height * 2))
        self.hexCenters.append(Point.Point(self.centerX - (self.width + self.smallWidth), self.centerY - self.height))
        self.hexCenters.append(Point.Point(self.centerX - (self.width + self.smallWidth), self.centerY + self.height))
        self.hexCenters.append(Point.Point(self.centerX, self.centerY + self.height * 2))
        self.hexCenters.append(Point.Point(self.centerX + (self.width + self.smallWidth), self.centerY + self.height))
        self.hexCenters.append(Point.Point(self.centerX + (self.width + self.smallWidth), self.centerY - self.height))
        self.hexCenters.append(Point.Point(self.centerX, self.centerY))

        """
        Assign numbers to each Hexagon on the Catan board, except for the desert
        which initially contains the robber instead of a number
        """
        counter = 0
        for i in range(len(self.tiles)):
            self.tiles[i].setLocation(self.hexCenters[i])
            if self.tiles[i].hexType != "desert":
                self.tiles[i].setNumber(self.hexNumbers[counter])
                counter = counter + 1
            else:
                self.robberLocation = self.tiles[i].location

        """ Assign the location of each intersection at the edge of a hexagon """
        for i in range(len(self.hexCenters)):
            self.hexIntersections.append(Point.Point(self.hexCenters[i].x + self.width, self.hexCenters[i].y))
            self.hexIntersections.append(Point.Point(self.hexCenters[i].x - self.width, self.hexCenters[i].y))
            self.hexIntersections.append(
                Point.Point(self.hexCenters[i].x + self.smallWidth, self.hexCenters[i].y + self.height))
            self.hexIntersections.append(
                Point.Point(self.hexCenters[i].x - self.smallWidth, self.hexCenters[i].y + self.height))
            self.hexIntersections.append(
                Point.Point(self.hexCenters[i].x + self.smallWidth, self.hexCenters[i].y - self.height))
            self.hexIntersections.append(
                Point.Point(self.hexCenters[i].x - self.smallWidth, self.hexCenters[i].y - self.height))

        """ Remove duplicates by converting to a Python set and back to a list """
        self.hexIntersections = [*set(self.hexIntersections)]

    """ Set up all of the ports on the Catan game board """
    def initPorts(self):
        """ Create Port objects for each Port on the Catan board and put them in a random order """
        for _ in range(4):
            self.ports.append(Port.Port("general"))
        self.ports.append(Port.Port("brick"))
        self.ports.append(Port.Port("ore"))
        self.ports.append(Port.Port("sheep"))
        self.ports.append(Port.Port("wheat"))
        self.ports.append(Port.Port("wood"))

        shuffle(self.ports)

        """ Assign locations of the each Port on the Catan board """
        self.portPoint1Locations.append(Point.Point(self.centerX - self.smallWidth, self.centerY + 5 * self.height))
        self.portPoint2Locations.append(Point.Point(self.centerX + self.smallWidth, self.centerY + 5 * self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX - (self.width + self.smallWidth * 2), self.centerY + 2 * self.height * 2))
        self.portPoint2Locations.append(
            Point.Point(self.centerX - (self.width * 2 + self.smallWidth), self.centerY + 3 * self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX - (3 * self.width + self.smallWidth * 2), self.centerY))
        self.portPoint2Locations.append(
            Point.Point(self.centerX - (self.width * 2 + 3 * self.smallWidth), self.centerY + self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX - (3 * self.width + self.smallWidth * 2), self.centerY - self.height * 2))
        self.portPoint2Locations.append(
            Point.Point(self.centerX - (self.width * 2 + 3 * self.smallWidth), self.centerY - 3 * self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX - (self.width + self.smallWidth * 2), self.centerY - 2 * self.height * 2))
        self.portPoint2Locations.append(Point.Point(self.centerX - self.width, self.centerY - 2 * self.height * 2))

        self.portPoint1Locations.append(
            Point.Point(self.centerX + self.width + self.smallWidth * 2, self.centerY - 2 * self.height * 2))
        self.portPoint2Locations.append(Point.Point(self.centerX + self.width, self.centerY - 2 * self.height * 2))

        self.portPoint1Locations.append(
            Point.Point(self.centerX + (3 * self.width + self.smallWidth * 2), self.centerY - self.height * 2))
        self.portPoint2Locations.append(
            Point.Point(self.centerX + (self.width * 2 + 3 * self.smallWidth), self.centerY - 3 * self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX + (3 * self.width + self.smallWidth * 2), self.centerY))
        self.portPoint2Locations.append(
            Point.Point(self.centerX + (self.width * 2 + 3 * self.smallWidth), self.centerY + self.height))

        self.portPoint1Locations.append(
            Point.Point(self.centerX + (self.width + self.smallWidth * 2), self.centerY + 2 * self.height * 2))
        self.portPoint2Locations.append(
            Point.Point(self.centerX + (self.width * 2 + self.smallWidth), self.centerY + 3 * self.height))

        for i in range(len(self.ports)):
            self.ports[i].setPortLocations(
                DoublePoint.DoublePoint(self.portPoint1Locations[i], self.portPoint2Locations[i]))

    """ Return the tile at the specified location, or -1 if not found """
    def findHexIndex(self, point):

        for i in range(len(self.tiles)):
            if point == self.tiles[i].location:
                return i
        return -1

    """
    Return the index of the settlement at the specified location, or -1 if not found. 
    If playerNum is not -1, only return a settlement index for the specified player.
    """
    def findSettlementIndex(self, point, playerNum):
        for i in range(len(self.settlements)):
            for j in range(len(self.settlements[i])):
                if (point == self.settlements[i][j].location and
                        (playerNum == -1 or self.settlements[i][j].playerNum == playerNum)):
                    return j
        return -1

    """
    Return the index of the city at the specified location, or -1 if not found. 
    If playerNum is not -1, only return a city index for the specified player.
    """
    def findCityIndex(self, point, playerNum):
        for i in range(len(self.cities)):
            for j in range(len(self.cities[i])):
                if (point == self.cities[i][j].location and
                        (playerNum == -1 or self.cities[i][j].playerNum == playerNum)):
                    return j
        return -1

    """
    Return the index of the road at the specified location, or -1 if not found. 
    If playerNum is not -1, only return a road index for the specified player.
    """
    def findRoadIndex(self, point1, point2, playerNum):
        """
        Return the road connecting the specified locations, or -1 if not found
        """
        for i in range(len(self.roads)):
            for j in range(len(self.roads[i])):
                if ((point1 == self.roads[i][j].location1 and point2 == self.roads[i][j].location2)
                        or (point1 == self.roads[i][j].location2 and point2 == self.roads[i][j].location1)
                        and (playerNum == -1 or self.roads[i][j].playerNum == playerNum)):
                    return j
        return -1

    """ Return True if the two points are adjacent to each other or False if they are not """
    def isAdjacent(self, point1, point2):

        distance = sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)
        if abs(distance - self.smallWidth * 2) < 2:
            return True
        else:
            return False

    """ Return the type of port at a specified location, or a blank string if the location is not at a port """
    def getPortType(self, point):
        for i in range(len(self.ports)):
            if point == self.ports[i].portLocations.p1 or point == self.ports[i].portLocations.p2:
                return self.ports[i].portType
        return ""

    """
    Create a list of every point adjacent to an intersection (should not include the point itself),
    for the purpose of determining where a settlement or a road can be built
    """
    def getAdjacentIntersections(self, point):
        adjacentPoints = []

        for i in range(len(self.hexIntersections)):
            if point != self.hexIntersections[i] and Board.isAdjacent(self, self.hexIntersections[i], point):
                adjacentPoints.append(self.hexIntersections[i])
        return adjacentPoints

    """
    Create a list of every hexagon adjacent to an intersection, 
    for the purpose of determining which tiles to collect resources from
    """
    def getAdjacentHexes(self, point):
        myHexes = []
        myInts = [Board.findHexIndex(self, Point.Point(point.x + self.width, point.y)),
                  Board.findHexIndex(self, Point.Point(point.x - self.width, point.y)),
                  Board.findHexIndex(self, Point.Point(point.x + self.smallWidth, point.y + self.height)),
                  Board.findHexIndex(self, Point.Point(point.x + self.smallWidth, point.y - self.height)),
                  Board.findHexIndex(self, Point.Point(point.x + self.smallWidth, point.y + self.height)),
                  Board.findHexIndex(self, Point.Point(point.x + self.smallWidth, point.y - self.height))]

        for i in range(6):
            if myInts[i] != -1:
                myHexes.append(self.tiles[i])

        return myHexes

    """
    Determine whether an intersection is legal for placing a settlement
    (no settlements or cities at the intersection or any adjacent intersections)
    """

    def legalPlacement(self, point):
        isHexLegal = True

        if Board.findSettlementIndex(self, point, -1) != -1 or Board.findCityIndex(self, point, -1) != -1:
            isHexLegal = False
        adjacentHexes = Board.getAdjacentIntersections(self, point)
        for i in range(len(adjacentHexes)):
            if (Board.findSettlementIndex(self, adjacentHexes[i], -1) != -1
                    or Board.findCityIndex(self, adjacentHexes[i], -1) != -1):
                isHexLegal = False
        return isHexLegal

    """ Return a list of possible locations for a player to build a city (replaces a settlement) """
    def getPossibleCityLocations(self, playerNum):
        possibleCityLocations = []
        for i in range(len(self.settlements[playerNum - 1])):
            possibleCityLocations.append(self.settlements[playerNum - 1][i].location)
        return possibleCityLocations

    """ Return a list of possible locations for a player to build a settlement """
    def getPossibleSettlementLocations(self, playerNum):
        playerRoadPoints = []
        possibleSettleLocations = []

        """ Create a list of all locations currently connected to the player's roads """
        for i in range(len(self.roads[playerNum - 1])):
            playerRoadPoints.append(self.roads[playerNum - 1][i].location1)
            playerRoadPoints.append(self.roads[playerNum - 1][i].location2)

        """ Remove duplicates by converting to a Python set and back to a list """
        playerRoadPoints = [*set(playerRoadPoints)]

        """ Include only locations where a settlement can be legally placed """
        for i in range(len(playerRoadPoints)):
            if self.legalPlacement(playerRoadPoints[i]):
                possibleSettleLocations.append(playerRoadPoints[i])

        return possibleSettleLocations

    """ Return a list of possible locations for a player to build a road """
    def getPossibleRoadLocations(self, playerNum):
        tempRoadPoints = []
        playerRoadPoints = []
        allRoadLocations = []
        possibleRoadLocations = []

        """ Create a list of all locations currently connected to the player's roads """
        for i in range(len(self.roads[playerNum - 1])):
            tempRoadPoints.append(self.roads[playerNum - 1][i].location1)
            tempRoadPoints.append(self.roads[playerNum - 1][i].location2)

        """ Remove duplicates by converting to a Python set and back to a list """
        tempRoadPoints = [*set(tempRoadPoints)]

        """ Only keep points not occupied by an opposing player's settlement or city """
        for i in range(len(tempRoadPoints)):
            mySettlementIndex = self.findSettlementIndex(tempRoadPoints[i], playerNum)
            myCityIndex = self.findCityIndex(tempRoadPoints[i], playerNum)
            anySettlementIndex = self.findSettlementIndex(tempRoadPoints[i], -1)
            anyCityIndex = self.findCityIndex(tempRoadPoints[i], -1)

            if ((mySettlementIndex != -1 or anySettlementIndex == -1)
                    and (myCityIndex != -1 or anyCityIndex == -1)):
                playerRoadPoints.append(tempRoadPoints[i])

        """ Create a list of possible roads, removing any for which the road already exists """
        for i in range(len(playerRoadPoints)):
            neighbors = self.getAdjacentIntersections(playerRoadPoints[i])
            for j in range(len(neighbors)):
                if self.findRoadIndex(playerRoadPoints[i], neighbors[j], -1) == -1:
                    allRoadLocations.append(DoublePoint.DoublePoint(playerRoadPoints[i], neighbors[j]))

        """ Remove duplicates """
        for roadLocation in allRoadLocations:
            if roadLocation not in possibleRoadLocations:
                possibleRoadLocations.append(roadLocation)

        return possibleRoadLocations
