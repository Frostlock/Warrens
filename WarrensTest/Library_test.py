__author__ = 'Frostlock'

import unittest

import random

from WarrensGame.Actors import Monster, Consumable, Equipment
from WarrensGame.Libraries import MonsterLibrary, ItemLibrary
from WarrensGame.Utilities import GameError

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
        self.mlib = MonsterLibrary()

    def tearDown(self):
        """
        unittest framework will run this after every individual test.
        """
        self.mlib = None

    def test_uniqueMonster(self):
        """
        Test if we can create a random monster.
        """
        with self.assertRaises(GameError):
            self.mlib.createMonster('zombie_master')
            self.mlib.createMonster('zombie_master')
        #print 'Creating unique monster twice raises correct GameError.'

    def test_monsterList(self):
        """
        Test if every monster can be correctly created.
        """
        # Create an instance of every monster
        monsters = []
        for monster_key in self.mlib.availableMonsters:
            monsters.append(self.mlib.createMonster(monster_key))
        #print 'Created ' + str(len(monsters)) + ' monsters'

        # Ensure monsters are being tracked correctly
        self.assertEqual(len(monsters), len(self.mlib.monsters))
        self.assertEqual(len(monsters), len(self.mlib.regularMonsters) + len(self.mlib.uniqueMonsters))

    def test_monsterProperties(self):
        # This test will trigger all properties
        difficulty = random.randint(1,10)
        aRandomMonster = self.mlib.getRandomMonster(difficulty)
        monsterClass = aRandomMonster.__class__.__name__
        property_names=[p for p in dir(eval(monsterClass)) if isinstance(getattr(eval(monsterClass),p),property)]
        for p in property_names:
            result = getattr(aRandomMonster, p)
            #print result

    def test_randomMonster(self):
        """
        Test if we can create a random monster.
        """
        #Create 10 monsters for the first 10 difficulty levels
        for difficulty in range(1, 10):
            #print "Difficulty " + str(difficulty)
            for i in range(1,10):
                monster = self.mlib.getRandomMonster(difficulty)
                #print "   Random monster: " + monster.name + " (CR: " + str(monster.challengeRating) + ")"

        with self.assertRaises(GameError):
            self.mlib.getRandomMonster(0)
        #print 'Asking for a monster with challenge rating 0 raises correct GameError.'

    def test_generatedMonster(self):
        for difficulty in range(1, 10):
            monster = self.mlib.generateMonster(difficulty)
            self.assertIsInstance(monster, Monster)

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
        self.ilib = ItemLibrary()

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
            item = self.ilib.createItem(item_key)
            items.append(item)
            if item.type == "Consumable":
                self.assertIsInstance(item,Consumable)
            elif item.type == "Equipment":
                self.assertIsInstance(item,Equipment)
            else:
                raise AssertionError("Unknown item type: " + str(item.type))

        #print 'Created ' + str(len(items)) + ' items'

        # Ensure items are being tracked correctly
        self.assertEqual(len(items), len(self.ilib.items))

    def test_itemProperties(self):
        # This test will trigger all properties
        difficulty = random.randint(1,10)
        aRandomItem = self.ilib.getRandomItem(difficulty)
        itemClass = aRandomItem.__class__.__name__
        property_names=[p for p in dir(eval(itemClass)) if isinstance(getattr(eval(itemClass),p),property)]
        for p in property_names:
            result = getattr(aRandomItem, p)
            #print result

    def test_randomItem(self):
        """
        Test if we can create a random item.
        """
        #Create 10 items for the first 10 difficulty levels
        for difficulty in range(1, 10):
            #print "Difficulty " + str(difficulty)
            for i in range(1,10):
                item = self.ilib.getRandomItem(difficulty)
                #print "   Random item: " + item.name + " (IL: " + str(item.itemLevel) + ")"

        with self.assertRaises(GameError):
            self.ilib.getRandomItem(0)

    def test_modifiedItem(self):
        """
        Test if we can create modified items
        """
        item = self.ilib.createItem("dagger","giant")
        self.assertEqual(item.name, "Giant dagger")

        #Incompatible modifiers should raise a GameError
        with self.assertRaises(GameError):
            self.ilib.createItem("dagger","minor")
        with self.assertRaises(GameError):
            self.ilib.createItem("firenova","soldier")

if __name__ == "__main__":
    unittest.main()