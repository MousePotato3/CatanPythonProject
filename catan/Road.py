'''
Structure to hold the locations, color, and player number of each road on the Catan board

Created on Sep 2, 2022

@author: Andrew Hubbard
'''

class Road:

    def __init__(self, location1, location2, color, playerNum):
        self.location1 = location1
        self.location2 = location2
        self.color = color
        self.playerNum = playerNum
