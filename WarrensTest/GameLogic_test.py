'''
Created on Apr 2, 2014

@author: pi

This module runs tests on the game logic.
'''
import unittest
#import WarrensGame.Actors
import WarrensGame.Libraries as Libraries
import WarrensGame.Utilities as Utilities

class TestMonsterLibrary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """
        unittest framework will run this once before all the tests in this class.
        """
        pass
    
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
        self.mlib = Libraries.MonsterLibrary()
        
    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        self.mlib = None
    
    def test_monsterList(self):
        """
        Test if every monster can be correctly created.
        """
        # Create an instance of every monster
        monsters = []
        for monster_key in self.mlib.availableMonsters:
            monsters.append(self.mlib.createMonster(monster_key))
        print 'Created ' + str(len(monsters)) + ' monsters'
        
        # Ensure monsters are being tracked correctly
        self.assertEqual(len(monsters), len(self.mlib.monsters))
        self.assertEqual(len(monsters), len(self.mlib.regularMonsters) + len(self.mlib.uniqueMonsters))
            
    def test_randomMonster(self):
        """
        Test if we can create a random monster.
        """
        monster = self.mlib.getRandomMonster(5)
        print 'Created random monster: ' + monster.name
    
    def test_uniqueMonster(self):
        """
        Test if we can create a random monster.
        """
        with self.assertRaises(Utilities.GameError):
            monster = self.mlib.createMonster('zombie_master')
            monster = self.mlib.createMonster('zombie_master')
        print 'Creating unique monster twice raises correct GameError.'
    
class TestItemLibrary(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """
        unittest framework will run this once before all the tests in this class.
        """
        pass
    
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
        self.ilib = Libraries.ItemLibrary()
        
    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        self.ilib = None
    
    def test_itemList(self):
        """
        Test if every item can be correctly created.
        """
        # Create an instance of every item
        items = []
        for item_key in self.ilib.availableItems:
            items.append(self.ilib.createItem(item_key))
        print 'Created ' + str(len(items)) + ' items'
        
        # Ensure items are being tracked correctly
        self.assertEqual(len(items), len(self.ilib.items))
            
    def test_randomItem(self):
        """
        Test if we can create a random item.
        """
        item = self.ilib.getRandomItem(5)
        print 'Created random item: ' + item.name


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
        
    
if __name__ == "__main__":
    print 'Run this using RunUnitTests.py in base directory.'