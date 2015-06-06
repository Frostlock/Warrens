'''
Created on Apr 2, 2014

@author: pi

This module runs tests on the game logic.
'''
import unittest

import WarrensGame.Game as Game
import WarrensGame.CONSTANTS as CONSTANTS

class TestGame(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = True
        CONSTANTS.SHOW_GAME_LOGGING = True
        CONSTANTS.SHOW_GENERATION_LOGGING = True
        
    @classmethod
    def tearDownClass(self):
        """
        unittest framework will run this once after all the tests in this class have been run.
        """
        pass
    
    def setUp(self):
        """
        unittest framework will run this before every individual test.
        """
        pass
        
    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        pass
    
    def test_basicGame(self):
        """
        Create a basic game.
        """
        G = Game.Game()
        

    #TODO: Add testing code for the different Effects.

if __name__ == "__main__":
    print 'Run this using RunUnitTests.py in base directory.'