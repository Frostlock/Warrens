'''
Created on Jan 12, 2015

Another way to render, this time using PyOpenGL together with pygame.

Thanks to 
http://www.arcsynthesis.org/gltut/
http://www.willmcgugan.com/blog/tech/2007/6/4/opengl-sample-code-for-pygame/

@author: pi
'''

import sys, pygame
from pygame.locals import *

from OpenGL import GL
from OpenGL import GLU
from OpenGL import GLUT

from WarrensGame.Game import Game
from WarrensGame.Actors import Character
import GuiUtilities
import GuiCONSTANTS

from gameobjects.matrix44 import *
from gameobjects.vector3 import *

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
#         pygame.K_LEFT: (-1, +0),    # arrows and pgup/dn keys
#         pygame.K_RIGHT: (+1, +0),
#         pygame.K_DOWN: (+0, -1),
#         pygame.K_UP: (+0, +1),
#         pygame.K_HOME: (-1, +1),
#         pygame.K_PAGEUP: (+1, +1),
#         pygame.K_END: (-1, -1),
#         pygame.K_PAGEDOWN: (+1, -1),
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

    @property
    def cameraMatrix(self):
        """
        Returns the camera matrix
        """
        return self._cameraMatrix

    @cameraMatrix.setter
    def cameraMatrix(self,m):
        """
        Sets the camera matrix
        """
        self._cameraMatrix = m

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
        self.FPS = 0
        
    #Called whenever the window is resized. The new window size is given, in pixels.
    def resizeWindow(self,displaySize):
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize,RESIZABLE|HWSURFACE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
        
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        
        GLU.gluPerspective(60.0, float(width)/height, .1, 1000.)
        
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
            
    def showMainMenu(self):
        #Init pygame
        pygame.init()
        self.resizeWindow((800,600))

        #Initialize fonts
        GuiUtilities.initFonts()
            
        #Init PyOpenGl
        GLUT.glutInit([])
        
        #Enable depth testing
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)
        
        #Enable alpha testing
        GL.glEnable(GL.GL_ALPHA_TEST)
        GL.glAlphaFunc(GL.GL_GREATER, 0.5)
        
#        GL.glShadeModel(GL.GL_FLAT)
#        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
# 
#        GL.glEnable(GL.GL_COLOR_MATERIAL)
#     
#        GL.glEnable(GL.GL_LIGHTING)
#        GL.glEnable(GL.GL_LIGHT0)        
#        GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION,  (0, 1, 1, 0))   

        #Init Game
        self._game = Game()
        self.game.resetGame()        
        

        clock = pygame.time.Clock()    
        
#        GL.glMaterial(GL.GL_FRONT, GL.GL_AMBIENT, (0.1, 0.1, 0.1, 1.0))    
#        GL.glMaterial(GL.GL_FRONT, GL.GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0)) 

        self.centerCameraOnMap()
        
        # Initialize speeds and directions
        rotation_direction = Vector3()
        rotation_speed = radians(90.0)
        movement_direction = Vector3()
        movement_speed = 5.0    
    
        while True:
            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)
            
            #handle game events
            if self.game.player.state == Character.DEAD:
                #zoom in on player corpse
                self.centerCameraOnActor(self.game.player)
                
            # Clear the screen, and z-buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT);
                            
            time_passed = clock.tick()
            time_passed_seconds = time_passed / 1000.
            if time_passed_seconds <> 0 : self.FPS=1/time_passed_seconds
            
            pressed = pygame.key.get_pressed()
            
            # Reset rotation and movement directions
            rotation_direction.set(0.0, 0.0, 0.0)
            movement_direction.set(0.0, 0.0, 0.0)
            
            # Modify direction vectors for key presses
            if pressed[K_LEFT]:
                rotation_direction.y = +1.0
            elif pressed[K_RIGHT]:
                rotation_direction.y = -1.0
            if pressed[K_UP]:
                rotation_direction.x = -1.0
            elif pressed[K_DOWN]:
                rotation_direction.x = +1.0
            if pressed[K_PAGEUP]:
                rotation_direction.z = -1.0
            elif pressed[K_PAGEDOWN]:
                rotation_direction.z = +1.0            
            if pressed[K_HOME]:
                movement_direction.z = -1.0
            elif pressed[K_END]:
                movement_direction.z = +1.0
            
            # Calculate rotation matrix and multiply by camera matrix    
            rotation = rotation_direction * rotation_speed * time_passed_seconds
            rotation_matrix = Matrix44.xyz_rotation(*rotation)        
            self.cameraMatrix *= rotation_matrix
            
            # Calcluate movment and add it to camera matrix translate
            heading = Vector3(self.cameraMatrix.forward)
            movement = heading * movement_direction.z * movement_speed                    
            self.cameraMatrix.translate += movement * time_passed_seconds
            
            # Upload the inverse camera matrix to OpenGL
            GL.glLoadMatrixd(self.cameraMatrix.get_inverse().to_opengl())
                    
            # Light must be transformed as well
#            GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION,  (0, 1.5, 1, 0)) 
                    
            #Render the 3D view
            self.drawView()
            
            #Render the HUD (health bar, XP bar, etc...)
            self.drawHUD()
                    
            # Show the screen
            pygame.display.flip()
            
            #If the player took a turn: Let the game play a turn
            if self._gamePlayerTookTurn: 
                self._game.playTurn()
                self._gamePlayerTookTurn = False
           


            
    def centerCameraOnActor(self, actor):
        #Set a new camera transform matrix
        self.cameraMatrix = Matrix44()
        #Translate it above the actor
        x = actor.tile.x
        y = actor.tile.y
        self.cameraMatrix.translate = (x * tileSize,y * tileSize, 4)

    def centerCameraOnMap(self):
        #Set a new camera transform matrix
        self.cameraMatrix = Matrix44()
        #Translate it above the center of the map
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        self.cameraMatrix.translate = (x * tileSize,y * tileSize-1, 13)
        
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
                
