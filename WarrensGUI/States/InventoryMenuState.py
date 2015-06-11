__author__ = 'Frostlock'

import sys

import pygame

from WarrensGUI.States.State import MenuState
from WarrensGUI.States.TargetingState import TargetingState

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
            # try to target the item
            state = TargetingState(self.window, self.parentState, myItem)
            state.mainLoop()
            self.close()
        else:
            #try to use the item
            self.window.game.player.tryUseItem(myItem)
        # Something may have happened in the world
        self.window.refreshDynamicObjects()

        # Refresh items, keys and handlers
        self.items = []
        self.keys = []
        self.handlers = []
        for item in self.inventory.items:
            self.items.append(item.name)
            self.keys.append(pygame.K_RETURN)
            self.handlers.append(self.useItem)