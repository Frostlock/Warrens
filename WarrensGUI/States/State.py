__author__ = 'pi'

import pygame
from OpenGL import GL
from WarrensGUI.Util.Constants import *

class State(object):
    '''
    The State class represents a state of the GUI.
    '''

    @property
    def window(self):
        return self._window

    @property
    def parentState(self):
        return self._parentState

    def __init__(self, window, parent=None):
        '''
        Constructor
        '''
        self._window = window
        self._parentState = parent

    def mainLoop(self):
        '''
        Main loop that shows this state
        :return: None
        '''
        self.loop = True
        self.loopInit()
        while self.loop:
            # Clear the screen, and z-buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # Draw
            self.loopDraw()

            # Handle events
            self.loopEvents()

            # Show the screen
            pygame.display.flip()

    def loopInit(self):
        '''
        Part of the main loop, should be implemented by subclasses.
        :return:
        '''
        raise NotImplementedError()

    def loopDraw(self):
        '''
        Part of the main loop, should be implemented by subclasses.
        :return:
        '''
        raise NotImplementedError()

    def loopEvents(self):
        '''
        Part of the main loop, should be implemented by subclasses.
        :return:
        '''
        raise NotImplementedError()

    def drawMenu(self, header, items, selected):
        """
        Draws a menu on the screen
        we use an Orthographic projection and some older style opengl code
        This is not using Vertex Buffers.
        """
        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.window.displayWidth, self.window.displayHeight, 0.0, -1.0, 10.0)

        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)

        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        #TODO: Improve clarity of Orthographic projection? Can we map it to a projection plane equal to the screen dimensions? Not -1.0 to 1.0?
        # Background
        GL.glLoadIdentity()
        #GL.glTranslatef(-0.5, -0.5, 0)
        width = 0.8
        height = 0.8
        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(*COLOR_GL_MENU_BG)
        GL.glVertex2f(width, -height)
        GL.glVertex2f(width, height)
        GL.glVertex2f(-width, height)
        GL.glVertex2f(-width, -height)
        GL.glEnd()

        # Header
        GL.glLoadIdentity()
        self.window.drawText((-0.72, 0.72, 0), header, 24, COLOR_PG_HUD_TEXT)

        # Items
        heightOffset = 0
        for i in range(0, len(items)):
            if selected == i:
                color = COLOR_PG_HUD_TEXT_SELECTED
            else:
                color = COLOR_PG_HUD_TEXT
            position=(-0.6, 0.6 - heightOffset, 0)
            self.window.drawText(position, items[i], 20, color)
            heightOffset += 0.1