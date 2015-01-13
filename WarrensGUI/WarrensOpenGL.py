'''
Created on Jan 12, 2015

Another way to render, this time using PyOpenGL together with pygame.

@author: pi
'''

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

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

tileSize = 0.25

class GlApplication(object):

    @property
    def game(self):
        """
        Returns the current game.
        """
        return self._game

    #constructor
    def __init__(self):
        """
        Constructor to create a new GlApplication object.
        """
        #Initialize class variables
        self._dragging = False
        self._rotating = False

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
        gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
        glutInit([])
    
        #Init Game
        self._game = Game()
        self.game.resetGame()        
        
        glMatrixMode(GL_MODELVIEW)
        
        #Camera is always at (0, 0, 0) looking down along the z axis
        
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
        #glTranslatef(0,0, -25)
         
        #Move camera out and rotate
        #glTranslatef(15 * tileSize,15 * tileSize, 0)
        glRotatef(-45, 0.5, 0, 1)
       
        while True:
            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)

            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)    
            
            glColor3f(0,1,0)
            glutSolidSphere(tileSize/2,32,32)
            #draw the scene
            self.drawScene()
            
            #finish up
            pygame.display.flip()
            pygame.time.wait(10)

    def drawScene(self):        
        #Draw map border
        map = self.game.currentLevel.map
        glBegin(GL_LINES) 
        glColor3f(0.95,0.95,0.95)
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
        glColor3f(0.5,0.5,0.5)
        for tile in self.game.currentLevel.map.visible_tiles:
            self.drawTile(tile)

        #Draw player
        pTile = self.game.player.tile
        glPushMatrix()
        glTranslatef(pTile.x * tileSize + tileSize / 2, pTile.y * tileSize + tileSize / 2, tileSize / 2)
        glColor3f(1,0,0)
        glutSolidSphere(tileSize/2,32,32)
        glPopMatrix()
        
    def handleEvent(self, event):
        #Quit
        if event.type == pygame.QUIT: sys.exit()
        
        #Window resize
        #elif event.type == VIDEORESIZE:
        #    self.setupSurfaces(event.dict['size'])
        
        #mouse
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                self.eventDraggingStart()
            elif event.button == 3:
                self.eventRotatingStart()
            elif event.button == 4:
                self.eventZoomIn()
            elif event.button == 5:
                self.eventZoomOut()
        elif event.type == MOUSEMOTION:
            self.eventMouseMovement()           
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                self.eventDraggingStop()
            elif event.button == 3:
                self.eventRotatingStop()

    def eventDraggingStart(self):
        self._dragging = True
        #call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventDraggingStop(self):
        self._dragging = False

    def eventRotatingStart(self):
        self._rotating = True
        #call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventRotatingStop(self):
        self._rotating = False
        
    def eventMouseMovement(self):
        #check for on going drag
        if self._dragging:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()
            
            m = glGetFloatv(GL_MODELVIEW_MATRIX)
            #Get the left right direction of the camera from the current modelview matrix
            x= m[0][0]
            y= m[1][0]
            z= m[2][0]
            s= m[3][3]
            factor = rel[0] / s
            glTranslatef(factor * x,factor * y,factor * z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= m[0][1]
            y= m[1][1]
            z= m[2][1]
            s= m[3][3]
            factor = -1 * rel[1] / s
            glTranslatef(factor * x,factor * y,factor * z)
            
        elif self._rotating:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()
            
            m = glGetFloatv(GL_MODELVIEW_MATRIX)
            #Get the left right direction of the camera from the current modelview matrix
            x= m[0][0]
            y= m[1][0]
            z= m[2][0]
            glRotatef(rel[1] ,x, y, z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= m[0][1]
            y= m[1][1]
            z= m[2][1]
            glRotatef(rel[0] ,x, y, z)

            

    def eventZoomIn(self):
        factor = -1
        #Get the direction of the camera from the current modelview matrix
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        x= m[0][2]
        y= m[1][2]
        z= m[2][2]
        #Translate along this direction        
        glTranslatef(factor * x,factor * y,factor * z)
        
    def eventZoomOut(self):
        factor = 1
        #Get the direction of the camera from the current modelview matrix
        m = glGetFloatv(GL_MODELVIEW_MATRIX)
        x= m[0][2]
        y= m[1][2]
        z= m[2][2]
        #Translate along this direction        
        glTranslatef(factor * x,factor * y,factor * z)