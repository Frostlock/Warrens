__author__ = 'Frostlock'

import unittest
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

    def test_randomMonster(self):
        """
        Test if we can create a random monster.
        """
        monster = self.mlib.getRandomMonster(5)
        #print 'Created random monster: ' + monster.name

        with self.assertRaises(GameError):
            self.mlib.getRandomMonster(0)
        #print 'Asking for a monster with challenge rating 0 raises correct GameError.'

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
            items.append(self.ilib.createItem(item_key))
        #print 'Created ' + str(len(items)) + ' items'

        # Ensure items are being tracked correctly
        self.assertEqual(len(items), len(self.ilib.items))

    def test_randomItem(self):
        """
        Test if we can create a random item.
        """
        item = self.ilib.getRandomItem(5)
        #print 'Created random item: ' + item.name
        with self.assertRaises(GameError):
            self.ilib.getRandomItem(0)

    def test_modifiedItem(self):
        """
        Test if we can create modified items
        """
        with self.assertRaises(GameError):
            self.ilib.createItem("dagger","minor")
        with self.assertRaises(GameError):
            self.ilib.createItem("firenova","soldier")

if __name__ == "__main__":
    unittest.main()