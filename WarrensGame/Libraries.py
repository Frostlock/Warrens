
from Actors import *

import csv
import random

class MonsterLibrary():
    '''
    This class represents a library of monsters.
    Logic to create monsters goes here. It contains logic related to managing
    a population of monsters.
    '''

    @property
    def uniqueMonsters(self):
        """
        Returns a list of all created unique Monster objects
        """
        return self._uniqueMonsters

    @property
    def regularMonsters(self):
        """
        Returns a list of all created regular Monster objects
        """
        return self._regularMonsters

    @property
    def monsters(self):
        """
        Returns a list of all created Monster objects
        """
        allMonsters = []
        for m in self.uniqueMonsters:
            allMonsters.append(m)
        for m in self.regularMonsters:
            allMonsters.append(m)
        return allMonsters

    @property
    def availableMonsters(self):
        """
        Returns a list of monsters that can be created.
        """
        return self.monsterIndex.keys()

    @property
    def monsterIndex(self):
        '''
        Dictionary that contains all monster data.
        Keys are monster keys.
        :return: Dictionary
        '''
        return self._monsterIndex

    @property
    def challengeIndex(self):
        '''
        Dictionary with an array of monster data dictionaries per challenge rating
        Keys are challenge rating.
        :return: Dictionary of arrays
        '''
        return self._challengeIndex

    def __init__(self):
        #initialize class variables
        self._uniqueMonsters = []
        self._regularMonsters = []
        self._monsterIndex = {}
        self._challengeIndex = {}

        # read data from CSV file
        with open("./WarrensGame/monsters.csv", "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for monsterDataDict in reader:
                # Register the monster data in the data dictionary
                self._monsterIndex[monsterDataDict['key']]=monsterDataDict
                # Register the monster data in the challenge dictionary
                if not int(monsterDataDict['challengeRating']) in self.challengeIndex.keys():
                    self.challengeIndex[int(monsterDataDict['challengeRating'])] = []
                self.challengeIndex[int(monsterDataDict['challengeRating'])].append(monsterDataDict)

    def getMaxMonstersPerRoomForDifficulty(self, difficulty):
        #maximum number of monsters per room
        max_monsters = difficulty / 2
        if max_monsters == 0: max_monsters = 1
        return max_monsters

    def getRandomMonster(self, maxChallengeRating):
        # Determine possibilities
        while not maxChallengeRating in self.challengeIndex.keys():
            maxChallengeRating -= 1
            if maxChallengeRating <= 0: raise Utilities.GameError("No monsters available below the give challenge rating")
        # Make a random choice
        possibilities = self.challengeIndex[maxChallengeRating]
        selection = random.choice(possibilities)
        # create the monster
        monster = self.createMonster(selection["key"])
        return monster

    def createMonster(self, monster_key):
        '''
        Function to create and initialize a new Monster.
        :param monster_key: string that identifies a monster in the config file.
        :return: Monster
        '''
        # load the monster data from the config
        monster_data = self.monsterIndex[monster_key]

        # do not create multiple unique monsters
        if monster_data['unique'] == 'True':
            unique_ids = []
            for unique_monster in self.uniqueMonsters:
                unique_ids.append(unique_monster.id)
            if monster_key in unique_ids:
                #This unique was already created, do nothing
                raise Utilities.GameError('Unique monster' + monster_key + ' already exists.')

        #create monster
        newMonster = Monster(monster_data)

        # register the monster
        if monster_data['unique'] == 'True':
            self.uniqueMonsters.append(newMonster)
            #Avoid randomly recreating the same unique monster in the future
            self.challengeIndex[int(monster_data["challengeRating"])].remove(monster_data)
            if len(self.challengeIndex[int(monster_data["challengeRating"])]) == 0:
                del self.challengeIndex[int(monster_data["challengeRating"])]
        else:
            self.regularMonsters.append(newMonster)
        return newMonster

    def generateMonster(self,difficulty):
        '''
        Completely random generation of a monster
        '''
        Utilities.message('generating monster from scratch', 'GENERATION')

        monster_data = {}

        #Actor components
        monster_data['key'] = 'random'
        monster_data['char'] = 'M'
        monster_data['hitdie'] = str(difficulty) + 'd8'
        monster_data['name'] = 'Unrecognizable aberation'
        monster_data['color'] = '[65, 255, 85]'

        #Character components
        monster_data['defense'] = str(difficulty)
        monster_data['power'] = str(difficulty)
        monster_data['xp'] = difficulty * difficulty * 50
        monster_data['ai'] = 'BasicMonsterAI'

        #Monster components
        monster_data['flavor'] = 'An unrecognizable aberation approaches'
        monster_data['killed_by'] = 'The aberation wanders around your remains.'

        #create monster
        newMonster = Monster(monster_data)

        # register the monster
        self.regularMonsters.append(newMonster)
        return newMonster

class ItemLibrary():
    '''
    This class represents a library of items. Logic to create items is
    implemented in this class.
    '''

    @property
    def items(self):
        '''
        Returns a list of all created items
        '''
        return self._items

    @property
    def availableItems(self):
        '''
        Returns a list of items that can be created.
        '''
        return self.itemIndex.keys()

    @property
    def itemIndex(self):
        '''
        Returns a list of the items that this library has created.
        '''
        return self._itemIndex


    @property
    def itemLevelIndex(self):
        '''
        Dictionary with an array of item data dictionaries per Item Level
        Keys are Item Level.
        :return: Dictionary of arrays
        '''
        return self._itemLevelIndex

    def __init__(self):
        '''
        Constructor to create a new item library
        '''
        #initialize class variables
        self._items = []
        self._itemIndex = {}
        self._itemLevelIndex = {}

        # read data from CSV file
        with open("./WarrensGame/items.csv", "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for itemDataDict in reader:
                # Register the item data in the data dictionary
                self._itemIndex[itemDataDict['key']]=itemDataDict
                # Register the item data in the item level dictionary
                if not int(itemDataDict['itemLevel']) in self.itemLevelIndex.keys():
                    self.itemLevelIndex[int(itemDataDict['itemLevel'])] = []
                self.itemLevelIndex[int(itemDataDict['itemLevel'])].append(itemDataDict)

    def createItem(self, item_key):
        '''
        Function to create and initialize a new Item.
        :param item_key: string that identifies the item
        :return: Item object
        '''
        # load the monster data from the config
        item_data = self.itemIndex[item_key]

        #create the correct type of item
        item_class = eval(item_data['type'])
        newItem = item_class and item_class(item_data) or None
        if newItem is None:
            raise Utilities.GameError('Failed to create item with key: ' + item_key + '; unknown item type: ' + item_data['type'])

        # register the new item
        self.items.append(newItem)
        return newItem

    def getMaxItemsPerRoomForDifficulty(self, difficulty):
        #maximum number of items per room
        max_items = difficulty / 2
        if max_items == 0: max_items = 1
        return max_items

    def getRandomItem(self, maxItemLevel):
        # Determine possibilities
        while not maxItemLevel in self.itemLevelIndex.keys():
            maxItemLevel -= 1
            if maxItemLevel <= 0: raise Utilities.GameError("No items available below the give item level")
        # Make a random choice
        possibilities = self.itemLevelIndex[maxItemLevel]
        selection = random.choice(possibilities)
        # Create the item
        newItem = self.createItem(selection["key"])
        return newItem