__author__ = 'Frost'

import sys

import pygame
from pygame.locals import *

from WarrensGUI.States.State import State
from WarrensGUI.States.DemoState import DemoState

class MainMenuState(State):

    def __init__(self, window, parentState=None):
        '''
        Constructor
        '''
        super(MainMenuState, self).__init__(window, parentState)

    def loopInit(self):
        self.header = "Warrens - Main Menu"
        self.items = ["n - New Game",
                      "d - OpenGl demo (testing purposes)",
                      "l - Legacy Interface (PyGame only, no OpenGl)",
                      "q - Quit"]
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
                    if self.selected == 0:
                        self.window.playGame()
                    elif self.selected == 1:
                        self.window.state = DemoState(self.window, self)
                    elif self.selected == 2:
                        self.window.legacyGui()
                    elif self.selected == 3:
                        sys.exit()
                # New game
                elif event.key == pygame.K_n:
                    self.window.playGame()
                # OpenGl test
                elif event.key == pygame.K_d:
                    self.window.state = DemoState(self.window, self)
                # Legacy GUI
                elif event.key == pygame.K_l:
                    self.window.legacyGui()
                # Quit
                elif event.key == pygame.K_q:
                    sys.exit()
                # Leave state / Close
                elif event.key == pygame.K_ESCAPE:
                    self.loop = False
