'''
Created on Jan 12, 2015

Another way to render, this time using PyOpenGL together with pygame.

@author: pi
'''

import sys, pygame
from pygame.locals import *

from OpenGL import GL
from OpenGL import GLU
from OpenGL import GLUT

from WarrensGame.Game import Game
from WarrensGame.Actors import Character
import GuiCONSTANTS

from math import sqrt

#movement keys
movement_keys = {
        pygame.K_h: (-1, +0),       # vi keys
        pygame.K_l: (+1, +0),
        pygame.K_j: (+0, -1),
        pygame.K_k: (+0, +1),
        pygame.K_y: (-1, +1),
        pygame.K_u: (+1, +1),
        pygame.K_b: (-1, -1),
        pygame.K_n: (+1, -1),
        pygame.K_KP4: (-1, +0),     # numerical keypad
        pygame.K_KP6: (+1, +0),
        pygame.K_KP2: (+0, -1),
        pygame.K_KP8: (+0, +1),
        pygame.K_KP7: (-1, +1),
        pygame.K_KP9: (+1, +1),
        pygame.K_KP1: (-1, -1),
        pygame.K_KP3: (+1, -1),
        pygame.K_LEFT: (-1, +0),    # arrows and pgup/dn keys
        pygame.K_RIGHT: (+1, +0),
        pygame.K_DOWN: (+0, -1),
        pygame.K_UP: (+0, +1),
        pygame.K_HOME: (-1, +1),
        pygame.K_PAGEUP: (+1, +1),
        pygame.K_END: (-1, -1),
        pygame.K_PAGEDOWN: (+1, -1),
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

    @property
    def displaySize(self):
        """
        Returns the display size (width, height)
        """
        return self._displaySize
    
    @property
    def displayWidth(self):
        """
        Returns the display width
        """
        return self.displaySize[0]
    
    @property    
    def displayHeight(self):
        """
        Returns the display height
        """
        return self.displaySize[1]
    
    #constructor
    def __init__(self):
        """
        Constructor to create a new GlApplication object.
        """
        #Initialize class variables
        self._displaySize = (800,600)
        self._dragging = False
        self._rotating = False
        self._gamePlayerTookTurn = False
        
    #Called whenever the window is resized. The new window size is given, in pixels.
    def resizeWindow(self,displaySize):
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize,RESIZABLE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
            
    def showMainMenu(self):
        #Init pygame
        pygame.init()
        self.resizeWindow((800,600))
    
        #Init PyOpenGl
        GLU.gluPerspective(45, (self.displayWidth/self.displayHeight), 0.1, 500.0)
        GLUT.glutInit([])
        
        #Enable depth testing
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)
    
        #Enable alpha testing
        GL.glEnable(GL.GL_ALPHA_TEST)
        GL.glAlphaFunc(GL.GL_GREATER, 0.5)
        
        #Init Game
        self._game = Game()
        self.game.resetGame()        
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        #Camera is always at (0, 0, 0) looking down along the z axis
         
        #Center above the center of the map
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        GL.glTranslatef(-1* x * tileSize,-1* y * tileSize, 0)
          
        #Move the entire world down so it becomes visible
        GL.glTranslatef(0,8, -25)
          
        #Move camera out and rotate
        #glTranslatef(15 * tileSize,15 * tileSize, 0)
        GL.glRotatef(-45, 0.5, 0, 1)
        
        while True:
            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)
            
            GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
            
            #draw the scene
            self.drawView()
            self.drawHUD()
            pygame.display.flip()
            
            #If the player took a turn: Let the game play a turn
            if self._gamePlayerTookTurn: 
                self._game.playTurn()
                self._gamePlayerTookTurn = False
                
                
            pygame.time.wait(10)

    def cameraPlayer(self):
        GL.glLoadIdentity()
        #Center above the player
        playerTile = self.game.player.tile
        x = playerTile.x
        y = playerTile.y
        GL.glTranslatef(-1* x * tileSize,-1* y * tileSize, 0)
        #Move the entire world down so it becomes visible
        #GL.glTranslatef(0,0, -25)
         
        #Move camera out and rotate
        #glTranslatef(15 * tileSize,15 * tileSize, 0)
        #GL.glRotatef(-45, 0.5, 0, 1)

    def cameraMap(self):
        GLU.gluLookAt(25,25,0, 0,0,0, 0,1,0)
        pass
        
    def drawView(self):        
        #Draw map border
        map = self.game.currentLevel.map
        GL.glBegin(GL.GL_POLYGON) 
        GL.glColor3f(0.5,0.4,0.1)
        GL.glVertex3fv((0 * tileSize,0 * tileSize,-0.0001))
        #glVertex3fv((map.width * tileSize, 0 * tileSize,0))
        GL.glVertex3fv((map.width * tileSize, 0 * tileSize,-0.0001))
        #glVertex3fv((map.width * tileSize, map.height * tileSize,0))
        GL.glVertex3fv((map.width * tileSize, map.height * tileSize,-0.0001))
        #glVertex3fv((0 * tileSize, map.height * tileSize,0))
        GL.glVertex3fv((0 * tileSize, map.height * tileSize,-0.0001))
        #glVertex3fv((0 * tileSize,0 * tileSize,0))
        GL.glEnd()
        
        #Draw all visible tiles on the current level
        GL.glColor3f(0,0,0)
        for tile in self.game.currentLevel.map.visible_tiles:
            self.drawTile(tile)
            for actor in tile.actors:
                self.drawActor(actor)
                

        #Draw underlying levels
        for i in range (1, len(self.game.levels) -1):
            GL.glPushMatrix()
            GL.glTranslatef(0, 0, -i)
            GL.glColor3f(0.5,0.5,0.5)
            self.drawLevel(self.game.levels[i])
            GL.glPopMatrix()
        
        """
        #Draw player
        pTile = self.game.player.tile
        GL.glPushMatrix()
        GL.glTranslatef(pTile.x * tileSize + tileSize / 2, pTile.y * tileSize + tileSize / 2, tileSize / 2)
        GL.glColor3f(1,0,0)
        GLUT.glutSolidSphere(tileSize/2,32,32)
        GL.glPopMatrix()
        """
        
    def drawLevel(self, level):
        for tilerow in level.map.tiles:
            for tile in tilerow:
                if not tile.blocked:
                    self.drawTile(tile)
    
    def drawTile(self, tile):
        GL.glBegin(GL.GL_QUADS)
        self.setDrawColor(tile.color) 
        GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize,0))
        GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize,0))
        #GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize,0))
        GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize + tileSize,0))
        #GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize + tileSize,0))
        GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize + tileSize,0))
        #GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize + tileSize,0))
        #GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize,0))
        GL.glEnd()
    
    def drawActor(self, actor):
        tile = actor.tile
        GL.glPushMatrix()
        GL.glTranslatef(tile.x * tileSize + tileSize / 2, tile.y * tileSize + tileSize / 2, tileSize / 2)
        self.setDrawColor(actor.color)
        GLUT.glutSolidSphere(tileSize/2,32,32)
        GL.glPopMatrix()
        
        
    def setDrawColor(self, color):
        GL.glColor3f(float(color[0])/250,float(color[1])/250,float(color[2])/250)
    
    def drawText(self, position, textString, textSize):     
        font = pygame.font.Font (None, textSize)
        textSurface = font.render(textString, True, (255,255,255,255))#, (0,0,0,255))     
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        GL.glRasterPos3d(*position)     
        GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)
        
    def drawHUD(self):
        #Switch to orthographic mode
        GL.glPushMatrix()
        GL.glOrtho(0.0, self.displayWidth, self.displayHeight, 0.0, -1.0, 10.0)
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        
        
        GL.glLoadIdentity()
        self.drawText((-0.98,0.9,0), self.game.currentLevel.name,24)
        
        #Health Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98,-0.9,0)
        current = self.game.player.currentHitPoints
        maximum = self.game.player.maxHitPoints
        barWidth = 0.5
        barHeight =0.08
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(GuiCONSTANTS.COLOR_BAR_HEALTH_BG)
        GL.glVertex2f(0.0, 0.0)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth/maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(GuiCONSTANTS.COLOR_BAR_HEALTH)
            GL.glVertex2f(0.0, 0.0)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glEnd()
        
        #Xp Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98,-0.95,0)
        current = self.game.player.xp
        maximum = self.game.player.nextLevelXp
        barWidth = 0.5
        barHeight =0.04
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(GuiCONSTANTS.COLOR_BAR_XP_BG)
        GL.glVertex2f(0.0, 0.0)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth/maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(GuiCONSTANTS.COLOR_BAR_XP)
            GL.glVertex2f(0.0, 0.0)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glEnd()
        
        #Switch back to perspective mode
        GLU.gluPerspective(45, (self.displayWidth/self.displayHeight), 0.1, 500.0)
        GL.glPopMatrix()
        pass

    def handleEvent(self, event):
        #Quit
        if event.type == pygame.QUIT: sys.exit()
        
        #Window resize
        elif event.type == VIDEORESIZE:
            self.resizeWindow(event.dict['size'])
        
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
            elif event.key == pygame.K_p:
                self.cameraPlayer()
            elif event.key == pygame.K_m:
                self.cameraMap()
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
            
            m = GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX)
            #Get the left right direction of the camera from the current modelview matrix
            x= m[0][0]
            y= m[1][0]
            z= m[2][0]
            l=sqrt(x*x+y*y+z*z)
            s= m[3][3]
            factor = rel[0] / s/l
            GL.glTranslatef(factor * x,factor * y,factor * z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= m[0][1]
            y= m[1][1]
            z= m[2][1]
            l=sqrt(x*x+y*y+z*z)
            s= m[3][3]
            factor =  -1* rel[1] / s/l
            GL.glTranslatef(factor * x,factor * y,factor * z)
            
        elif self._rotating:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()

            #set rotation center, rotate around the center of the top map
            map = self.game.currentLevel.map
            rotation_center_x = map.width / 2
            rotation_center_y = map.height / 2
            GL.glTranslatef(rotation_center_x * tileSize,rotation_center_y * tileSize, 0)
                     
            m = GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX)
            #Get the left right direction of the camera from the current modelview matrix
            x= m[0][0]
            y= m[1][0]
            z= m[2][0]
            GL.glRotatef(rel[1] ,x, y, z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= m[0][1]
            y= m[1][1]
            z= m[2][1]
            GL.glRotatef(rel[0] ,x, y, z)

            #unset rotation center
            GL.glTranslatef(-rotation_center_x * tileSize,-rotation_center_y * tileSize, 0)
            
    def eventZoomIn(self):
        factor = -1
        #Get the direction of the camera from the current modelview matrix
        m = GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX)
        x= m[0][2]
        y= m[1][2]
        z= m[2][2]
        #Translate along this direction        
        GL.glTranslatef(factor * x,factor * y,factor * z)
        
    def eventZoomOut(self):
        factor = 1
        #Get the direction of the camera from the current modelview matrix
        m = GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX)
        x= m[0][2]
        y= m[1][2]
        z= m[2][2]
        #Translate along this direction        
        GL.glTranslatef(factor * x,factor * y,factor * z)