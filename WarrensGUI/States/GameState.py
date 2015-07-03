__author__ = 'Frost'

import pygame
from pygame.locals import *

from WarrensGame.Game import Game
from WarrensGame.Actors import Character

from WarrensGUI.States.State import State
from WarrensGUI.States.InventoryMenuState import InventoryMenuState
from WarrensGUI.States.GameMenuState import GameMenuState
from WarrensGUI.States.InteractionState import InteractionState
from WarrensGUI.Util.Constants import *

class GameState(State):
    '''
    State to show a game in progress.
    '''

    def __init__(self, window, parentState):
        '''
        Constructor
        '''
        super(GameState, self).__init__(window, parentState)
        # To keep track how long keys are pressed
        self.pressedTimes = {}
        for pygameKey in MOVEMENT_KEYS.keys():
            self.pressedTimes[pygameKey] = 0

    def loopInit(self):
        self.window.setCameraCenterOnActor(self.window.game.player)
        #self.window.setCameraCenterOnMap()

    def loopDraw(self):
        # Animate every frame
        self.window.animateDynamicObjects()
        # Redraw window
        self.window.drawAll()

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)

        # Handle keys that stay pressed
        self.handlePressedKeys()

        # Handle game events
        self.window.progressGame()

    def handlePressedKeys(self):
        pressed = pygame.key.get_pressed()

        #camera movement
        if pressed[pygame.K_UP]:
            self.window.cameraDistance -= 0.1
        if pressed[pygame.K_DOWN]:
            self.window.cameraDistance += 0.1
        if pressed[pygame.K_RIGHT]:
            self.window.cameraAngleXY -= 1
        if pressed[pygame.K_LEFT]:
            self.window.cameraAngleXY += 1
        if pressed[pygame.K_PAGEDOWN]:
            self.window.cameraAngleXZ -= 1
        if pressed[pygame.K_PAGEUP]:
            self.window.cameraAngleXZ += 1

        #player movement
        if self.window.game.state == Game.PLAYING:
            player = self.window.game.player
            if player.state == Character.ACTIVE:
                # movement
                global MOVEMENT_KEYS
                for pygameKey in MOVEMENT_KEYS.keys():
                    if pressed[pygameKey]:
                        self.pressedTimes[pygameKey] += 1
                        frames = self.window.clock.get_fps()
                        # Move once on the first press
                        if self.pressedTimes[pygameKey] == 1:
                            player.tryMoveOrAttack(*MOVEMENT_KEYS[pygameKey])
                        # Start moving continually after 1 second
                        elif self.pressedTimes[pygameKey] > frames:
                            player.tryMoveOrAttack(*MOVEMENT_KEYS[pygameKey])
                    else:
                        #reset pressed timer
                        self.pressedTimes[pygameKey] = 0
            # React to player death
            elif player.state == Character.DEAD:
                self.window.cameraMode = CAM_ISOMETRIC
                self.window.cameraAngleXY += 1
                self.window.cameraDistance -= 0.05

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

            # Handle keys that are active while playing
            if self.window.game.state == Game.PLAYING:
                player = self.window.game.player
                if player.state == Character.ACTIVE:
                    # portal keys
                    if event.key == pygame.K_LESS:
                        # check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                            player.tryFollowPortalDown()
                        else:
                            player.tryFollowPortalUp()
                    # inventory
                    elif event.key == pygame.K_i:
                        state = InventoryMenuState(self.window, self, player.inventory)
                        state.mainLoop()
                    elif event.key == pygame.K_d:
                        raise NotImplementedError()
                    # interact
                    elif event.key == pygame.K_COMMA:
                        interaction = player.tryInteract()
                        if not interaction is None:
                            state = InteractionState(self.window, self, interaction)
                            state.mainLoop()
                        self.window.refreshDynamicObjects()
                    # select
                    elif event.key == pygame.K_TAB:
                         # check for shift modifier
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT):
                            self.window.selectPreviousSceneObject()
                        else:
                            self.window.selectNextSceneObject()