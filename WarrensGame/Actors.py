#!/usr/bin/python

#from Maps import Tile

import random
from Utilities import message, rollHitDie, GameError, distanceBetween, clamp
import CONSTANTS
import Effects #this is used in an eval statement
import AI #this is used in an eval statement
from Inventory import Inventory
from Interaction import Interaction

##########
# ACTORS #
##########
class Actor(object):
    """
    Base class for everything that can occur in the gameworld.
    Example sub classes: Items and Characters.
    """
    #I added hitpoints on this level, every Actor can be destroyed,
    # including items and portals.

    @property
    def id(self):
        """
        ID code for this Actor
        """
        return self._id

    @property
    def name(self):
        """
        Name of this Actor
        """
        return self._name

    @name.setter
    def name(self, newName):
        self._name = newName

    @property
    def flavorText(self):
        """
        Fancy description of the monster.
        """
        return self._flavorText

    @flavorText.setter
    def flavorText(self, text):
        self._flavorText = text

    @property
    def char(self):
        """
        Returns a 1 char shorthand for this actor.
        """
        return self._char

    @char.setter
    def char(self, newChar):
        self._char = newChar

    @property
    def tile(self):
        """
        Returns the Tile on which this Actor is located. Can be None.
        """
        return self._tile

    @tile.setter
    def tile(self, targetTile):
        """
        Moves this actor to the targetTile.
        """
        if self._tile is not None:
            self._tile.removeActor(self)
        self._tile = targetTile
        targetTile.addActor(self)

    @property
    def level(self):
        """
        Returns level on which this Actor is located. Can be None.
        """
        return self._level

    @level.setter
    def level(self, targetLevel):
        """
        Moves this actor to the targetLevel
        """
        if self._level is not None:
            self.level.removeActor(self)
        self._level = targetLevel
        self.registerWithLevel(targetLevel)

    @property
    def actionTaken(self):
        """
        Property to indicate if the actor took an action.
        Used by Game class to keep track of turns.
        :return: Boolean
        """
        return self._actionTaken

    @actionTaken.setter
    def actionTaken(self, acted):
        """
        Property to indicate if the actor took an action.
        :param acted: Boolean indicating if actor took action or not
        :return: None
        """
        self._actionTaken = acted

    @property
    def inView(self):
        """
        This actor is in view of the player.
        """
        return self._inView

    @inView.setter
    def inView(self, visible):
        self._inView = visible

    @property
    def color(self):
        """
        This actors preferred color (RGB tuple).
        """
        return self._color

    @property
    def sceneObject(self):
        '''
        Property used to store the scene object that represents this actor in the GUI.
        :return: SceneObject
        '''
        return self._sceneObject

    @sceneObject.setter
    def sceneObject(self, sceneObject):
        self._sceneObject = sceneObject

    def __init__(self):
        """
        Creates a new basic Actor, normally not used directly but should
        be called by subclasses.
        """
        # Initialize class properties
        self._char = "?"
        self._id = "not set"
        self._name = "Nameless"
        self._flavorText = ""
        self._tile = None
        self._level = None
        self._actionTaken = False
        self._color = (255, 255, 255)
        self._inView = False
        self._sceneObject = None

    #functions
    def __str__(self):
        return self._name + " " + super(Actor, self).__str__()

    def registerWithLevel(self, level):
        """
        This function registers this actor with the provided level.
        It has to be overridden in the Actor subclasses to ensure that the
        actor correctly registers with the level.
        """
        raise GameError('Missing implementation registerWithLevel()')

    def moveToRandomTile(self):
        """
        moves this actor to a random tile on the current level
        """
        if self.level is not None:
            self.moveToTile(self.level.getRandomEmptyTile)

    def moveToTile(self, targetTile):
        """
        moves this actor to the targetTile on the current level
        """
        if not targetTile.blocked:
            self.tile = targetTile

    def moveToLevel(self, targetLevel, targetTile):
        """
        moves this actor to the targetTile on the targetLevel
        """
        self.level = targetLevel
        self.moveToTile(targetTile)

    def removeFromLevel(self):
        """
        This method removes this actor from the level
        """
        if self.tile is not None:
            self.tile.removeActor(self)
        self._tile = None
        if self.level is not None:
            self.level.removeActor(self)
        self._level = None

    def moveAlongVector(self, vx, vy):
        """
        moves this actor on the current map according to the specified vector
        """
        #only works if we are on a map
        if self.tile is not None:
            targetX = self.tile.x + vx
            targetY = self.tile.y + vy
            #avoid out of bounds
            clamp(targetX, 0, self.tile.map.width)
            clamp(targetY, 0, self.tile.map.height)
            targetTile = self.level.map.tiles[targetX][targetY]
            if self.tile is not targetTile:
                self.moveToTile(targetTile)

    def moveTowards(self, targetActor):
        """
        Moves this actor towards the provided actor.
        arguments
            actor - the target Actor object
        """
        #vector towards the target
        dx = targetActor.tile.x - self.tile.x
        dy = targetActor.tile.y - self.tile.y
        #distance towards the target
        distance = distanceBetween(self, targetActor)
        #normalize it to length 1 (preserving direction), then round it and
        #convert to integer so the movement is restricted to the map grid
        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        #move along the vector
        self.moveAlongVector(dx, dy)

    def takeDamage(self, amount, attacker):
        """
        base function to take damage from an attacker.
        arguments
           damage - the incoming damage
           attacker - the attacking Actor
        """
        #base Actors are invulnerable
        pass