#         #Draw underlying levels
#         for i in range (1, len(self.game.levels) -1):
#             GL.glPushMatrix()
#             GL.glTranslatef(0, 0, -i)
#             GL.glColor3f(0.5,0.5,0.5)
#             self.drawLevel(self.game.levels[i])
#             GL.glPopMatrix()
    
        
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
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPushMatrix()
        GL.glLoadIdentity()
        GL.glOrtho(0.0, self.displayWidth, self.displayHeight, 0.0, -1.0, 10.0)
        
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        
        #Level name
        GL.glLoadIdentity()
        self.drawText((-0.98,0.9,0), self.game.currentLevel.name,24)
        
        #Player name
        GL.glLoadIdentity()
        self.drawText((-0.98,-0.85,0), self.game.player.name + " (Lvl " + str(self.game.player.playerLevel) + ")",18)
        
        #Health Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98,-0.94,0)
        current = self.game.player.currentHitPoints
        maximum = self.game.player.maxHitPoints
        barWidth = 0.46
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
        GL.glTranslatef(-0.98,-0.99,0)
        current = self.game.player.xp
        maximum = self.game.player.nextLevelXp
        barWidth = 0.46
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

        #FPS
        GL.glLoadIdentity()
        self.drawText((-0.98,-1,0), str(self.FPS),12)

        #Right side: render game messages
        GL.glLoadIdentity()
        widthOffset = 200
        heightOffset = 100
        messageCounter = 1
        nbrOfMessages = len (self.game.messageBuffer)
        while heightOffset > 0:
            if messageCounter > nbrOfMessages: break
            #get messages from game message buffer, starting from the back
            message = self.game.messageBuffer[nbrOfMessages - messageCounter]
            #create textLines for message
            textLines = GuiUtilities.wrap_multi_line(message,GuiUtilities.FONT_PANEL,800-widthOffset)
            nbrOfLines = len(textLines)
            #blit the lines
            for l in range(1,nbrOfLines+1):
                textSurface = GuiUtilities.FONT_PANEL.render(textLines[nbrOfLines-l], 1, GuiCONSTANTS.COLOR_PANEL_FONT)
                heightOffset = heightOffset - 2 * textSurface.get_height()
                textData = pygame.image.tostring(textSurface, "RGBA", True)
                GL.glRasterPos3d(-0.5,-0.88-(heightOffset/600.),0)     
                GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)

            messageCounter += 1
            
        #Switch back to perspective mode
        GLU.gluPerspective(60.0, (self.displayWidth/self.displayHeight), .1, 1000.)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glPopMatrix()

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
                self.centerCameraOnActor(self.game.player)
            elif event.key == pygame.K_m:
                self.centerCameraOnMap()
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
            
            s= self.cameraMatrix[3,3]
            
            #Get the left right direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,0]
            y= self.cameraMatrix[1,0]
            z= self.cameraMatrix[2,0]
            l=sqrt(x*x+y*y+z*z)
            factor = -1 * rel[0] / s/l
            #Translate along this direction
            translation = Matrix44.translation(factor * x,factor * y,factor * z)
            self.cameraMatrix *= translation
            
            #Get the up down direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,1]
            y= self.cameraMatrix[1,1]
            z= self.cameraMatrix[2,1]
            l=sqrt(x*x+y*y+z*z)
            factor = rel[1] / s/l
            #Translate along this direction
            translation = Matrix44.translation(factor * x,factor * y,factor * z)
            self.cameraMatrix *= translation
            
        elif self._rotating:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()

            #set rotation center, rotate around the center of the top map
#             map = self.game.currentLevel.map
#             rotation_center_x = map.width / 2
#             rotation_center_y = map.height / 2
#             GL.glTranslatef(rotation_center_x * tileSize,rotation_center_y * tileSize, 0)
                     
            #Get the left right direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,0]
            y= self.cameraMatrix[1,0]
            z= self.cameraMatrix[2,0]
            rotation = Matrix44.rotation_about_axis((x,y,z), radians(1))#.translation(factor * x,factor * y,factor * z)
            self.cameraMatrix *= rotation
            #GL.glRotatef(rel[1] ,x, y, z)
            
            #Get the up down direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,1]
            y= self.cameraMatrix[1,1]
            z= self.cameraMatrix[2,1]
            rotation = Matrix44.rotation_about_axis((x,y,z), radians(-1))#.translation(factor * x,factor * y,factor * z)
            self.cameraMatrix *= rotation
            #GL.glRotatef(rel[0] ,x, y, z)

            #unset rotation center
            #GL.glTranslatef(-rotation_center_x * tileSize,-rotation_center_y * tileSize, 0)
            
    def eventZoomIn(self):
        factor = -1
        #Get the direction of the camera from the camera matrix
        x= self.cameraMatrix[0,2]
        y= self.cameraMatrix[1,2]
        z= self.cameraMatrix[2,2]
        #Translate along this direction
        translation = Matrix44.translation(factor * x,factor * y,factor * z)
        self.cameraMatrix *= translation
        
    def eventZoomOut(self):
        factor = 1
        #Get the direction of the camera from the current modelview matrix
        x= self.cameraMatrix[0,2]
        y= self.cameraMatrix[1,2]
        z= self.cameraMatrix[2,2]
        #Translate along this direction        
        translation = Matrix44.translation(factor * x,factor * y,factor * z)
        self.cameraMatrix *= translation