"""
Structure to hold the numbers rolled on each 6-sided die, and their sum

Created on Dec 23, 2023

@author: Andrew Hubbard
"""

from random import randrange

class Dice:

    def __init__(self):
        self.d1 = 0
        self.d2 = 0
        self.sum = 0

    def rollDice(self):
        self.d1 = randrange(6) + 1
        self.d2 = randrange(6) + 1
        self.sum = self.d1 + self.d2
        return self.sum
