"""
Structure to hold the type and location of each port on the Catan board

Created on Sep 2, 2022

@author: Andrew Hubbard
"""

class Port:

    def __init__(self, portType):
        self.portLocations = None
        self.portType = portType

    def setPortLocations(self, portLocations):
        self.portLocations = portLocations