############
# Specials #
############
class Portal(Actor):
    """
    This class can be used to represent portals in and out of a level
    """

    @property
    def message(self):
        """
        In game message that should be displayed when portal is used.
        """
        return self._message

    @message.setter
    def message(self, msg):
        self._message = msg

    @property
    def destinationPortal(self):
        """
        The destination portal where this portal leads to
        """
        return self._destination

    def __init__(self):
        """
        Constructor to create a new portal
        """
        super(Portal, self).__init__()
        #portals are purple
        self._message = ""
        self._destination = None
        self._color = (150, 0, 255)

    def connectTo(self, otherPortal):
        """
        Connects this portal to another portal
        """
        self._destination = otherPortal
        otherPortal._destination = self

    def registerWithLevel(self, level):
        """
        Makes the level aware that this portal is on it.
        """
        level.addPortal(self)

class Container(Actor):
    '''
    Sub class representing a container object.
    '''

    @property
    def inventory(self):
        return self._inventory

    def __init__(self):
        """
        Constructor to create a new portal
        """
        super(Container, self).__init__()
        self._inventory = Inventory(self)
        #containers are gray
        self._color = (45, 45, 45)

    def addItem(self, newItem):
        self.inventory.add(newItem)

    def removeItem(self, removeItem):
        self.inventory.remove(removeItem)

