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
from WarrensGame.Actors import Character

from math import sqrt

#movement keys
movement_keys = {
        pygame.K_h: (-1, +0),       # vi keys
        pygame.K_l: (+1, +0),
        pygame.K_j: (+0, +1),
        pygame.K_k: (+0, -1),
        pygame.K_y: (-1, -1),
        pygame.K_u: (+1, -1),
        pygame.K_b: (-1, +1),
        pygame.K_n: (+1, +1),
        pygame.K_KP4: (-1, +0),     # numerical keypad
        pygame.K_KP6: (+1, +0),
        pygame.K_KP2: (+0, +1),
        pygame.K_KP8: (+0, -1),
        pygame.K_KP7: (-1, -1),
        pygame.K_KP9: (+1, -1),
        pygame.K_KP1: (-1, +1),
        pygame.K_KP3: (+1, +1),
        pygame.K_LEFT: (-1, +0),    # arrows and pgup/dn keys
        pygame.K_RIGHT: (+1, +0),
        pygame.K_DOWN: (+0, +1),
        pygame.K_UP: (+0, -1),
        pygame.K_HOME: (-1, -1),
        pygame.K_PAGEUP: (+1, -1),
        pygame.K_END: (-1, +1),
        pygame.K_PAGEDOWN: (+1, +1),
        }

#tileSize in OpenGl space
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
         
        #Move camera out and rotate
        #glTranslatef(15 * tileSize,15 * tileSize, 0)
        glRotatef(-45, 0.5, 0, 1)
        
       
        while True:
            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)

            #glPushMatrix()
            
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)    
            
            glColor3f(0,1,0)
            glutSolidSphere(tileSize/2,32,32)
            #draw the scene
            self.drawScene()
            
            #glPopMatrix()
            
            #finish up
            pygame.display.flip()
            pygame.time.wait(10)

    def drawScene(self):        
        #Draw map border
        map = self.game.currentLevel.map
        glBegin(GL_POLYGON) 
        glColor3f(0.5,0.4,0.1)
        glVertex3fv((0 * tileSize,0 * tileSize,0))
        #glVertex3fv((map.width * tileSize, 0 * tileSize,0))
        glVertex3fv((map.width * tileSize, 0 * tileSize,0))
        #glVertex3fv((map.width * tileSize, map.height * tileSize,0))
        glVertex3fv((map.width * tileSize, map.height * tileSize,0))
        #glVertex3fv((0 * tileSize, map.height * tileSize,0))
        glVertex3fv((0 * tileSize, map.height * tileSize,0))
        #glVertex3fv((0 * tileSize,0 * tileSize,0))
        glEnd()
        
        #Draw all visible tiles on the first level
        glColor3f(0,0,0)
        for tile in self.game.currentLevel.map.visible_tiles:
            self.drawTile(tile)

        #Draw underlying levels
        for i in range (1, len(self.game.levels) -1):
            glPushMatrix()
            glTranslatef(0, 0, -i)
            glColor3f(0.5,0.5,0.5)
            self.drawLevel(self.game.levels[i])
            glPopMatrix()
        
        #Draw player
        pTile = self.game.player.tile
        glPushMatrix()
        glTranslatef(pTile.x * tileSize + tileSize / 2, pTile.y * tileSize + tileSize / 2, tileSize / 2)
        glColor3f(1,0,0)
        glutSolidSphere(tileSize/2,32,32)
        glPopMatrix()
        
    def drawLevel(self, level):
        for tilerow in level.map.tiles:
            for tile in tilerow:
                if not tile.blocked:
                    self.drawTile(tile)
        
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
        
        #keyboard    
        elif event.type == pygame.KEYDOWN:
            #Handle keys that are always active
            if event.key == pygame.K_ESCAPE:
                sys.exit() 
            #Handle keys that are active while playing
            if self.game.state == Game.PLAYING:
                player = self.game.player
                if player.state == Character.ACTIVE:
                    #movement
                    global movement_keys
                    if event.key in movement_keys:
                        player.tryMoveOrAttack(*movement_keys[event.key])
                        #TODO: Decide in the game code if turn is taken or not, tookATurn should be bool on player which can be reset by the game.
                        self._gamePlayerTookTurn = True
                    
                    #portal keys
                    elif event.key == pygame.K_LESS:
                        #check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT): 
                            player.tryFollowPortalDown()
                        else:
                            player.tryFollowPortalUp()
                    #inventory
                    elif event.key == pygame.K_i:
                        self.useInventory()
                    elif event.key == pygame.K_d:
                        self.dropInventory()
                    #interact
                    elif event.key == pygame.K_COMMA:
                        player.tryPickUp()
                    
                    # update field of vision
                    if self._gamePlayerTookTurn:
                        self.game.currentLevel.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)

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
            l=sqrt(x*x+y*y+z*z)
            s= m[3][3]
            factor = rel[0] / s/l
            glTranslatef(factor * x,factor * y,factor * z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= m[0][1]
            y= m[1][1]
            z= m[2][1]
            l=sqrt(x*x+y*y+z*z)
            s= m[3][3]
            factor =  -1* rel[1] / s/l
            glTranslatef(factor * x,factor * y,factor * z)
            
        elif self._rotating:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()

            #set rotation center, rotate around the center of the top map
            map = self.game.currentLevel.map
            rotation_center_x = map.width / 2
            rotation_center_y = map.height / 2
            glTranslatef(rotation_center_x * tileSize,rotation_center_y * tileSize, 0)
                     
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

            #unset rotation center
            glTranslatef(-rotation_center_x * tileSize,-rotation_center_y * tileSize, 0)
            
            

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