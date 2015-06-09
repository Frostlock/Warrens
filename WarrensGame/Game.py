"""
Created on Apr 13, 2014

To understand the design, it is recommended to read
the class design documentation on the wiki first!

@author: pi
"""

# Load proprietary modules
import CONSTANTS
import Utilities
from Maps import *
from Levels import *
from Actors import *
from Libraries import *
from AI import *
from Effects import *


class Game(object):
    """
    The game class contains the logic to run the game.
    It knows about turns
    It has pointers to all the other stuff, via the Game object you can drill
    down to all components
    It can save and load
    It keeps track of the levels and knows which is the current level
    At the moment I don't see the need for sub classes
    """

    PLAYING = 0
    FINISHED = 1
    _state = PLAYING

    @property
    def state(self):
        """
        Returns the game state
        """
        return self._state

    @property
    def messageBuffer(self):
        """
        Returns a queue of game messages.
        This is meant to be used by the GUI application to show the latest relevant game messages. 
        """
        return Utilities.messageBuffer

    @property
    def effectBuffer(self):
        """
        Returns an array of game effects.
        This is meant to give the GUI application the opportunity to show a visualization of the effect.
        :rtype : Utilities.effectBuffer
        """
        return Utilities.effectBuffer

    @property
    def player(self):
        """
        The player of the game
        """
        return self._player

    @property
    def levels(self):
        """
        Returns the list of levels in this game.
        """
        return self._levels

    @property
    def currentLevel(self):
        """
        Returns the current level
        """
        return self._currentLevel

    @currentLevel.setter
    def currentLevel(self, level):
        """
        Sets the current level
        """
        self._currentLevel = level

    @property
    def activeEffects(self):
        """
        A list of the currently active effects
        :return: Array of Effects
        """
        return self._activeEffects

    @property
    def monsterLibrary(self):
        """
        Returns the monster library used by this game.
        """
        return self._monsterLibrary

    @property
    def itemLibrary(self):
        """
        Returns the item library used by this game.
        """
        return self._itemLibrary

    def __init__(self):
        """
        Constructor to create a new game
        :rtype : Game
        """
        # Initialize class variables
        self._player = None
        self._currentLevel = None
        self._activeEffects = []
        # Initialize libraries
        self._monsterLibrary = MonsterLibrary()
        self._itemLibrary = ItemLibrary()

    def resetGame(self):
        """
        Resets this Game class to a play a new game.
        :rtype : None
        """
        # Clear up
        Utilities.resetMessageBuffer()
        self._levels = []

        # Generate a town level
        levelName = "Town"
        levelDifficulty = 1
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(levelDifficulty) + ')', "GENERATION")
        town = TownLevel(self, levelDifficulty, levelName)
        self._levels.append(town)
        self._currentLevel = town

        # Add some dungeon levels underneath the town
        prevLevel = None
        for i in range(1, 10):
            prevLevel = self.levels[i - 1]
            self.addDungeonLevel(i, [prevLevel])

        # Add a cave level
        self.addCaveLevel(2, [town, prevLevel])

        # Create player
        self.resetPlayer()

        # Set the game state
        self._state = Game.PLAYING

        # Send welcome message to the player
        Utilities.message('You are ' + self.player.name +
                          ', a young and fearless adventurer. It is time to begin your '
                          + 'legendary and without doubt heroic expedition into the '
                          + 'unknown. Good luck!', "GAME")

    def addDungeonLevel(self, difficulty, connectedLevels):
        """
        Adds a dungeon level to this game.
        Connect the new dungeon level to the connectedLevels
        :param difficulty: Difficulty for the new dungeon level
        :param connectedLevels: Levels to which the new dungeon level will be connected
        :rtype : None
        """
        levelName = 'Dungeon level ' + str(difficulty)
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        dungeonLevel = DungeonLevel(self, difficulty, levelName)
        self._levels.append(dungeonLevel)
        for lvl in connectedLevels:
            # Add portal in previous level to current level
            downPortal = Portal()
            downPortal._char = '>'
            downPortal._name = 'stairs leading down into darkness'
            downPortal._message = 'You follow the stairs down, looking for more adventure.'
            downPortal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # Add portal in current level to previous level
            upPortal = Portal()
            upPortal._char = '<'
            upPortal._name = 'stairs leading up'
            upPortal._message = 'You follow the stairs up, hoping to find the exit.'
            upPortal.moveToLevel(dungeonLevel, dungeonLevel.getRandomEmptyTile())
            # Connect the two portals
            downPortal.connectTo(upPortal)

    def addCaveLevel(self, difficulty, connectedLevels):
        """
        Adds a cave level to this game.
        Connect the new cave level to the connectedLevels
        :param difficulty: Difficulty for the new cave level
        :param connectedLevels: Levels to which the new cave level will be connected
        :rtype : None
        """
        levelName = 'Cave of the Cannibal'
        Utilities.message("Generating level: " + levelName + '(difficulty:' + str(difficulty) + ')', "GENERATION")
        caveLevel = CaveLevel(self, difficulty, levelName)
        self._levels.append(caveLevel)

        # For each connected level
        for lvl in connectedLevels:
            # create a portal in the connected level that leads to the new cave
            downPortal = Portal()
            downPortal._char = '>'
            downPortal._name = 'a deep pit with crumbling walls'
            downPortal._message = 'You jump into the pit. As you fall deeper and deeper, you realize you didn\'t ' \
                                  'think about how to get back out afterward...'
            downPortal.moveToLevel(lvl, lvl.getRandomEmptyTile())
            # create a portal in the new cave that leads back
            upPortal = Portal()
            upPortal._char = '<'
            upPortal._name = 'an opening far up in the ceiling'
            upPortal._message = 'After great difficulties you manage to get out of the pit.'
            upPortal.moveToLevel(caveLevel, caveLevel.getRandomEmptyTile())
            # connect the two portals
            downPortal.connectTo(upPortal)

    def resetPlayer(self):
        """
        Reset the player for this game.
        :rtype : None
        """
        self._player = Player()
        firstLevel = self.levels[0]
        self.player.moveToLevel(firstLevel, firstLevel.getRandomEmptyTile())

        # Quickstart
        if CONSTANTS.QUICKSTART:
            firstLevel = self.levels[0]
            self._currentLevel = firstLevel
            self.player.moveToLevel(firstLevel, firstLevel.portals[len(firstLevel.portals) - 2].tile)

        firstLevel.map.updateFieldOfView(
            self._player.tile.x, self._player.tile.y)

        # Starting gear
        scroll = self.itemLibrary.createItem("firenova", "double")
        self.player.addItem(scroll)
        scroll = self.itemLibrary.createItem("tremor")
        self.player.addItem(scroll)
        potion = self.itemLibrary.createItem("healingvial", "exquisite")
        self.player.addItem(potion)
        potion = self.itemLibrary.createItem("healingpotion")
        self.player.addItem(potion)
        potion = self.itemLibrary.createItem("healingpotion")
        self.player.addItem(potion)
        cloak = self.itemLibrary.createItem("cloak")
        self.player.addItem(cloak)
