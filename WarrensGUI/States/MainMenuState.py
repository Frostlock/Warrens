__author__ = 'Frost'

import sys

import pygame
from pygame.locals import *

from WarrensGUI.States.State import State

class MainMenuState(State):

    def __init__(self, window, parentState=None):
        '''
        Constructor
        '''
        super(MainMenuState, self).__init__(window, parentState)

    def loopInit(self):
        self.header = "Warrens - Main Menu"
        self.items = ["n - New Game",
                      "t - OpenGl test",
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
            # Quit
            if event.type == pygame.QUIT:
                sys.exit()
            # Window resize
            elif event.type == VIDEORESIZE:
                self.resizeWindow(event.dict['size'])
            # keyboard
            elif event.type == pygame.KEYDOWN:
                # Select up
                if event.key == pygame.K_UP:
                    selected -= 1
                    if selected < 0 : selected = 0
                # Select down
                elif event.key == pygame.K_DOWN:
                    selected += 1
                    if selected > len(items)-1: selected = len(items) - 1
                # Select
                elif event.key == pygame.K_RETURN:
                    if selected == 0:
                        self.playGame()
                    elif selected == 1:
                        self.playTest()
                    elif selected == 2:
                        self.legacyGui()
                    elif selected == 3:
                        sys.exit()
                # New game
                elif event.key == pygame.K_n:
                    self.window.playGame()
                # OpenGl test
                elif event.key == pygame.K_t:
                    self.window.playTest()
                # Legacy GUI
                elif event.key == pygame.K_l:
                    self.window.legacyGui()
                # Quit
                elif event.key == pygame.K_q:
                    sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    sys.exit()
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
                    if selected == 0:
                        self.playGame()
                    elif selected == 1:
                        self.playTest()
                    elif selected == 2:
                        self.legacyGui()
                    elif selected == 3:
                        sys.exit()
                # New game
                elif event.key == pygame.K_n:
                    self.playGame()
                # OpenGl test
                elif event.key == pygame.K_t:
                    self.playTest()
                # Legacy GUI
                elif event.key == pygame.K_l:
                    self.legacyGui()
                # Quit
                elif event.key == pygame.K_q:
                    sys.exit()
                # Close
                elif event.key == pygame.K_ESCAPE:
                    self.loop = False
