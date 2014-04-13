#!/usr/bin/python

#from Maps import Tile

import random
import Utilities
import CONSTANTS
import Effects #this is used in an eval statement
import AI
import Inventory

##########
# ACTORS #
##########
class Actor(object):
    """
    Base class for everything that can occur in the gameworld.
    Example sub classes: Items and Characters.
    """
    #Frostlock: I'm not completely happy with the name Actor but haven't
    # found anything better yet :-)
    # Also I added hitpoints on this level, every Actor can be destroyed,
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

    @property
    def char(self):
        """
        Returns a 1 char shorthand for this actor.
        """
        return self._char

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
    def maxHitPoints(self):
        """
        Maximum hitpoints of this Character (overrides Actor)
        """
        bonus = 0
        #TODO medium:
        #return actual max_hp, by summing up the bonuses from all equipped items
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

    #Constructor
    def __init__(self):
        """
        Creates a new basic Actor, normally not used directly but should
        be called by subclasses.
        """
        #initialize class properties
        self._baseMaxHitPoints = 1
        self._char = '?'
        self._currentHitPoints = 1
        self._id = 'not set'
        self._name = 'Nameless'
        self._tile = None
        self._level = None
        self._color = (255, 255, 255)
        self._inView = False

    #functions
    def __str__(self):
        return self._name + " " + super(Actor, self).__str__()

    def registerWithLevel(self, level):
        """
        This function registers this actor with the provided level.
        It has to be overridden in the Actor subclasses to ensure that the
        actor correctly registers with the level.
        """
        raise Utilities.GameError('Missing implementation registerWithLevel()')

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
            Utilities.clamp(targetX, 0, self.tile.map.width)
            Utilities.clamp(targetY, 0, self.tile.map.height)
            #move
            self.moveToTile(self.level.map.tiles[targetX][targetY])

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
        distance = Utilities.distanceBetween(self, targetActor)
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

class Portal(Actor):
    """
    This class can be used to represent portals in and out of a level
    """
    _message = ''

    @property
    def message(self):
        """
        In game message that should be displayed when portal is used.
        """
        return self._message

    _destination = None

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
        self._color = (191, 0, 255)

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


