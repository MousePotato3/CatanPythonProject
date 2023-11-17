'''
Structure to hold the coordinates of each intersection on the Catan board

Created on Sep 2, 2022

@author: Andrew Hubbard
'''

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    ''' Determines whether 2 Point objects are equal (==) to each other '''
    def __eq__(self, other):
        if(int(self.x-other.x)==0 and int(self.y-other.y)==0):
            return True
        else:
            return False

    ''' Determines whether 2 DoublePoint objects are not equal (!=) to each other '''
    def __ne__(self, other):
        return not self.__eq__(other)

    ''' Allows for duplicate removal from a list of Point objects '''
    def __hash__(self):
        return hash(str(int(self.x)) + "," + str(int(self.y)))