##############
# CHARACTERS #
##############
class Character(Actor):
    """
    Base class for characters that can move around and interact
    Should probably not be instantiated but describes the general interface of
    a character
    Basic logic is in here, more specialised logic will be in the subclasses
    Every character has an AI that governs it
    Every character manages an inventory of items
    """

    @property
    def inventory(self):
        return self._inventory

    @property
    def equipedItems(self):
        """
        Returns a list of items that this characters has equiped.
        These are the equiped items only.
        """
        return self._equipedItems

    ACTIVE = 0
    DEAD = 1

    @property
    def state(self):
        """
        Returns this characters state
        """
        return self._state

    @property
    def maxHitPoints(self):
        """
        Maximum hitpoints of this Character (overrides Actor)
        """
        bonus = 0
        #TODO medium: return actual max_hp, by summing up the bonuses from all equipped items
        #bonus = sum(equipment.max_hp_bonus for equipment in get_all_equipped(self.owner))
        return self._baseMaxHitPoints + bonus

    @property
    def currentHitPoints(self):
        """
        The current amount of hitpoints
        """
        return self._currentHitPoints

    @currentHitPoints.setter
    def currentHitPoints(self, hitPoints):
        if hitPoints > self.maxHitPoints:
            self._currentHitPoints = self.maxHitPoints
        else:
            self._currentHitPoints = hitPoints

    @property
    def xpValue(self):
        """
        Return xp value
        """
        return self._xpValue

    @property
    def attackBonus(self):
        """
        Return attack attack bonus
        """
        bonus = 0
        for item in self.equipedItems:
            bonus += int(item.attackBonus)
        return self.baseAttackBonus + bonus

    @property
    def baseAttackBonus(self):
        return self._baseAttackBonus

    @property
    def armorClass(self):
        """
        Return armor value
        """
        bonus = 0
        for item in self.equipedItems:
            bonus += item.armorBonus
        #TODO: Limit armor bonus to one equiped armor and one possible shield.
        return 10 + self.naturalArmor + bonus

    @property
    def naturalArmor(self):
        return self._naturalArmor

    @property
    def weapon(self):
        for item in self.equipedItems:
            if not item.damage == "None":
                return item
        return None

    @property
    def AI(self):
        """
        Return AI associated to this character.
        """
        return self._AI
    
    @AI.setter
    def AI(self,myAI):
        """
        Sets the AI for this character.
        """
        self._AI = myAI

    #Constructor
    def __init__(self):
        """
        Creates a new character object, normally not used directly but called
        by sub class constructors.
        """
        #call super class constructor
        super(Character, self).__init__()
        #initialize class variables
        self._baseMaxHitPoints = 1
        self._currentHitPoints = 1
        self._naturalArmor = 0
        self._baseAttack = 1
        self._equipedItems = []
        self._inventory = Inventory(self)
        self._xpValue = 0
        self._AI = None
        self._state = Character.ACTIVE

    #Functions
    def registerWithLevel(self, level):
        """
        Makes the level aware that this character is on it.
        """
        level.addCharacter(self)

    def addItem(self, item):
        """
        adding item puts it in this characters inventory
        """
        self.inventory.add(item)
        #TODO: check for auto equip

    def removeItem(self, item):
        """
        removes the item from the characters inventory
        """
        if item in self.equipedItems:
            #unequip the item
            self.unEquipItem(item)
        self.inventory.remove(item)

    def equipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only equip if item is in inventory
        if item in self.inventory.items:
            #can only equip if not yet equiped
            if item not in self.equipedItems:
                self.equipedItems.append(item)
                item.isEquiped = True
                message(self.name.capitalize() + ' equips a '
                        + item.name + '.', "GAME")

    def unEquipItem(self, item):
        """
        basic implementation of equiping, doesn't take into account
        equipment slots. Should be overridden in subclass implementations.
        """
        #can only unequip if item is equiped
        if item in self.equipedItems:
            self.equipedItems.remove(item)
            item.isEquiped = False
            message(self.name.capitalize() + ' unequips a '
                        + item.name + '.', "GAME")

    def pickUpItem(self, item):
        """
        Make this character pick up an item.
        Arguments
            item - the item to be picked up
        """
        #remove the item from its tile and level
        item.removeFromLevel()
        #add the item to the inventory of this character
        self.addItem(item)
        #message
        message(self.name.capitalize() + ' picks up a '
                    + item.name + '.', "GAME")

    def dropItem(self, item):
        """
        Make this character drop an item on the current tile.
        Arguments
            item - the item to be dropped
        """
        #unequip it if required
        if item in self.equipedItems:
            self.unEquipItem(item)
        #if it is in the inventory remove it
        if item in self.inventory.items:
            self.inventory.remove(item)
        #add it to the current tile of the character
        item.moveToLevel(self.level, self.tile)
        #message
        message(self.name.capitalize() + ' drops a '
                    + item.name + '.', "GAME")

    def attackRoll(self):
        '''
        Rolls a D2O and applies this Characters attack bonus.
        :return: attackRoll
        '''
        roll = rollHitDie("1d20")
        if roll == 1: return 1   # natural 1 is always a miss
        elif roll == 20: return 20 # natural 20 is always a hit
        else: return roll + self.attackBonus

    def attack(self, target):
        """
        Attack another Character
        Arguments
            target - the Character to be attacked
        """
        # Check if the attack hits
        attackRoll = self.attackRoll()
        message(self.name.capitalize() + ': Attack Roll: ' + str(attackRoll) + ' Armor Class: ' + str(target.armorClass), "COMBAT")
        if attackRoll == 1:
            # Natural miss
            message(self.name.capitalize() + ' attacks ' + target.name + ' : Critical miss!', "GAME")
        elif attackRoll == 20:
            #Natural hit
            weapon = self.weapon
            if weapon is None:
                #Unarmed attack
                damage = rollHitDie("1d3") * 2
            else:
                damage = rollHitDie(weapon.damage) * 2
            message(self.name.capitalize() + ' attacks ' + target.name + ' : Critical hit! (' + str(damage) + ' Damage)', "GAME")
            target.takeDamage(damage, self)
        elif attackRoll >= target.armorClass:
            weapon = self.weapon
            if weapon is None:
                #Unarmed attack
                damage = rollHitDie("1d3")
            else:
                damage = rollHitDie(weapon.damage)
            message(self.name.capitalize() + ' attacks ' + target.name + ' : Hit! (' + str(damage) + ' Damage)', "GAME")
            target.takeDamage(damage, self)
        else:
            message(self.name.capitalize() + ' attacks ' + target.name + ' : Miss!', "GAME")

    def takeDamage(self, amount, attacker):
        """
        function to take damage from an attacker
        arguments
           damage - the incoming damage
           attacker - the attacking Actor
        """
        if self.state == Character.ACTIVE:
            #apply damage if possible
            if amount > 0:
                self.currentHitPoints -= amount
            #check for death
            if self.currentHitPoints <= 0:
                message(self.name.capitalize() + ' is killed!', "GAME")
                self._killedBy(attacker)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Character
        """
        if self.state == Character.ACTIVE:
            if type(attacker) is Player:
                #yield experience to the player
                message(attacker.name + ' gains ' + str(self.xpValue) + ' XP.', "GAME")
                attacker.gainXp(self.xpValue)
            if type(attacker) is Monster:
                if attacker.killedByText != '':
                    message(attacker.killedByText, "GAME")
            #transform this character into a corpse and remove AI
            self._char = '%'
            self._AI = None
            self._name = self.name + ' corpse'
            self._state = Character.DEAD

    def takeHeal(self, amount, healer):
        """
        function to heal a given amount of hitpoints
        arguments
           amount - the number of hitpoints to heal
           healer - the source of teh healing
        """
        #heal by the given amount
        if amount > 0:
            self.currentHitPoints += amount
            message(self.name.capitalize() + ' gains '
                    + str(amount) + ' hitpoints from a ' +  healer.name
                    + '.', "GAME")

    def takeTurn(self):
        """
        Function to make this Character take one turn.
        """
        if self.AI is not None:
            self.AI.takeTurn()

class Player(Character):
    """
    Sub class representing a player
    """
    @property
    def xp(self):
        """
        Returns the current xp of the player.
        """
        return self._xp

    @property
    def nextLevelXp(self):
        """
        Returns the required Xp to reach the next player level
        """
        return self._nextLevelXp

    @property
    def playerLevel(self):
        """
        Returns the current level of the player.
        """
        return self._playerLevel

    @property
    def direction(self):
        """
        Last direction in which this player moved
        :return: (x,y) modifier that shows the direction
        """
        return self._direction

    @direction.setter
    def direction(self,direction):
        self._direction = direction

    #constructor
    def __init__(self):
        """
        Creates and initializes new player object. Note that the object is not
        linked to a game tile. It should be moved to the tile after creation.
        """
        #call super class constructor
        super(Player, self).__init__()

        #initialize all properties
        #Actor properties
        self._id = 'player'
        self._char = '@'
        self._baseMaxHitPoints = 60
        self._currentHitPoints = 60
        self._name = random.choice(('Joe', 'Wesley', 'Frost'))
        #player is white
        self._color = (250,250,250)
        #Character properties
        self._naturalArmor = 0
        self._baseAttackBonus = 0
        self._xpValue = 1
        self._AI = None
        #Player properties
        self._xp = 0
        self._playerLevel = 1
        self._nextLevelXp = CONSTANTS.GAME_XP_BASE
        self.direction = (1,1)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Player
        It overrides the Character implementation
        """
        origName = self.name
        #call super class implementation
        super(Player, self)._killedBy(attacker)
        #Player class specific
        self._char = '%'
        self._color = (255,0,0)
        self._name = 'The remains of ' + origName
        
    def levelUp(self):
        '''
        Increase level of this player
        '''
        message("You feel stronger!", "GAME")
        self._playerLevel += 1
        self._nextLevelXp = CONSTANTS.GAME_XP_BASE + CONSTANTS.GAME_XP_BASE * CONSTANTS.GAME_XP_FACTOR * (self.playerLevel * self.playerLevel - 1)
        self._baseMaxHitPoints += rollHitDie("1d10")
         
    def gainXp(self, amount):
        """
        Increase xp of this player with the given amount
        arguments
            amount - integer
        """
        self._xp += amount
        #check for level up
        while self.xp >= self.nextLevelXp:
            self.levelUp()

    def followPortal(self, portal):
        """
        Send player through specified portal.
        """
        #Game message
        message(portal.message, "GAME")
        #Move the player to the destination
        destinationLevel = portal.destinationPortal.level
        destinationTile = portal.destinationPortal.tile
        self.moveToLevel(destinationLevel, destinationTile)
        #change the current level of the game to the destinationlevel
        myGame = destinationLevel.game
        myGame.currentLevel = destinationLevel

    def tryMoveOrAttack(self, dx, dy):
        """
        Player tries to move or attack in direction (dx, dy).
        This function is meant to be called from the GUI.
        This function will also register that the player took an action
        """
        self.actionTaken = True

        self.direction = (dx,dy)
        # The coordinates the player is moving to/attacking
        x = self.tile.x + dx
        y = self.tile.y + dy
        targetTile = self.level.map.tiles[x][y]

        # Try to find a target actor on the target tile
        target = None
        for a in targetTile.actors:
            #only attack monsters
            if type(a) is Monster:
                #don't attack dead monsters
                if a.state != Character.DEAD:
                    target = a

        # Attack if target found, move otherwise
        if target is not None:
            self.attack(target)
        else:
            self.moveAlongVector(dx, dy)

    def tryFollowPortalUp(self):
        """
        Player attempts to follow a portal up at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '<':
                self.followPortal(a)
                break

    def tryFollowPortalDown(self):
        """
        Player attempts to follow a portal down at the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is a portal up on the current tile
        for a in self.tile.actors:
            if type(a) is Portal and a.char == '>':
                self.followPortal(a)
                break

    def tryInteract(self):
        """
        Player attempts to interact with actors on the current tile.
        This function is meant to be called from the GUI.
        If the interaction requires further handling in the GUI and interaction object will be returned.
        Returns None if the interaction can be completed without further GUI activities.
        """
        #check if there are items on the current tile to interact with
        for a in self.tile.actors:
            if isinstance(a, Item):
                self.pickUpItem(a)
                return None
            if isinstance(a, Container):
                interaction = Interaction(CONSTANTS.INTERACTION_CONTAINER, self, a)
                return interaction

    def tryUseItem(self, item, target=None):
        """
        Player attempts to use an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Consumable):
            #try to use the consumable
            if not item.isConsumed:
                if target is None:
                    #apply to self
                    item.applyTo(self)
                else:
                    #apply to target
                    item.applyTo(target)
            #remove the item it is used up
            if item.isConsumed == True:
                self.removeItem(item)

        elif isinstance(item, Equipment):
            if item.isEquiped:
                #unequip the item
                self.unEquipItem(item)
            else:
                #equip the item
                self.equipItem(item)
        else:
            raise GameError("Missing implementation to use item")

    def tryDropItem(self, item):
        """
        Player attempts to drop an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Equipment):
            if item.isEquiped:
                message("You can't drop an equiped item.")
                return
        self.dropItem(item)

