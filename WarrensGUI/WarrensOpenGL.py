'''
Created on Jan 12, 2015

Another way to render, this time using PyOpenGL together with pygame.

@author: pi
'''

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

from WarrensGame.Game import Game


vertices = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )

class GlApplication(object):

    @property
    def game(self):
        """
        Returns the current game.
        """
        return self._game

    def rotatingCube(self):
        #This rotates the entire openGl coordinate system
        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        #Draw cube
        glBegin(GL_LINES)
        for edge in edges:
            for vertex in edge:
                glVertex3fv(vertices[vertex])
        glEnd()
            
    def drawTile(self, tile):
        tileSize = 0.25
        glBegin(GL_LINES) 
        glVertex3fv((tile.x * tileSize,tile.y * tileSize,0))
        glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize,0))
        glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize,0))
        glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize + tileSize,0))
        glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize + tileSize,0))
        glVertex3fv((tile.x * tileSize,tile.y * tileSize + tileSize,0))
        glVertex3fv((tile.x * tileSize,tile.y * tileSize + tileSize,0))
        glVertex3fv((tile.x * tileSize,tile.y * tileSize,0))
        glEnd()
        
        
        
        
    def showMainMenu(self):
        #Init pygame
        pygame.init()
        display = (800,600)
        pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    
        #Init PyOpenGl
        gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    
        #Init Game
        self._game = Game()
        self.game.resetGame()
        
        
        #Camera is always at (0, 0, 0) looking down along the z axis
        
        
        tileSize = 0.25
        
        #Center above the player
        #playerTile = self.game.player.tile
        #x = playerTile.x
        #y = playerTile.y
        #glTranslatef(-1* x * tileSize,-1* y * tileSize, 0)
        
        #Center above the center of the map
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        glTranslatef(-1* x * tileSize,-1* y * tileSize, 0)
        
        #Move the entire world down so it becomes visible
        glTranslatef(0,8, -25)
        #Move camera out and rotate
        #glTranslatef(15 * tileSize,15 * tileSize, 0)
        glRotatef(-45, 0.5, 0, 1)
    
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
    
            #self.rotatingCube()
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            #Fancy rotation
            #glRotatef(1, 0, 0, 1)
            
            #Draw map border
            glBegin(GL_LINES) 
            glVertex3fv((0 * tileSize,0 * tileSize,0))
            glVertex3fv((map.width * tileSize, 0 * tileSize,0))
            glVertex3fv((map.width * tileSize, 0 * tileSize,0))
            glVertex3fv((map.width * tileSize, map.height * tileSize,0))
            glVertex3fv((map.width * tileSize, map.height * tileSize,0))
            glVertex3fv((0 * tileSize, map.height * tileSize,0))
            glVertex3fv((0 * tileSize, map.height * tileSize,0))
            glVertex3fv((0 * tileSize,0 * tileSize,0))
            glEnd()
            
            #Draw all visible tiles
            for tile in self.game.currentLevel.map.visible_tiles:
                self.drawTile(tile)


            pygame.display.flip()
            pygame.time.wait(10)

