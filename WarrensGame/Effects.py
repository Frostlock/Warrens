#!/usr/bin/python

######################
# Magic/Event system #
######################

import Utilities
import AI

class EffectTarget:
    """
    Enumerator class to describe effect target types.
    """
    SELF = 0
    CHARACTER = 3
    TILE = 4

class Effect(object):
    """
    Base class for more specialized events, melee or magic effects.
    """

    #class properties
    @property
    def source(self):
        """
        The source of this effect
        """
        return self._source

    @property
    def tiles(self):
        """
        The tiles affected by this effect.
        :return: List of tiles
        """
        return self._tiles

    @property
    def actors(self):
        """
        The actors affected by this effect.
        :return: List of actors
        """
        return self._actors

    @property
    def targetType(self):
        """
        indicates the type of target this effect needs, enumerator
        """
        return self._targetType

    @property
    def targeted(self):
        """
        Boolean that indicates whether this effect is targeted.
        """
        return self.source.targeted
    
    @property
    def effectRadius(self):
        """
        Radius of the effect size
        """
        return self.source.effectRadius

    @property
    def effectHitDie(self):
        """
        Hit die used to determine the random size of this effect.
        """
        return self.source.effectHitDie

    @property
    def effectDuration(self):
        """
        Duration of this effect in number of turns.
        """
        return self._effectDuration

    @effectDuration.setter
    def effectDuration(self, duration):
        self._effectDuration = duration

    @property
    def effectDescription(self):
        """
        Textual description that describes what happens when
        this effect is applied.
        """
        return self._effectDescription

    @property
    def effectElement(self):
        """
        The element of this effect.
        """
        return self.source.effectElement

    def __init__(self, source):
        """
        Constructor for a new Effect, meant to be used by the Effect subclasses.
        arguments
            source - an object representing the source of the effect
        """
        self._source = source
        self._tiles = []
        self._actors = []
        self._targetType = EffectTarget.SELF
        self._effectDuration = self.source.effectDuration
        self._effectDescription = "Description not set"

    def applyTo(self, target):
        """
        Applies this effect to a target. The target can be several types of
        objects, it depends on the specific Effect subclass.
        """
        raise NotImplementedError("WARNING: missing effect applyTo() implementation")

    def tick(self):
        """
        Applies an additional duration tick for this effect.
        Supposed to be overridden in subclass.
        """
        raise NotImplementedError("WARNING: missing effect tick() implementation")

class MagicEffect(Effect):
    """
    Base class for magic effects.
    """
    #current thinking is that this class can both represent targeted as area
    #of effect spells.

class HealEffect(MagicEffect):
    """
    This class represents a healing effect
    """

    #constructor
    def __init__(self, source):
        super(HealEffect, self).__init__(source)
        self._effectDescription = "Wounds close, bones knit."
        self._targetType = EffectTarget.SELF

    def applyTo(self, target):
        """
        Healing effect will be applied to target character.
        arguments
            target - Character object
        """
        self._tiles = [target.tile]
        self._actors = [target]
        target.tile.map.level.game.activeEffects.append(self)
        self.tick()

    def tick(self):
        """
        Apply one tick of healing
        """
        # Update effectduration
        if self.effectDuration == 0: return
        self.effectDuration -= 1
        # Apply healing
        for target in self.actors:
            healAmount = Utilities.rollHitDie(self.effectHitDie)
            target.takeHeal(healAmount, self.source)

class ConfuseEffect(MagicEffect):
    """
    This class represents a damage nova effect
    """
    #constructor
    def __init__(self, source):
        '''
        source is the item that causes the effect
        '''
        super(ConfuseEffect, self).__init__(source)
        self._effectDescription = "An eerie melodie plays in the distance."
        self._targetType = EffectTarget.CHARACTER

    def applyTo(self, target):
        """
        Confuse effect will be applied to target character.
        arguments
            target - Character object
        """
        confusedTurns = self.effectDuration
        AI.ConfusedMonsterAI(self, target, confusedTurns)
        target.level.game.activeEffects.append(self)
        Utilities.message(target.name + ' is confused for ' + str(confusedTurns) + ' turns.', "GAME")        

class DamageEffect(MagicEffect):
    """
    This class implements a damage effect.
    It can be targeted, in which case it will damage all actors in a circular area.
    It can be untargeted, in which case it will function as a nova, damaging all actors in a circular area around the source, excluding the tile of the source
    """
    
    @property
    def centerTile(self):
        '''
        Returns tile on which the damage area is centered.
        '''
        return self._centerTile
    
    #constructor
    def __init__(self, source):
        '''
        source is the item that causes the effect
        '''
        super(DamageEffect, self).__init__(source)
        self._effectDescription = "The area is bombarded by magical energy."
        self._targetType = EffectTarget.TILE
        self._centerTile = None

    def applyTo(self, targetActor):
        """
        Damage area is circular around center.
        If this effect is targeted, center should be a Tile object.
        If this effect is not targeted, center should be an Actor object.
        """
        if self.targeted:
            self._centerTile = targetActor
        else:
            self._centerTile = targetActor.tile
        #find all tiles that are in the damage area
        sourceTile = self.centerTile
        fullCircle = True
        excludeBlockedTiles = True
        radius = self.effectRadius
        self._tiles = sourceTile.map.getCircleTiles(sourceTile.x, sourceTile.y, radius, fullCircle, excludeBlockedTiles)
        #in case this is an untargeted effect
        if not self.targeted:
            #exclude the center of the nova
            self.tiles.remove(sourceTile)
        # Tick for damage
        self.tick()
        # Register effect with Game
        targetActor.level.game.activeEffects.append(self)

    def tick(self):
        # Update effectduration
        if self.effectDuration == 0: return
        self.effectDuration -= 1
        #find all targets in range
        targets = []
        for tile in self.tiles:
            for actor in tile.actors:
                targets.append(actor)
        #apply damage to every target
        damageAmount = Utilities.rollHitDie(self.effectHitDie)
        for target in targets:
            Utilities.message(self.source.name.capitalize() + ' hits '
                    + target.name + ' for ' + str(damageAmount) + ' Damage.', "GAME")
            target.takeDamage(damageAmount, self.source.owner)