##############
# CHARACTERS #
##############
class Character(Actor):
    """
    Base class for characters that can move around and interact
    Should probably not be instatiated but describes the general interface of
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
    def xpValue(self):
        """
        Return xp value
        """
        return self._xpValue

    @property
    def power(self):
        """
        Return attack power
        """
        bonus = 0
        for item in self.equipedItems:
            bonus += int(item.powerBonus)
        return self._basePower + bonus

    @property
    def defense(self):
        """
        Return defense value
        """
        bonus = 0
        for item in self.equipedItems:
            bonus += int(item.defenseBonus)
        return self._baseDefense + bonus

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
        self._baseDefense = 0
        self._basePower = 1
        self._equipedItems = []
        self._inventory = Inventory.Inventory()
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
                Utilities.message(self.name.capitalize() + ' equips a '
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
            Utilities.message(self.name.capitalize() + ' unequips a '
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
        Utilities.message(self.name.capitalize() + ' picks up a '
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
        Utilities.message(self.name.capitalize() + ' drops a '
                    + item.name + '.', "GAME")

    def attack(self, target):
        """
        Attack another Character
        Arguments
            target - the Character to be attacked
        """
        #a simple formula for attack damage
        damage = self.power - target.defense

        if damage > 0:
            Utilities.message(self.name.capitalize() + ' attacks '
                    + target.name + ' for ' + str(damage) + ' Damage.', "GAME")
            target.takeDamage(damage, self)
        else:
            Utilities.message(self.name.capitalize() + ' attacks '
                    + target.name + ' but it has no effect!', "GAME")

    def takeDamage(self, amount, attacker):
        """
        function to take damage from an attacker
        arguments
           damage - the incoming damage
           attacker - the attacking Actor
        """
        #apply damage if possible
        if amount > 0:
            self.currentHitPoints -= amount
        #check for death
        if self.currentHitPoints < 0:
            Utilities.message(self.name.capitalize() + ' is killed!', "GAME")
            self._killedBy(attacker)

    def _killedBy(self, attacker):
        """
        This function handles the death of this Character
        """
        if type(attacker) is Player:
            #yield experience to the player
            Utilities.message(attacker.name + ' gains ' + str(self.xpValue) + ' XP.', "GAME")
            attacker.gainXp(self.xpValue)
        if type(attacker) is Monster:
            if attacker.killedByText != '':
                Utilities.message(attacker.killedByText, "GAME")
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
            Utilities.message(self.name.capitalize() + ' gains '
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
        return CONSTANTS.LEVEL_UP_BASE + self.playerLevel * CONSTANTS.LEVEL_UP_FACTOR

    @property
    def playerLevel(self):
        """
        Returns the current level of the player.
        """
        return self._playerLevel

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
        self._baseDefense = 2
        self._basePower = 5
        self._xpValue = 1
        self._AI = None
        #Player properties
        self._xp = 0
        self._playerLevel = 1

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
        Utilities.message("You feel stronger!", "GAME")
        self._playerLevel += 1
        self._baseMaxHitPoints += 10
        self._baseDefense += 1
        self._basePower += 1
         
    def gainXp(self, amount):
        """
        Increase xp of this player with the given amount
        arguments
            amount - integer
        """
        self._xp += amount
        #check for level up
        if self.xp >= self.nextLevelXp:
            self.levelUp()

    def followPortal(self, portal):
        """
        Send player through specified portal.
        """
        #Game message
        Utilities.message(portal.message, "GAME")
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
        """
        #the coordinates the player is moving to/attacking
        x = self.tile.x + dx
        y = self.tile.y + dy
        targetTile = self.level.map.tiles[x][y]

        #try to find an attackable actor there
        target = None
        for a in targetTile.actors:
            #only attack monsters
            if type(a) is Monster:
                #don't attack dead monsters
                if a.state != Character.DEAD:
                    target = a

        #attack if target found, move otherwise
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

    def tryPickUp(self):
        """
        Player attempts to pick up something on the current location.
        This function is meant to be called from the GUI.
        """
        #check if there is an item on the current tile
        for a in self.tile.actors:
            if isinstance(a, Item):
                self.pickUpItem(a)

    def tryUseItem(self, item, target=None):
        """
        Player attempts to use an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Consumable):
            #try to use the consumable
            if item.effect is not None and item.isConsumed is False:
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
            raise Utilities.GameError("Missing implementation to use item")

    def tryDropItem(self, item):
        """
        Player attempts to drop an item.
        This function is meant to be called from the GUI.
        """
        if isinstance(item, Equipment):
            if item.isEquiped:
                Utilities.message("You can't drop an equiped item.")
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

    #Class variables
    _flavorText = "Flavor text not set"

    @property
    def flavorText(self):
        """
        Fancy description of the monster.
        """
        return self._flavorText

    _killedByText = "Killed by text not set"

    @property
    def killedByText(self):
        """
        Killed by message that can be shown if this monster kills the player.
        """
        return self._killedByText

    #constructor
    def __init__(self, monster_data):
        """
        Creates a new uninitialized Monster object.
        Use MonsterLibrary.createMonster() to create an initialized Monster.
        """
        #call super class constructor
        #(ensure instance gets unique copies of class variables)
        super(Monster, self).__init__()
        
        #Actor components
        self._id = monster_data['key']
        self._char = monster_data['char']
        self._baseMaxHitPoints = Utilities.rollHitDie(monster_data['hitdie'])
        self._currentHitPoints = self._baseMaxHitPoints
        self._name = monster_data['name']
        self._color = eval(monster_data['color'])

        #Character components
        self._baseDefense = int(monster_data['defense'])
        self._basePower = int(monster_data['power'])
        self._xpValue = int(monster_data['xp'])
        #gets a class object by name; and instanstiate it if not None
        ai_class = eval('AI.' + monster_data['ai'])
        self._AI = ai_class and ai_class(self) or None

        #Monster components
        self._flavorText = monster_data['flavor']
        self._killedByText = monster_data['killed_by']



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
    def name(self):
        '''
        Name of this Item, overrides base class implementation to deal stack names.
        '''
        if self.stackable and self.stackSize > 1:
            return self._name + ' stack (' + str(self.stackSize) + ')'
        else:
            return self._name
    
    def registerWithLevel(self, level):
        """
        Makes the level aware that this item is on it.
        """
        level.addItem(self)

    #constructor
    def __init__(self, item_data):
        """
        Creates a new Item object, normally not used directly but called
        by sub class constructors.
        """
        #call super class constructor
        super(Item, self).__init__()
        #Initialize Item components
        self._id = item_data['key']
        self._char = item_data['char']
        self._baseMaxHitPoints = 1
        self._currentHitPoints = self._baseMaxHitPoints
        self._name = item_data['name']
        #Basic items are not stackable
        self._stackable = False
        self.stackSize = 1

class Equipment(Item):
    """
    Sub class for equipment = items that can be equiped
    Might need more subclasses for weapons versus armor
    """

    _defenseBonus = 0

    @property
    def defenseBonus(self):
        """
        The defense bonus of this piece of equipment
        """
        return self._defenseBonus

    _powerBonus = 0

    @property
    def powerBonus(self):
        """
        The power bonus of this piece of equipment
        """
        return self._powerBonus

    _isEquiped = False

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
    def __init__(self, item_data):
        """
        Creates a new uninitialized Equipment object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Equipment, self).__init__(item_data)
        #Initialize equipment properties
        self._defenseBonus = item_data['defense_bonus']
        self._powerBonus = item_data['power_bonus']
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
        return self._effect

    @property
    def effectColor(self):
        """
        The effect that this consumable can generate.
        """
        return self._effectColor

    @property
    def targeted(self):
        """
        Boolean that indicates whether this consumable is targeted.
        """
        if self.effect is None: 
            return False
        else:
            return self.effect.targeted
    
    @property
    def isConsumed(self):
        """
        Boolean indicating if this stack of consumable has been consumed completely
        """
        if self.stackSize == 0: return True
        return False
    
    #constructor
    def __init__(self, item_data):
        """
        Creates a new uninitialized Consumable object.
        Use ItemLibrary.createItem() to create an initialized Item.
        """
        #call super class constructor
        super(Consumable, self).__init__(item_data)
        #consumables are stackable
        self._stackable = True
        #consumables usually have an effect
        if item_data['effect'] != '':
            effect_class = eval("Effects." + item_data['effect'])
            self._effect = effect_class and effect_class(self, item_data) or None
        else:
            self._effect = None

    #functions
    def applyTo(self, target):
        """
        Applies the effect of this consumable to a target.
        The target can be several types of object, it depends on the
        specific Effect subclass.
        """
        if self.stackSize > 0:
            if self.effect is not None:
                self.effect.applyTo(target)
            self.stackSize -= 1

class QuestItem(Item):
    """
    Sub class for quest items
    Probably don't need this in the beginning but it would fit in here :)
    """
