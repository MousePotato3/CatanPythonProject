'''
Structure to hold the type, location, number, and value of each hexagon on the Catan board

Created on Sep 2, 2022

@author: Andrew Hubbard
'''

class Hexagon:

    def __init__(self, hexType):
        self.hexType = hexType
        self.number = 0
        self.value = 0

    def setLocation(self, location):
        self.location = location

    def setNumber(self, number):
        self.number = number
        if(number < 7):
            self.value = number - 1
        else:
            self.value = 13 - number

    ''' Determines whether 2 Hexagon objects are equal (==) to each other '''
    def __eq__(self, other):
        if(self.location==other.location):
            return True
        else:
            return False

    ''' Determines whether 2 Hexagon objects are not equal (!=) to each other '''
    def __ne__(self, other):
        return not self.__eq__(other)

    ''' Allows for duplicate removal from a list of Hexagon objects '''
    def __hash__(self):
        return hash(self.location)
