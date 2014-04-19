'''
Created on Apr 14, 2014

@author: pi
'''
import unittest
import WarrensGame.Database as Database

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.db = Database.Database()


    def tearDown(self):
        pass


    def test_database(self):
        monsterData = self.db.getMonsterData(22)
        print monsterData.keys()
        print monsterData
        print monsterData['name']


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_database']
    unittest.main()