class NPC(Character):
    """
    Sub class representing a NPC, for example a vendor
    Probably we'll need to override some inventory concepts
    """


class Monster(Character):
    """
    Sub class representing a monster
    Later we can consider more specialised subclasses
    for example Humanoid, Undead, Animal
    """
    @property
    def baseMonster(self):
        return self._baseMonster

    @property
    def killedByText(self):
        """
        Killed by message that can be shown if this monster kills the player.
        """
        return self.baseMonster.killedBy

    @property
    def modifiers(self):
        '''
        Modifiers linked to this item
        '''
        return self._modifiers

    @property
    def challengeRating(self):
        cRating =  self.baseMonster.challengeRating
        for modifier in self.modifiers:
            cRating += modifier.modifierLevel
        return cRating

    #constructor
    def __init__(self, baseMonster):
        """
        Creates a new uninitialized Monster object.
        Use MonsterLibrary.createMonster() to create an initialized Monster.
        """
        #call super class constructor
        super(Monster, self).__init__()

        self._baseMonster = baseMonster
        self._modifiers = []

        #Actor components
        self._id = baseMonster.key
        self._char = baseMonster.char
        self._baseMaxHitPoints = rollHitDie(baseMonster.hitdie)
        self._currentHitPoints = self._baseMaxHitPoints
        self._name = baseMonster.name
        self._flavorText = baseMonster.flavor
        self._color = baseMonster.color

        #Character components
        self._naturalArmor = baseMonster.naturalArmor
        self._baseAttackBonus = baseMonster.attackBonus
        self._xpValue = baseMonster.xp
        #gets a class object by name; and instanstiate it if not None
        ai_class = eval('AI.' + baseMonster.AI)
        self._AI = ai_class and ai_class(self) or None

