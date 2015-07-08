'''
Created on Apr 13, 2014

@author: pi
'''

class Inventory(object):
    '''
    This class represents an inventory of Items.
    It will stack incoming items if they are stackable.
    '''

    @property
    def items(self):
        '''
        Basic array of all items in this inventory
        '''
        return self._items

    @property
    def owner(self):
        '''
        The character that owns this inventory
        '''
        return self._owner

    def __init__(self, character):
        '''
        Constructor
        '''
        self._items = []
        self._owner = character
        
    def add(self,newItem):
        '''
        Add an item to this inventory
        '''
        newItem.owner = self.owner
        #if item is stackable
        if newItem.stackable:
            #Check if there is an identical item
            existingItem = self.find(newItem)
            if existingItem is None:
                #If there is no existing item just add the new one
                self.items.append(newItem)
            else:
                #Item already exists, increase the stack with one
                existingItem.stackSize +=1
        else:
            #Add non stackable item
            self.items.append(newItem)
    
    def remove(self, removeItem):
        '''
        Remove an item from this inventory
        '''
        self.items.remove(removeItem)

    def find(self, item):
        '''
        Search this inventory for the specified item. with the specified itemID.
        Matching is done based on itemID and modifierIDs.
        Returns None if the item is not found
        '''
        for availableItem in self.items:
            # Same base item
            if availableItem.key == item.key:
                availableModKeys = [mod.key for mod in availableItem.modifiers]
                itemModKeys = [mod.key for mod in item.modifiers]
                # TODO: sort itemModKeys and availableModKeys alphabetically
                if str(availableModKeys) == str(itemModKeys):
                    return availableItem
        return None
