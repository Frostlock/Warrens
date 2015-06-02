__author__ = 'Frostlock'

import sys

import pygame

from WarrensGUI.States.State import MenuState
from WarrensGUI.States.DemoState import DemoState

class MainMenuState(MenuState):
    '''
    State to show the main menu.
    '''

    def __init__(self, window, parentState=None):
        '''
        Constructor
        '''
        super(MainMenuState, self).__init__(window, parentState)

        self.header = "Warrens - Main Menu"
        self.items = ["n - New Game",
                      "l - Load Game",
                      "d - OpenGl demo (testing purposes)",
                      "i - Legacy Interface (PyGame only, no OpenGl)",
                      "q - Quit"]
        self.keys = [pygame.K_n,
                     pygame.K_l,
                     pygame.K_d,
                     pygame.K_i,
                     pygame.K_q]
        self.handlers = [self.window.playNewGame,
                         self.window.loadGame,
                         self.runDemoState,
                         self.window.legacyGui,
                         sys.exit]
        self.selected = 0

    def runDemoState(self):
        self.window.state = DemoState(self.window, self)

