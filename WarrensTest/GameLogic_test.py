'''
Created on Apr 2, 2014

@author: pi

This module runs tests on the game logic.
'''
import unittest
import random
import WarrensGame.Game as Game
import WarrensGame.CONSTANTS as CONSTANTS
from WarrensGame.Utilities import GameError
from WarrensGame.Actors import Character

class TestGame(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        """
        unittest framework will run this once before all the tests in this class.
        """
        CONSTANTS.SHOW_AI_LOGGING = False
        CONSTANTS.SHOW_GAME_LOGGING = False
        CONSTANTS.SHOW_COMBAT_LOGGING = True
        CONSTANTS.SHOW_GENERATION_LOGGING = False

        self.game = Game.Game()
        self.game.resetGame()
        
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


    def test_healingEffect(self):
        # Note that we recreate the healing item every time because it is potentially used up.

        # Healing the player
        healingItem = self.game.itemLibrary.createItem("healingpotion")
        healingItem.applyTo(self.game.player)

        # Healing a monster
        healingItem = self.game.itemLibrary.createItem("healingpotion")
        aMonster = random.choice(self.game.monsterLibrary.monsters)
        healingItem.applyTo(aMonster)

        # Healing an item
        healingItem = self.game.itemLibrary.createItem("healingpotion")
        anItem = random.choice(self.game.itemLibrary.items)
        with self.assertRaises(GameError):
            healingItem.applyTo(anItem)

        # Healing a tile
        healingItem = self.game.itemLibrary.createItem("healingpotion")
        aTile = self.game.currentLevel.map.getRandomTile()
        with self.assertRaises(GameError):
            healingItem.applyTo(aTile)

    def test_damageEffect(self):
        # Note that we recreate the damage item every time because it is potentially used up.

        # Damage the player
        damageItem = self.game.itemLibrary.createItem("fireball")
        damageItem.applyTo(self.game.player)

        # Damage a monster
        damageItem = self.game.itemLibrary.createItem("fireball")
        aMonster = random.choice(self.game.monsterLibrary.monsters)
        damageItem.applyTo(aMonster)

        # Damage an item
        damageItem = self.game.itemLibrary.createItem("fireball")
        anItem = random.choice(self.game.itemLibrary.items)
        damageItem.applyTo(anItem)

        # Damage a tile
        damageItem = self.game.itemLibrary.createItem("fireball")
        aTile = self.game.currentLevel.map.getRandomTile()
        damageItem.applyTo(aTile)

        # Damage a something that does not make sense
        damageItem = self.game.itemLibrary.createItem("fireball")
        with self.assertRaises(GameError):
            damageItem.applyTo(self.game)

    def test_confuseEffect(self):
        # Note that we recreate the confuse item every time because it is potentially used up.

        # Confuse the player
        confuseItem = self.game.itemLibrary.createItem("confuse")
        with self.assertRaises(GameError):
            confuseItem.applyTo(self.game.player)

        # Confuse a monster
        confuseItem = self.game.itemLibrary.createItem("confuse")
        aMonster = random.choice(self.game.monsterLibrary.monsters)
        confuseItem.applyTo(aMonster)

        # Confuse an item
        confuseItem = self.game.itemLibrary.createItem("confuse")
        anItem = random.choice(self.game.itemLibrary.items)
        with self.assertRaises(GameError):
            confuseItem.applyTo(anItem)
        
        # Confuse a tile
        confuseItem = self.game.itemLibrary.createItem("confuse")
        aTile = self.game.currentLevel.map.getRandomTile()
        with self.assertRaises(GameError):
            confuseItem.applyTo(aTile)

        # Confuse a something that does not make sense
        confuseItem = self.game.itemLibrary.createItem("confuse")
        with self.assertRaises(GameError):
            confuseItem.applyTo(self.game)

    def test_combat(self):
        player = self.game.player
        aMonster = random.choice(self.game.monsterLibrary.monsters)
        while not (player.state == Character.DEAD or aMonster.state == Character.DEAD):
            #print "Attacker: " + str(player)
            #print "Target: " + str(aMonster)
            player.attack(aMonster)
            aMonster.attack(player)

if __name__ == "__main__":
    TestGame.main()