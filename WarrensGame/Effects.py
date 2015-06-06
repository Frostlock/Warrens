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
        return self._targeted
    
    @property
    def effectRadius(self):
        """
        Radius of the effect size
        """
        return self._effectRadius

    @property
    def effectHitDie(self):
        """
        Hit die used to determine the random size of this effect.
        """
        return self._effectHitDie

    @property
    def effectDuration(self):
        """
        Duration in number of turns.
        """
        return self._effectDuration

    @property
    def effectDescription(self):
        """
        Textual description that describes what happens when
        this effect is applied.
        """
        return self._effectDescription

    @property
    def effectColor(self):
        """
        RGB tuple that indicates the color of this effect.
        """
        return self._effectColor
    
    #constructor
    def __init__(self, source, effectItem):
        """
        Constructor for a new Effect, meant to be used by the Effect subclasses.
        arguments
            source - an object representing the source of the effect
        """
        self._source = source
        self._targetType = EffectTarget.SELF
        self._effectDescription = "Description not set"
        
        self._targeted = effectItem.targeted
        self._effectRadius = effectItem.effectRadius
        self._effectHitDie = effectItem.effectHitDie
        self._effectDuration = effectItem.effectDuration
        self._effectColor = effectItem.effectColor
    

    #functions
    def applyTo(self, target):
        """
        Applies this effect to a target. The target can be several types of
        objects, it depends on the specific Effect subclass.
        """
        print "WARNING: missing effect applyTo() implementation"

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
    def __init__(self, source, effectItem):
        super(HealEffect, self).__init__(source, effectItem)
        self._effectDescription = "Wounds close, bones knit."
        self._targetType = EffectTarget.SELF

    def applyTo(self, target):
        """
        Healing effect will be applied to target character.
        arguments
            target - Character object
        """
        healAmount = Utilities.rollHitDie(self.effectHitDie)
        target.takeHeal(healAmount, self.source)
        effectTiles = [target.tile]
        Utilities.registerEffect(self, effectTiles)

class ConfuseEffect(MagicEffect):
    """
    This class represents a damage nova effect
    """
    #constructor
    def __init__(self, source, effectItem):
        '''
        source is the item that causes the effect
        '''
        super(ConfuseEffect, self).__init__(source, effectItem)
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
        Utilities.message(target.name + ' is confused for ' + str(confusedTurns) + ' turns.', "GAME")        

class DamageEffect(MagicEffect):
    """
    This class implements a damage effect.
    It can be targeted, in which case it will damage all actors in a circular area.
    It can be untargeted, in which case it will function as a nova, damaging all actors in a circular area around the source, excluding the tile of the source
    """

    #set when effect is applied
    _centerTile = None
    
    @property
    def centerTile(self):
        '''
        Returns tile on which the damage area is centered.
        '''
        return self._centerTile
    
    #constructor
    def __init__(self, source, effectItem):
        '''
        source is the item that causes the effect
        '''
        super(DamageEffect, self).__init__(source, effectItem)
        self._effectDescription = "The area is bombarded by magical energy."
        self._targetType = EffectTarget.TILE

    def applyTo(self, center):
        """
        Damage area is circular around center.
        If this effect is targeted, center should be a Tile object.
        If this effect is not targeted, center should be an Actor object.
        """
        if self.targeted:
            self._centerTile = center
        else:
            self._centerTile = center.tile
        #find all tiles that are in the damage area
        sourceTile = self.centerTile
        fullCircle = True
        excludeBlockedTiles = True
        radius = self.effectRadius
        effectTiles = sourceTile.map.getCircleTiles(sourceTile.x, sourceTile.y, radius, fullCircle, excludeBlockedTiles)
        #in case this is an untargeted effect
        if not self.targeted:
            #exclude the center of the nova
            effectTiles.remove(sourceTile)
        #find all targets in range
        targets = []
        for tile in effectTiles:
            for actor in tile.actors:
                targets.append(actor)
        #apply damage to every target
        damageAmount = Utilities.rollHitDie(self.effectHitDie)
        for target in targets:
            Utilities.message(self.source.name.capitalize() + ' hits '
                    + target.name + ' for ' + str(damageAmount) + ' Damage.', "GAME")
            target.takeDamage(damageAmount, self.source)
        #effect visualization
        Utilities.registerEffect(self, effectTiles)