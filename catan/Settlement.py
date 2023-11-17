'''
Structure to hold the location, color, and player number of each settlement on the Catan board

Created on Sep 2, 2022

@author: Andrew Hubbard
'''

class Settlement:

    def __init__(self, location, color, playerNum):
        self.location = location
        self.color = color
        self.playerNum = playerNum
