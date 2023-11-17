"""
The main program for the Settlers of Catan board game

Created on Aug 31, 2022

@author: Andrew Hubbard
"""
from catan import Game

''' Create a new instance of the Game class and call its main method '''

def main():
    catan = Game.Game()
    catan.play()

main()
