__author__ = 'Frostlock'

import sys

import pygame

from WarrensGUI.States.State import MenuState

class InventoryMenuState(MenuState):
    """
    State to show inventory menu.
    """

    def __init__(self, window, parentState, inventory):
        """
        Constructor
        :param window: 
        :param parentState: 
        :param inventory: 
        :return:
        """
        super(InventoryMenuState, self).__init__(window, parentState)
        
        self.inventory = inventory
        self.header = "Inventory"
        self.items = []
        self.keys = []
        self.handlers = []
        for item in self.inventory.items:
            self.items.append(item.name)
            self.keys.append(pygame.K_RETURN)
            self.handlers.append(self.useItem)
        self.selected = 0

    def useItem(self):
        myItem = self.inventory.items[self.selected]
        if myItem.targeted:
            # TODO: targeting to be implemented
            # self.eventTargetingStart(useItem)
            raise NotImplementedError()
        else:
            #try to use the item
            self.window.game.player.tryUseItem(myItem)

        # Refresh items, keys and handlers
        self.items = []
        self.keys = []
        self.handlers = []
        for item in self.inventory.items:
            self.items.append(item.name)
            self.keys.append(pygame.K_RETURN)
            self.handlers.append(self.useItem)