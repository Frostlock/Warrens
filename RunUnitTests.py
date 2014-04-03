'''
Created on Apr 2, 2014

@author: pi
'''
import unittest

if __name__ == '__main__':

    #Test the semantics of the game config file
    #These are currently not written in the unittest framework
    #TODO: convert Game.conf tests to unittest framework
    from WarrensTest import test_config
    test_config.runTests()
    
    #Discover relevant unittest tests
    suite = unittest.TestLoader().discover('./WarrensTest', pattern = "*_test.py")
    #Run the disccovered suite of tests
    unittest.TextTestRunner(verbosity=2).run(suite)