#!/usr/bin/python

######
# AI #
######
import Actors
import Utilities
import math


class AI(object):
    """
    Base class for AI logic
    Methods are empty, to be implemented by subclasses
    """

    _character = None

    @property
    def character(self):
        """
        Returns character to which this AI is linked.
        """
        return self._character

    def __init__(self, character):
        """
        Constructor
        Arguments
            character - Character to which this AI is linked.
        """
        self._character = character

    def takeTurn(self):
        """
        Take one turn
        """
        raise Utilities.GameError("Class AI does not have implementation"
                "for takeTurn(), please use one of the subclasss")


class BasicMonsterAI(AI):
    """
    AI sub class that provides AI implementation for basic monsters.
    """

    def __init__(self, monster):
        """
        Constructor
        Arguments
            monster - Monster to which this AI is linked.
        """
        super(BasicMonsterAI, self).__init__(monster)
        #init class variables
        self._player = None
        
    def takeTurn(self):
        """
        Take one turn
        """
        Utilities.message(self.character.name + ' at ' + str(self.character.tile) +
                ' takes turn.', "AI")
        #Only take action if we are in a level
        if self.character.level is None:
            Utilities.message("   Not in a level, can't take action.", "AI")
            return
        #Only take action if we find the player
        if self.character.level.game.player is None:
            Utilities.message("   No player found, staying put", "AI")
            return

        player = self.character.level.game.player
        #Only take action if player is not dead.
        if player.state == Actors.Character.DEAD:
            Utilities.message("   Player is dead, no action needed", "AI")
            return

        #TODO medium: read this from the config file via monsterlibrary via
        #new class variable in Character class
        RoS = 8  # Range of Sight
        RoA = 2  # Range of Attack
        distance = Utilities.distanceBetween(self.character, player)
        #message('   Player ' + self.player.name + ' found at ' + \
        #        str(self.player.tile) + ' distance: ' + str(distance), "AI")

        #Only take action if player is within range of sight
        if distance > RoS:
            #message("   Player out of range of sight", "AI")
            return
        #Attack if player is within range of attack
        elif distance < RoA:
            Utilities.message("   Attacking player", "AI")
            self.character.attack(player)
            return
        else:
            Utilities.message("   Moving towards player", "AI")
            self.character.moveTowards(player)
            return


class ConfusedMonsterAI(AI):
    """
    AI sub class that provides AI implementation for confused monsters.
    It can be used to confuse a monster for a number of turns. After the turns the confusedAI will switch the monster back to the original AI.
    
    """
    def __init__(self, sourceEffect, confusedMonster, confusedTurns):
            """
            Constructor
            Arguments
                sourceEffect - the effect that causes the confusion
                confusedMonster - the Monster to which this AI is linked.
                confusedTurns - the number of turns the monster is confused
            """
            super(ConfusedMonsterAI, self).__init__(confusedMonster)
            self.originalAI = confusedMonster.AI
            self.sourceEffect = sourceEffect
            self.confusedTurns = confusedTurns
            confusedMonster.AI = self
    
    def takeTurn(self):
        """
        Take one turn
        """
        #act confused
        #TODO: roam around in random directions
        Utilities.message(self.character.name + ' stumbles around.', "GAME")
        
        self.confusedTurns -= 1
        if self.confusedTurns == 0:
            #switch back to regular AI
            self.character.AI = self.originalAI
        