#########
# ITEMS #
#########
class Item(Actor):
    """
    Base class for items
    Should probably not be instantiated but describes the general interface of
    an item
    """
    @property
    def type(self):
        return self.baseItem.type

    @property
    def targeted(self):
        """
        Base class implementation, basic items are not targetable, can be refined in subclasses
        """
        return False

    @property
    def stackable(self):
        """
        Items can be stackable
        """
        return self._stackable
    
    @property
    def stackSize(self):
        '''
        Stack size getter
        '''
        return self._stackSize
    
    @stackSize.setter
    def stackSize(self,newStackSize):
        '''
        Stack size setter
        '''
        self._stackSize = newStackSize

    @property
    def baseItem(self):
        '''
        Base item for this item.
        '''
        return self._baseItem

    @property
    def modifiers(self):
        '''
        Modifiers linked to this item
        '''
        return self._modifiers

    @property
    def name(self):
        '''
        Name of this Item
        '''
        name = self.baseItem.name
        # Apply modifiers
        for modifier in self.modifiers:
            if modifier.position == "prefix":
                name = modifier.name + " " + name
            elif modifier.position == "suffix":
                name = name + " " + modifier.name
        # Stack size
        if self.stackable and self.stackSize > 1:
            name += '(stack: ' + str(self.stackSize) + ')'
        # Fix capitalization
        name = name.lower().capitalize()
        return name

    @property
    def itemLevel(self):
        iLevel= self.baseItem.itemLevel
        for modifier in self.modifiers:
            iLevel += modifier.modifierLevel
        return iLevel

    @property
    def owner(self):
        """
        Returns the owner of this item.
        :return: Character or None
        """
        return self._owner

    @owner.setter
    def owner(self, owner):
        '''
        Set the owner of this item to the given owner (Character).
        :param owner: Character that owns this item
        :return: None
        '''
        self._owner = owner

    def registerWithLevel(self, level):
        """
        Makes the level aware that this item is on it.
        """
        level.addItem(self)

    def __init__(self, baseItem):
        """
        Creates a new Item object, normally not used directly but called
        by sub class constructors.
        """
        #call super class constructor
        super(Item, self).__init__()
        #Initialize Item components
        self._baseItem = baseItem
        self._id = baseItem.key
        self._char = baseItem.char
        self._baseMaxHitPoints = 1
        self._currentHitPoints = self._baseMaxHitPoints
        self._name = baseItem.name
        self._modifiers = []
        self._owner = None

        #Basic items are not stackable
        self._stackable = False
        self.stackSize = 1

