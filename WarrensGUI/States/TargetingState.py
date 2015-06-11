__author__ = 'Frostlock'

import sys

from OpenGL import GL
from WarrensGUI.Util.Constants import *
from WarrensGame.Effects import EffectTarget
import pygame

from WarrensGUI.States.State import State

class TargetingState(State):
    """
    State that allows targetting.
    """

    #TODO: enable targeting of actors
    #TODO: enable targeting of tiles

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


    def loopInit(self):
        #Nothing to be done but need to override super class method to avoid error messsage.
        pass

    def loopDraw(self):
        # Draw parent behind this inventory
        if self.parentState is not None: self.parentState.loopDraw()

        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.window.displayWidth, self.window.displayHeight, 0.0, -1.0, 10.0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        # # Background
        # GL.glLoadIdentity()
        # width = 0.8
        # height = 0.8
        # GL.glBegin(GL.GL_QUADS)
        # GL.glColor4f(*COLOR_GL_MENU_BG)
        # GL.glVertex2f(width, -height)
        # GL.glVertex2f(width, height)
        # GL.glVertex2f(-width, height)
        # GL.glVertex2f(-width, -height)
        # GL.glEnd()

        # Header
        GL.glLoadIdentity()
        self.window.drawText((-0.85, 0.85, 0), self.header, FONT_HUD_XXL, COLOR_PG_HUD_TEXT_SELECTED)

        # # Items
        # heightOffset = 0
        # for i in range(0, len(items)):
        #     if selected == i:
        #         color = COLOR_PG_HUD_TEXT_SELECTED
        #     else:
        #         color = COLOR_PG_HUD_TEXT
        #     position=(-0.6, 0.6 - heightOffset, 0)
        #     self.window.drawText(position, items[i], FONT_HUD_XL, color)
        #     heightOffset += 3 * FONT_HUD_XL_HEIGHT / float(self.window.displayHeight)

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)
            # mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.handleMouseClick()
            # keyboard events
            if event.type == pygame.KEYDOWN:
                #TODO: keyboard targetting, iterate over visible candidate targets
               # Select up
                if event.key == pygame.K_UP:
                    self.selected -= 1
                    if self.selected < 0 : self.selected = len(self.items) - 1
                # Select down
                elif event.key == pygame.K_DOWN:
                    self.selected += 1
                    if self.selected > len(self.items)-1: self.selected = 0
                # Select
                elif event.key == pygame.K_RETURN:
                    pass
                elif event.key == pygame.K_ESCAPE:
                    self.close()

    def handleMouseClick(self):
        # Try to select a an object based on the mouse position
        mousePos = pygame.mouse.get_pos()
        target = self.window.selectSceneObject(mousePos)
        # Object found
        if not target is None:
            #TODO: switch base on TargetType however target type is in the effect object and that only is created on apply...
            #if self.seeker.effect.targetType == EffectTarget.CHARACTER:
            self.window.game.player.tryUseItem(self.seeker, target)
            #elif self.seeker.effect.targetType == EffectTarget.TILE:
            #    self.window.game.player.tryUseItem(self.seeker, target.tile)
            #else:
            #    raise NotImplementedError("Unknown target type.")
            # Targeting completed
            self.close()