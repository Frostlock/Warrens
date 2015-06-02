__author__ = 'Frostlock'

import sys

import pygame
from pygame.locals import *

from WarrensGUI.States.State import State
from WarrensGUI.States.DemoState import DemoState

class GameMenuState(State):
    '''
    State to show the main menu.
    '''

    def __init__(self, window, parentState=None):
        '''
        Constructor
        '''
        super(GameMenuState, self).__init__(window, parentState)

    def loopInit(self):
        #TODO: Replicate this approach in inventory and main menu states
        self.header = "Menu"
        self.items = ["s - Save Game",
                      "l - Load Game",
                      "q - Quit Game"]
        self.keys = [pygame.K_s,
                     pygame.K_l,
                     pygame.K_q]
        self.handlers = [self.saveGame,
                         self.loadGame,
                         self.quitGame]
        self.selected = 0

    def loopDraw(self):
        # Draw parent behind this inventory
        if self.parentState is not None: self.parentState.loopDraw()

        # Draw a menu with the items
        self.drawMenu(self.header, self.items, self.selected)

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)
            # keyboard events
            if event.type == pygame.KEYDOWN:
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
                    self.handlers[self.selected]()
                elif event.key in self.keys:
                    self.handlers[self.keys.index(event.key)]()
                elif event.key == pygame.K_ESCAPE:
                    self.close()

    def saveGame(self):
        print "called save"
        self.window.saveGame()
        self.close()

    def loadGame(self):
        print "called load"
        self.window.loadGame()
        self.close()

    def quitGame(self):
        self.close()
        self.parentState.close()
