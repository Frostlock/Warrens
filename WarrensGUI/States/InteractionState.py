__author__ = 'Frostlock'

import pygame
from pygame.locals import *
from OpenGL import GL

from WarrensGUI.Hud import *
from WarrensGUI.States.State import State
from WarrensGUI.Util.Constants import *
from WarrensGame.CONSTANTS import *

class InteractionState(State):

    @property
    def interaction(self):
        return self._interaction

    """
    Utility state to handle game interactions.
    """
    def __init__(self, window, parentState, interaction):
        """
        Constructor
        :param window:
        :param parentState:
        :return: MenuState object
        """
        super(InteractionState, self).__init__(window, parentState)

        self._interaction = interaction

    def loopInit(self):
        #Nothing to be done but need to override super class method to avoid error messsage.
        pass

    def loopDraw(self):
        # Draw parent behind this inventory
        if self.parentState is not None: self.parentState.loopDraw()

        # Get the relevant interface surface for interaction type
        if self.interaction.type == INTERACTION_CONTAINER:
            interfaceSurface = self.containerInteraction()
        else:
            raise NotImplementedError("Unknown interaction type.")

        # Draw the surface
        self.drawSurface(interfaceSurface)

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)
        #     # keyboard events
        #     if event.type == pygame.KEYDOWN:
        #        # Select up
        #         if event.key == pygame.K_UP:
        #             self.selected -= 1
        #             if self.selected < 0 : self.selected = len(self.items) - 1
        #         # Select down
        #         elif event.key == pygame.K_DOWN:
        #             self.selected += 1
        #             if self.selected > len(self.items)-1: self.selected = 0
        #         # Select
        #         elif event.key == pygame.K_RETURN:
        #             self.handlers[self.selected]()
        #         elif event.key in self.keys:
        #             self.handlers[self.keys.index(event.key)]()
        #         elif event.key == pygame.K_ESCAPE:
        #             self.close()

    def containerInteraction(self):
        """
        Returns a pygame surface for the on-going interaction
        """
        # TODO: Optimize performance, move some of this code into the loopInit function
        self.clearMouseHandlers()

        # Use a transparent surface with the same size as the screen to allow alignment between mouse clicks and button rectangles
        width = self.window.displayWidth
        height = self.window.displayHeight
        mainSurf = pygame.Surface((width,height), SRCALPHA)
        xOffsetOuter = self.window.displayWidth / 6
        yOffsetOuter = self.window.displayHeight / 6

        # Main box and border
        boxWidth = self.window.displayWidth - 2 * xOffsetOuter
        boxHeight = self.window.displayHeight - 2 * yOffsetOuter
        mainRect = pygame.Rect(xOffsetOuter,yOffsetOuter,boxWidth,boxHeight)
        mainSurf.fill(COLOR_PG_HUD_BACKGROUND, mainRect)
        pygame.draw.rect(mainSurf, COLOR_PG_HUD_BORDER, mainRect, BORDER_SIZE)
        xOffset = xOffsetOuter + BORDER_SIZE + SPACE_INNER
        yOffset = yOffsetOuter + BORDER_SIZE + SPACE_INNER

        # Container name
        textSurf = FONT_HUD_L.render(self.interaction.container.name, True, COLOR_PG_HUD_TEXT)
        mainSurf.blit(textSurf,(xOffset, yOffset))

        # Close Button
        buttonWidth = textSurf.get_height()
        buttonHeight = textSurf.get_height()
        xOffset = width - xOffsetOuter - BORDER_SIZE - SPACE_INNER - buttonWidth
        buttonSurf = createButton(COLOR_PG_HUD_BUTTON, buttonWidth, buttonHeight, "X", COLOR_PG_HUD_TEXT, COLOR_PG_HUD_BORDER)
        buttonRect = mainSurf.blit(buttonSurf, (xOffset,yOffset))
        buttonHandler = self.close
        self.registerMouseHandler(buttonRect, buttonHandler, None)

        # Take all Button
        buttonWidth = 50
        xOffset = xOffset - SPACE_INNER - buttonWidth
        buttonSurf = createButton(COLOR_PG_HUD_BUTTON, buttonWidth, buttonHeight, "Take all", COLOR_PG_HUD_TEXT, COLOR_PG_HUD_BORDER)
        buttonRect = mainSurf.blit(buttonSurf, (xOffset,yOffset))
        buttonHandler = self.takeAll
        self.registerMouseHandler(buttonRect, buttonHandler, None)

        # Inventory boxes
        yOffset += textSurf.get_height() + SPACE_INNER
        inventoryWidth = boxWidth / 2 - BORDER_SIZE - 2 * SPACE_INNER
        inventoryHeight = boxHeight - 2 * BORDER_SIZE - 2 * SPACE_INNER -SPACE_INNER - textSurf.get_height()
        xOffsetContainerInventory = xOffsetOuter + BORDER_SIZE + SPACE_INNER
        xOffsetPlayerInventory = xOffsetContainerInventory + inventoryWidth + SPACE_INNER
        yOffsetInventory = yOffset

        # Create a button for every container inventory item
        buttonHeight = 22
        yOffset = yOffsetInventory
        for item in self.interaction.container.inventory.items:
            buttonSurf = createButton(COLOR_PG_HUD_BUTTON, inventoryWidth, buttonHeight, item.name, COLOR_PG_HUD_TEXT)
            buttonRect = mainSurf.blit(buttonSurf,(xOffsetContainerInventory,yOffset))
            buttonHandler = self.moveItemFromContainerToPlayer
            buttonItem = item
            self.registerMouseHandler(buttonRect, buttonHandler, buttonItem)
            yOffset += buttonSurf.get_height()

        # Create a button for every player inventory item
        yOffset = yOffsetInventory
        for item in self.interaction.player.inventory.items:
            buttonSurf = createButton(COLOR_PG_HUD_BUTTON, inventoryWidth, buttonHeight, item.name, COLOR_PG_HUD_TEXT)
            buttonRect = mainSurf.blit(buttonSurf,(xOffsetPlayerInventory,yOffset))
            buttonHandler = self.moveItemFromPlayerToContainer
            buttonItem = item
            self.registerMouseHandler(buttonRect, buttonHandler, buttonItem)
            yOffset += buttonSurf.get_height()

        # Borders
        containerRect = pygame.Rect(xOffsetContainerInventory ,yOffsetInventory,inventoryWidth,inventoryHeight)
        playerRect = pygame.Rect(xOffsetPlayerInventory,yOffsetInventory,inventoryWidth,inventoryHeight)
        pygame.draw.rect(mainSurf, COLOR_PG_HUD_BORDER, containerRect, BORDER_SIZE)
        pygame.draw.rect(mainSurf, COLOR_PG_HUD_BORDER, playerRect, BORDER_SIZE)

        return mainSurf

    def takeAll(self):
        container = self.interaction.container
        player = self.interaction.player
        for item in list(container.inventory.items):
            container.removeItem(item)
            player.addItem(item)

    def moveItemFromContainerToPlayer(self, item):
        container = self.interaction.container
        player = self.interaction.player
        container.removeItem(item)
        player.addItem(item)

    def moveItemFromPlayerToContainer(self, item):
        container = self.interaction.container
        player = self.interaction.player
        player.removeItem(item)
        container.addItem(item)



    def drawSurface(self,surface):
        """
        Draws a pygame surface on the screen
        we use an Orthographic projection and some older style opengl code
        This is not using Vertex Buffers.
        """
        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.window.displayWidth, self.window.displayHeight, 0.0, -1.0, 10.0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        pixelX = self.window.displayWidth / 2 - surface.get_width() / 2
        pixelY = self.window.displayHeight / 2 - surface.get_height() / 2 + surface.get_height()
        ndcX = (pixelX/float(self.window.displayWidth))*2.0 - 1.0
        ndcY = 1.0 - (pixelY/float(self.window.displayHeight)) * 2.0
        surfData = pygame.image.tostring(surface, "RGBA", True)
        # Draw on the OpenGl screen
        GL.glLoadIdentity()
        GL.glRasterPos3d(ndcX, ndcY, -1.0)
        GL.glDrawPixels(surface.get_width(), surface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, surfData)
