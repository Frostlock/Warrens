__author__ = 'Frostlock'

import sys

import pygame

from WarrensGUI.States.State import MenuState

class GameMenuState(MenuState):
    """
    State to show the game menu.
    """

    def __init__(self, window, parentState):
        """
        Constructor
        :param window:
        :param parentState: GameMenuState requires a GameState parent
        :return: GameMenuState object
        """
        super(GameMenuState, self).__init__(window, parentState)

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

    def saveGame(self):
        self.window.saveGame()
        self.close()

    def loadGame(self):
        self.window.loadGame()
        self.close()

    def quitGame(self):
        self.close()
        self.parentState.close()
