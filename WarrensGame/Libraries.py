
from Actors import *
from CONSTANTS import *
from Utilities import GameError

import csv
import random

class BaseMonster(dict):
    '''
    Base monster, properties are generated from the dictionary
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        :param args: Dictionary object with the monster data
        :param kwargs:
        :return:
        '''
        super(BaseMonster, self).__init__(*args, **kwargs)
        self.__dict__ = self

class MonsterModifier(dict):
    '''
    Monster modifier, properties are generated from the dictionary
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        :param args: Dictionary object with the modifier data
        :param kwargs:
        :return:
        '''
        super(MonsterModifier, self).__init__(*args, **kwargs)
        self.__dict__ = self

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
        with open(DATA_MONSTERS, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for monsterDataDict in reader:
                # Ensure incoming data from csv file is interpreted correctly
                monsterDataDict["power"] = int(monsterDataDict["power"])
                monsterDataDict["defense"] = int(monsterDataDict["defense"])
                monsterDataDict["xp"] = int(monsterDataDict["xp"])
                monsterDataDict["unique"] = eval(monsterDataDict["unique"])
                monsterDataDict["challengeRating"] = int(monsterDataDict["challengeRating"])
                monsterDataDict["color"] = eval(monsterDataDict["color"])
                # Create the BaseMonster object
                baseMonster = BaseMonster(monsterDataDict)
                # Register the monster data in the data dictionary
                self.monsterIndex[baseMonster.key]=baseMonster
                # Register the monster data in the challenge dictionary
                if not int(baseMonster.challengeRating) in self.challengeIndex.keys():
                    self.challengeIndex[baseMonster.challengeRating] = []
                self.challengeIndex[baseMonster.challengeRating].append(baseMonster)

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
        monster = self.createMonster(selection.key)
        return monster

    def createMonster(self, monster_key):
        '''
        Function to create and initialize a new Monster.
        :param monster_key: string that identifies a monster in the config file.
        :return: Monster
        '''
        # load the monster data from the config
        baseMonster = self.monsterIndex[monster_key]

        # do not create multiple unique monsters
        if baseMonster.unique:
            unique_ids = []
            for unique_monster in self.uniqueMonsters:
                unique_ids.append(unique_monster.id)
            if monster_key in unique_ids:
                #This unique was already created, do nothing
                raise GameError('Unique monster' + monster_key + ' already exists.')

        #create monster
        newMonster = Monster(baseMonster)

        # register the monster
        if baseMonster.unique:
            self.uniqueMonsters.append(newMonster)
            #Avoid randomly recreating the same unique monster in the future
            self.challengeIndex[baseMonster.challengeRating].remove(baseMonster)
            if len(self.challengeIndex[baseMonster.challengeRating]) == 0:
                del self.challengeIndex[baseMonster.challengeRating]
        else:
            self.regularMonsters.append(newMonster)
        return newMonster

    def generateMonster(self,difficulty):
        '''
        Completely random generation of a monster, not based on the csv data file.
        '''
        Utilities.message('generating monster from scratch', 'GENERATION')

        monster_data = {}

        #Actor components
        monster_data['key'] = 'random'
        monster_data['char'] = 'M'
        monster_data['hitdie'] = str(difficulty) + 'd8'
        monster_data['name'] = 'Unrecognizable aberation'
        monster_data['color'] = [65, 255, 85]

        #Character components
        monster_data['defense'] = difficulty
        monster_data['power'] = difficulty + 2
        monster_data['xp'] = difficulty * difficulty * 50
        monster_data['ai'] = 'BasicMonsterAI'

        #Monster components
        monster_data['flavor'] = 'An unrecognizable aberation approaches'
        monster_data['killed_by'] = 'The aberation wanders around your remains.'

        #create monster
        baseMonster = BaseMonster(monster_data)
        newMonster = Monster(baseMonster)

        # register the monster
        self.regularMonsters.append(newMonster)
        return newMonster

class BaseItem(dict):
    '''
    Base Item, properties are generated from the dictionary
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        :param args: Dictionary object with the item data
        :param kwargs:
        :return:
        '''
        super(BaseItem, self).__init__(*args, **kwargs)
        self.__dict__ = self

#TODO: item modifiers should modify the item, currently they only affect the item name.
class ItemModifier(dict):
    '''
    Item modifier, properties are generated from the dictionary
    '''
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        :param args: Dictionary object with the item modifier data
        :param kwargs:
        :return:
        '''
        super(ItemModifier, self).__init__(*args, **kwargs)
        self.__dict__ = self

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
        Returns a dictionary of the items that this library can create.
        :return: Dictionary
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

    @property
    def availableModifiers(self):
        '''
        Returns a list of item modifiers that can be applied.
        '''
        return self.modifierIndex.keys()

    @property
    def modifierIndex(self):
        '''
        Returns a dictionary of item modifiers that this library can apply.
        :return: Dictionary
        '''
        return self._modifierIndex

    @property
    def modifierLevelIndex(self):
        '''
        Dictionary with an array of item modifier data dictionaries per modifier level
        Keys are Modifier Level.
        :return: Dictionary of arrays
        '''
        return self._modifierLevelIndex

    def __init__(self):
        '''
        Constructor to create a new item library
        '''
        #initialize class variables
        self._items = []
        self._itemIndex = {}
        self._itemLevelIndex = {}
        self._modifierIndex = {}
        self._modifierLevelIndex = {}

        # read item data from CSV file
        with open(DATA_ITEMS, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for itemDataDict in reader:
                baseItem = BaseItem(itemDataDict)
                # Register the item data in the data dictionary
                self.itemIndex[baseItem.key]=baseItem
                # Register the item data in the item level dictionary
                if not int(baseItem.itemLevel) in self.itemLevelIndex.keys():
                    self.itemLevelIndex[int(baseItem.itemLevel)] = []
                self.itemLevelIndex[int(baseItem.itemLevel)].append(baseItem)

        # read item modifier data from CSV file
        with open(DATA_ITEM_MODIFIERS, "rb") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for modifierDataDict in reader:
                itemModifier = ItemModifier(modifierDataDict)
                # Register the item modifier data in the data dictionary
                self.modifierIndex[itemModifier.key]=itemModifier
                # Register the item modifier data in the modifier level dictionary
                if not int(itemModifier.modifierLevel) in self.modifierLevelIndex.keys():
                    self.modifierLevelIndex[int(itemModifier.modifierLevel)] = []
                self.modifierLevelIndex[int(itemModifier.modifierLevel)].append(itemModifier)

    def createItem(self, item_key, modifier_key=None):
        '''
        Function to create and initialize a new Item.
        :param item_key: string that identifies the item
        :param modifier_key: string that identifies the item modifier
        :return: Item object
        '''
        # load the monster data from the config
        item_data = self.itemIndex[item_key]

        #create the correct type of item
        baseItem = BaseItem(item_data)
        item_class = eval(baseItem.type)
        newItem = item_class and item_class(baseItem) or None
        if newItem is None:
            raise GameError('Failed to create item with key: ' + item_key + '; unknown item type: ' + item_data['type'])

        if modifier_key is not None:
            modifier_data = self.modifierIndex[modifier_key]
            mod = ItemModifier(modifier_data)
            if baseItem.type == mod.type:
                newItem.modifiers.append(mod)
            else:
                raise GameError("Incompatible item modifier type. Can not apply " + modifier_key + " to " + item_key)

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
        itemLevel = maxItemLevel
        while not itemLevel in self.itemLevelIndex.keys():
            itemLevel -= 1
            if itemLevel <= 0: raise GameError("No items available below the give item level")
        # Make a random choice
        possibilities = self.itemLevelIndex[itemLevel]
        selection = random.choice(possibilities)
        # Create the item
        newItem = self.createItem(selection["key"])
        # Apply modifiers
        maxModifierLevel = maxItemLevel - itemLevel
        if maxModifierLevel > 0:
            modifier = self.getRandomModifier(maxModifierLevel)
            if newItem.type == modifier.type:
                newItem.modifiers.append(modifier)
        return newItem

    def getRandomModifier(self, maxModifierLevel):
        # Determine possibilities
        modifierLevel = maxModifierLevel
        while not modifierLevel in self.modifierLevelIndex.keys():
            modifierLevel -= 1
            if modifierLevel <= 0: raise GameError("No modifiers available below the give modifier level")
        # Make a random choice
        possibilities = self.modifierLevelIndex[modifierLevel]
        selection = random.choice(possibilities)
        # Create the item
        modifier = ItemModifier(selection)
        return modifier