#        scroll = self.itemLibrary.createItem("firenova")
#        self.player.addItem(scroll)
        scroll = self.itemLibrary.createItem("fireball")
        self.player.addItem(scroll)
        scroll = self.itemLibrary.createItem("confuse")
        self.player.addItem(scroll)
        scroll = self.itemLibrary.createItem("lightning")
        self.player.addItem(scroll)

    def loadGame(self, fileName):
        """
        Loads game state from a file
        :param fileName:
        :rtype : None
        """
        # TODO: Implement saving and loading of gamestate
        pass

    def saveGame(self, fileName):
        """
        Saves state of current game to a file.
        :param fileName:
        :rtype : None
        """
        pass

    def tryToPlayTurn(self):
        """
        This function should be called regularly by the GUI. It waits for the player
        to take action after which all AI controlled characters also get to act.
        This is what moves the game forward.
        :rtype : Boolean indicating if a turn was played
        """
        # Wait for player to take action
        if self.player.actionTaken:
            # Let characters take a turn
            for c in self.currentLevel.characters:
                assert isinstance(c, Character)
                if c.state == Character.ACTIVE:
                    c.takeTurn()
                    c.actionTaken = False
            # Update field of view
            self.currentLevel.map.updateFieldOfView(self.player.tile.x, self.player.tile.y)
            # Let effects tick
            toRemove = []
            for effect in self.activeEffects:
                if effect.effectDuration <= 0:
                    toRemove.append(effect)
                else:
                    effect.tick()
            # Remove effects that are no longer active
            for effect in toRemove:
                self.activeEffects.remove(effect)
            return True
        else:
            return False