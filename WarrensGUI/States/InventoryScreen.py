__author__ = 'pi'

import sys

import pygame
from pygame.locals import *

from WarrensGUI.States.State import State

class InventoryScreen(State):

    @property
    def inventory(self):
        return self._inventory

    def __init__(self, window, parentState, inventory):
        '''
        Constructor
        '''
        super(InventoryScreen, self).__init__(window, parentState)
        self._inventory = inventory

    def loopInit(self):
        self.header = "Inventory"
        self.selected = 0

    def loopDraw(self):
        # Draw parent behind this inventory
        if self.parentState is not None: self.parentState.loopDraw()

        # Refresh items from inventory
        self.items = []
        for item in self.inventory.items:
            self.items.append(item.name)

        # Draw a menu with the items
        self.drawMenu(self.header, self.items, self.selected)

    def loopEvents(self):
        # handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                # Quit Program
                if event.type == pygame.QUIT:
                    sys.exit()
                # Window resize
                elif event.type == VIDEORESIZE:
                    self.resizeWindow(event.dict['size'])
                # keyboard
                elif event.type == pygame.KEYDOWN:
                    # Select up
                    if event.key == pygame.K_UP:
                        self.selected -= 1
                        if self.selected < 0 : self.selected = 0
                    # Select down
                    elif event.key == pygame.K_DOWN:
                        self.selected += 1
                        if self.selected > len(self.items)-1: self.selected = len(self.items) - 1
                    # Select
                    elif event.key == pygame.K_RETURN:
                        useItem = self.inventory.items[self.selected]
                        if useItem.targeted:
                            # TODO: targeting to be implemented
                            # self.eventTargetingStart(useItem)
                            raise NotImplementedError()
                        else:
                            #try to use the item
                            self.window.game.player.tryUseItem(useItem)
                    # Close
                    elif event.key == pygame.K_ESCAPE:
                        self.loop = False