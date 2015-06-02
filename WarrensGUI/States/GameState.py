__author__ = 'Frost'

import pygame
from pygame.locals import *

from WarrensGame.Game import Game
from WarrensGame.Actors import Character

from WarrensGUI.States.State import State
from WarrensGUI.States.InventoryState import InventoryState
from WarrensGUI.States.GameMenuState import GameMenuState

# Movement keys
MOVEMENT_KEYS = {
    pygame.K_h: (-1, +0),  # vi keys
    pygame.K_l: (+1, +0),
    pygame.K_j: (+0, -1),
    pygame.K_k: (+0, +1),
    pygame.K_y: (-1, +1),
    pygame.K_u: (+1, +1),
    pygame.K_b: (-1, -1),
    pygame.K_n: (+1, -1),
    pygame.K_KP4: (-1, +0),  # numerical keypad
    pygame.K_KP6: (+1, +0),
    pygame.K_KP2: (+0, -1),
    pygame.K_KP8: (+0, +1),
    pygame.K_KP7: (-1, +1),
    pygame.K_KP9: (+1, +1),
    pygame.K_KP1: (-1, -1),
    pygame.K_KP3: (+1, -1),
}

class GameState(State):
    '''
    State to show a game in progress.
    '''

    def __init__(self, window, parentState):
        '''
        Constructor
        '''
        super(GameState, self).__init__(window, parentState)


    def loopInit(self):
        #self.centerCameraOnActor(self.game.player)
        self.window.setCameraCenterOnMap()

    def loopDraw(self):
        # Refresh the actors VAO (some actors might have moved)
        self.window.refreshDynamicObjects()
        # Redraw window
        self.window.drawAll()

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)

        # handle game events
        self.window.playGame()

    def handlePyGameEvent(self, event):
        # Call super class event handler
        super(GameState, self).handlePyGameEvent(event)
        # mouse
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.window.eventDraggingStart()
            elif event.button == 3:
                self.window.eventRotatingStart()
            elif event.button == 4:
                self.window.eventZoomIn()
            elif event.button == 5:
                self.window.eventZoomOut()
        elif event.type == MOUSEMOTION:
            self.window.eventMouseMovement()
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.window.eventDraggingStop()
            elif event.button == 3:
                self.window.eventRotatingStop()

        # keyboard
        elif event.type == pygame.KEYDOWN:
            # Handle keys that are always active
            if event.key == pygame.K_ESCAPE:
                # Show game menu
                GameMenuState(self.window,self).mainLoop()
            elif event.key == pygame.K_v:
                self.window.cycleCameraMode()

            #TODO: these should keep working while key is still pressed
            elif event.key == pygame.K_UP:
                self.window.cameraDistance -= 0.1
            elif event.key == pygame.K_DOWN:
                self.window.cameraDistance += 0.1
            elif event.key == pygame.K_RIGHT:
                self.window.cameraAngleXY -= 1
            elif event.key == pygame.K_LEFT:
                self.window.cameraAngleXY += 1
            elif event.key == pygame.K_PAGEDOWN:
                self.window.cameraAngleXZ -= 1
            elif event.key == pygame.K_PAGEUP:
                self.window.cameraAngleXZ += 1

            # Handle keys that are active while playing
            if self.window.game.state == Game.PLAYING:
                player = self.window.game.player
                if player.state == Character.ACTIVE:
                    # movement
                    global MOVEMENT_KEYS
                    if event.key in MOVEMENT_KEYS:
                        player.tryMoveOrAttack(*MOVEMENT_KEYS[event.key])
                    # portal keys
                    elif event.key == pygame.K_LESS:
                        # check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                            player.tryFollowPortalDown()
                        else:
                            player.tryFollowPortalUp()
                    # inventory
                    elif event.key == pygame.K_i:
                        state = InventoryState(self, self, player.inventory)
                        state.mainLoop()
                    elif event.key == pygame.K_d:
                        raise NotImplementedError()
                    # interact
                    elif event.key == pygame.K_COMMA:
                        player.tryPickUp()
