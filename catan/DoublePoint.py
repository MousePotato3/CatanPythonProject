"""
Structure to hold 2 Point variables at once

Created on Sep 2, 2022

@author: Andrew Hubbard
"""

class DoublePoint:

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2

    """ Determines whether 2 DoublePoint objects are equal (==) to each other """
    def __eq__(self, other):
        if ((self.p1 == other.p1 and self.p2 == other.p2)
                or (self.p1 == other.p2 and self.p2 == other.p1)):
            return True
        else:
            return False

    """ Determines whether 2 DoublePoint objects are not equal (!=) to each other """
    def __ne__(self, other):
        return not self.__eq__(other)

    """ Allows for duplicate removal from a list of DoublePoint objects """
    @property
    def __hash__(self):
        return hash(str(int(self.p1.x)) + "," + str(int(self.p1.y))
                    + str(int(self.p2.x)) + "," + str(int(self.p2.y)))
