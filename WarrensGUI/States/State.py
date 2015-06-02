__author__ = 'Frostlock'

import sys

import pygame
from pygame.locals import *

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

    @parentState.setter
    def parentState(self, state):
        self._parentState = state

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

    def close(self):
        self.loop = False
        #self.window.state = self.parentState

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

    def handlePyGameEvent(self, event):
        # Quit
        if event.type == pygame.QUIT:
            sys.exit()
        # Window resize
        elif event.type == VIDEORESIZE:
            self.window.resizeWindow(event.dict['size'])

class MenuState(State):
    """
    Utility state to show a menu.
    """
    def __init__(self, window, parentState=None):
        """
        Constructor
        :param window:
        :param parentState:
        :return: MenuState object
        """
        super(MenuState, self).__init__(window, parentState)

    def loopInit(self):
        #Nothing to be done but need to override super class method to avoid error messsage.
        pass

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