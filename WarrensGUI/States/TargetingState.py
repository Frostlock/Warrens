__author__ = 'Frostlock'

import sys

from OpenGL import GL
from WarrensGUI.Util.Constants import *
from WarrensGame.Actors import Actor
import pygame

from WarrensGUI.States.State import State

class TargetingState(State):
    """
    State that allows targeting.
    """
    @property
    def selectedTarget(self):
        return self._selectedTarget

    @selectedTarget.setter
    def selectedTarget(self,target):
        self._selectedTarget = target

    def __init__(self, window, parentState, seeker):
        """
        Constructor
        :param window: 
        :param parentState: 
        :param seeker: the object that is looking for a target
        :return:
        """
        super(TargetingState, self).__init__(window, parentState)
        
        self.seeker = seeker
        self.header = "Select target for " + str(self.seeker.name)
        self._selectedTarget = None

    def loopInit(self):
        # Determine available targets
        self.targets = self.window.game.getPossibleTargets(self.seeker)
        if len(self.targets) == 0:
            self.close()
        elif len(self.targets) == 1:
            self.resolve(self.targets[0])
        else:

            # To enable mouse based selection, calculate a selection area for each possible target
            self.targetRectangles = []
            for target in self.targets:
                # Can only target items that are visible in the GUI.
                if not target.sceneObject is None:
                    targetRect = self.window.getScreenRectangle(target.sceneObject)
                    self.targetRectangles.append(targetRect)

            # To enable TAB based selection, create a list of actor targets
            self.actorTargets = []
            for target in self.targets:
                if isinstance(target, Actor):
                    self.actorTargets.append(target)
            if len(self.actorTargets) == 0:
                self.selected = None
            else:
                self.selected = 0

    def loopDraw(self):
        # Draw parent behind this inventory
        if self.parentState is not None: self.parentState.loopDraw()

        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.window.displayWidth, self.window.displayHeight, 0.0, -1.0, 10.0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # Draw header
        GL.glLoadIdentity()
        self.window.drawText((-0.85, 0.85, 0), self.header, FONT_HUD_XXL, COLOR_PG_HUD_TEXT_SELECTED)

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)
            # mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Try to select a an object based on the mouse position
                    target = self.selectedTarget
                    if not target is None: self.resolve(target)
            elif event.type == pygame.MOUSEMOTION:
                self.handleMouseMotion()
            # keyboard events
            elif event.type == pygame.KEYDOWN:
               # Select up
                if event.key == pygame.K_TAB:
                    self.actorTargets[self.selected].sceneObject.selected = False
                    # check for shift modifier
                    mods = pygame.key.get_mods()
                    if (mods & pygame.KMOD_LSHIFT) or (mods & pygame.KMOD_RSHIFT):
                        self.selected -= 1
                        if self.selected < 0 : self.selected = len(self.actorTargets) - 1
                        self.actorTargets[self.selected].sceneObject.selected = True
                    else:
                        self.selected += 1
                        if self.selected > len(self.actorTargets)-1: self.selected = 0
                        self.actorTargets[self.selected].sceneObject.selected = True
                # Select
                elif event.key == pygame.K_RETURN:
                    if not self.selected is None:
                        target = (self.actorTargets[self.selected])
                        self.resolve(target)
                elif event.key == pygame.K_ESCAPE:
                    self.close()

    def resolve(self, target):
        self.window.game.player.tryUseItem(self.seeker, target)
        self.close()

    def handleMouseMotion(self):
        # Unselect all targets
        for target in self.targets:
            if not target.sceneObject is None:
                target.sceneObject.selected = False
        # Get mouse position
        mousePos = pygame.mouse.get_pos()
        # Check if mouse position is in one of the item rectangles
        for i in range(0, len(self.targetRectangles)):
            if self.targetRectangles[i].collidepoint(mousePos):
                self.selectedTarget = self.targets[i]
                #print str(item) + " " + str(mousePos) + " collides with " + str(self.itemRectangles[i])
                self.selected = i
                if not self.selectedTarget.sceneObject is None:
                    self.selectedTarget.sceneObject.selected = True
                    # Refresh mesh (without waiting for animation to refresh it)
                    self.selectedTarget.sceneObject.refreshMesh()
                    self.window.selectedObject = self.selectedTarget.sceneObject
                    break
        # Attention:
        #
        # You should not call
        # self.window.refreshStaticObjects()
        # self.window.loadVAOStaticObjects()
        # these kill performance as they would trigger whenever the mouse goes over a tile.
        #
        # You should not call
        # self.window.refreshStaticObjects()
        # self.window.refreshDynamicObjects()
        # This will create new scene objects (voiding the ones we just did the effort to select.