class Equipment(Item):
    """
    Sub class for equipment = items that can be equiped
    Might need more subclasses for weapons versus armor
    """
    @property
    def armorBonus(self):
        """
        The armor bonus of this piece of equipment
        """
        return self._armorBonus

    @property
    def attackBonus(self):
        """
        The attack bonus of this piece of equipment
        """
        return self._attackBonus

    @property
    def damage(self):
        return self._damage

    @property
    def isEquiped(self):
        """
        Boolean indicating if this piece of equipment is equiped.
        """
        return self._isEquiped

    @isEquiped.setter
    def isEquiped(self, status):
        """
        Sets the isEquiped status for this piece of equipment.
        """
        self._isEquiped = status

    @property
    def name(self):
        """
        Specialised version of name property.
        """
        suffix =''
        if self.isEquiped:
            suffix = ' (equiped)'
        return super(Equipment, self).name + suffix

    #constructor
    def __init__(self, baseItem):
        """
        Creates a new uninitialized Equipment object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Equipment, self).__init__(baseItem)
        #Initialize equipment properties
        self._armorBonus = baseItem.armorBonus
        self._attackBonus = baseItem.attackBonus
        self._damage = baseItem.damage
        self._isEquiped = False

class Consumable(Item):
    """
    Sub class for items that can be used and consumed.
    """
    @property
    def effect(self):
        """
        The effect that this consumable can generate.
        """
        #TODO: Modifier to take into account?
        return self._effect

    @property
    def targeted(self):
        """
        Boolean that indicates whether this consumable is targeted.
        """
        #TODO: Modifier of non targeted to targeted?
        return self.baseItem.targeted

    @property
    def effectRadius(self):
        """
        The radius of the effect that this consumable can generate.
        """
        radius = self.baseItem.effectRadius
        for modifier in self.modifiers:
            radius += modifier.effectRadius
        return radius

    @property
    def effectHitDie(self):
        """
        The HitDie of the effect that this consumable can generate.
        """
        nbr, die = self.baseItem.effectHitDie.split('d')
        nbr = int(nbr)
        for modifier in self.modifiers:
            nbr += modifier.effectHitDie
        return str(nbr) + 'd' + die

    @property
    def effectDuration(self):
        """
        The duration of the effect that this consumable can generate.
        """
        duration = self.baseItem.effectDuration
        for modifier in self.modifiers:
            duration += modifier.effectDuration
        return duration

    @property
    def effectElement(self):
        """
        The element of the effect that this consumable can generate.
        """
        element = self.baseItem.effectElement
        for modifier in self.modifiers:
            if modifier.effectElement is not None:
                element = modifier.effectElement
        return element

    @property
    def isConsumed(self):
        """
        Boolean indicating if this stack of consumable has been consumed completely
        """
        if self.stackSize == 0: return True
        return False
    
    #constructor
    def __init__(self, baseItem):
        """
        Creates a new uninitialized Consumable object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Consumable, self).__init__(baseItem)
        #consumables are stackable
        self._stackable = True
        # Effect will be created when item is consumed
        self._effect = None

    #functions
    def applyTo(self, target):
        """
        Applies the effect of this consumable to a target.
        The target can be several types of object, it depends on the
        specific Effect subclass.
        """
        if self.stackSize > 0:
            if self.baseItem.effect != '':
                effect_class = eval("Effects." + self.baseItem.effect)
                self._effect = effect_class and effect_class(self) or None
                if self.effect is not None:
                    self.effect.applyTo(target)
            self.stackSize -= 1

class QuestItem(Item):
    """
    Sub class for quest items
    Probably don't need this in the beginning but it would fit in here :)
    """
