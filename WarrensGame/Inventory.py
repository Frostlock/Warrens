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
            #Check if there is another item with the same ID
            existingItem = self.find(newItem.id)
            if existingItem is None:
                #If there is no existing item just add the new one
                self.items.append(newItem)
                #TODO: Problem here: Items with different modifiers should not stack!
                #TODO: Problem here: Modifiers on first item apply to entire stack
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

    def find(self, itemID):
        '''
        Search this inventory for an item with the specified itemID.
        Returns None if the item is not found
        '''
        for item in self.items:
            if item.id == itemID:
                return item
        return None
