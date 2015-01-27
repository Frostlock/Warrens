'''
Created on Jan 12, 2015

Another way to render, this time using PyOpenGL together with pygame.

Thanks to 
http://www.arcsynthesis.org/gltut/
http://www.willmcgugan.com/blog/tech/2007/6/4/opengl-sample-code-for-pygame/

@author: pi
'''

import pygame
from pygame.locals import *
from OpenGL import GL
from OpenGL.GL.ARB.vertex_array_object import glBindVertexArray

from OpenGL import GLUT

from ctypes import c_void_p

from WarrensGame.Game import Game
from WarrensGame.Actors import Character

import GuiUtilities
import GuiCONSTANTS

from WarrensGUI.Utilities.matrix44 import *
from WarrensGUI.Utilities.vector3 import *

import sys

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
TILESIZE = 0.25

# 4 bytes in a float
# TODO: Find a better way to deal with this
SIZE_OF_FLOAT = 4

# 4 components in a vector: X, Y, Z, W
VERTEX_COMPONENTS = 4

class GlApplication(object):

    @property
    def game(self):
        """
        Returns the current game.
        """
        return self._game

    @property
    def level(self):
        """
        Returns the level that is currently being shown in the GUI
        """
        return self._level

    @level.setter
    def level(self,level):
        """
        Sets the level to be shown in the GUI.
        This will also load the vertexbuffer for the level mesh
        """
        self._level = level
        #Load the mesh for the level in the vertexbuffer
        self.loadVBOLevel()

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
    def openGlProgram(self):
        return self._openGlProgram

    @openGlProgram.setter
    def openGlProgram(self,program):
        self._openGlProgram = program

    @property
    def cameraMatrix(self):
        """
        Returns the camera matrix
        """
        return self._cameraMatrix

    @cameraMatrix.setter
    def cameraMatrix(self,matrix):
        """
        Sets the camera matrix
        """
        self._cameraMatrix = matrix

    @property
    def perspectiveMatrix(self):
        """
        Returns the perspective matrix
        """
        return self._perspectiveMatrix

    @perspectiveMatrix.setter
    def perspectiveMatrix(self,matrix):
        """
        Sets the perspective matrix
        """
        self._perspectiveMatrix= matrix
        # Send the perspective matrix to the GPU
        if self.openGlProgram is not None:
            GL.glUseProgram(self.openGlProgram)
            glBindVertexArray(self.VAO_id.value)
            GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, matrix)
            GL.glUseProgram(0)

    #constructor
    def __init__(self):
        """
        Constructor to create a new GlApplication object.
        """
        #Initialize class variables
        self._game = None
        self._level = None
        self._displaySize = (800,600)
        self._openGlProgram = None
        self._cameraMatrix = None
        self._perspectiveMatrix = None
        #TODO: create proper properties for these
        self._dragging = False
        self._rotating = False
        self._gamePlayerTookTurn = False
        self.FPS = 0

    #Called whenever the window is resized. The new window size is given, in pixels.
    def resizeWindow(self,displaySize):
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize,RESIZABLE|HWSURFACE|DOUBLEBUF|OPENGL)
        #Uncomment to run in fullscreen2
        #pygame.display.set_mode(self.displaySize,FULLSCREEN|HWSURFACE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
        self.calculatePerspectiveMatrix()

#        GL.glMatrixMode(GL.GL_PROJECTION)
#        GL.glLoadIdentity()
#        GLU.gluPerspective(60.0, float(width)/height, .1, 1000.)
#        GL.glMatrixMode(GL.GL_MODELVIEW)
#        GL.glLoadIdentity()

    def calculatePerspectiveMatrix(self):
        fFrustumScale = 1.0
        fzNear = 0.1
        fzFar = 1000.0
        theMatrix = [0.0 for i in range(16)]
        theMatrix[0] = fFrustumScale * 1
        theMatrix[5] = fFrustumScale * (float(self.displayWidth) / self.displayHeight)
        theMatrix[10] = (fzFar + fzNear) / (fzNear - fzFar)
        theMatrix[14] = (2 * fzFar * fzNear) / (fzNear - fzFar)
        theMatrix[11] = -1.0
        self.perspectiveMatrix = theMatrix

    def initOpenGl(self):
        """
        Initializes OpenGl settings and shaders
        """
        GLUT.glutInit([])

        #Compile Shaders into program object
        from OpenGL.GL.shaders import compileShader, compileProgram
        strVertexShader = open("WarrensGUI/Shaders/VertexShader.glsl").read()
        strFragmentShader = open("WarrensGUI/Shaders/FragmentShader.glsl").read()
        self.openGlProgram = compileProgram(
            compileShader(strVertexShader, GL.GL_VERTEX_SHADER),
            compileShader(strFragmentShader, GL.GL_FRAGMENT_SHADER)
        )

        #Create uniform variables for the compiled shaders
        GL.glUseProgram(self.openGlProgram)
        self.perspectiveMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "perspectiveMatrix")
        self.cameraMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "cameraMatrix")

        #Generate a Vertex Array Object
        self.VAO_id = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_id)

        #Recalculate the perspective matrix
        self.calculatePerspectiveMatrix()

        GL.glUseProgram(0)

        #Enable depth testing
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)

        #Enable alpha testing
        GL.glEnable(GL.GL_ALPHA_TEST)
        GL.glAlphaFunc(GL.GL_GREATER, 0.5)

        #Todo: face culling to optimize performance
        #GL.glEnable(GL.GL_CULL_FACE)
        #GL.glCullFace(GL.GL_BACK)
        #GL.glFrontFace(GL.GL_CW)

#        GL.glShadeModel(GL.GL_FLAT)
#        GL.glClearColor(1.0, 1.0, 1.0, 0.0)
#
#        GL.glEnable(GL.GL_COLOR_MATERIAL)
#
#        GL.glEnable(GL.GL_LIGHTING)
#        GL.glEnable(GL.GL_LIGHT0)
#        GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION,  (0, 1, 1, 0))

    def showMainMenu(self):
        #Init pygame
        pygame.init()
        self.resizeWindow((800,600))

        #Initialize fonts
        GuiUtilities.initFonts()
            
        #Init OpenGl
        self.initOpenGl()

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
                self.handlePyGameEvent(event)
            
            #handle game events
            self.handleWarrensGameEvents()

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

            # Load the GPU program and Vertex Array Object
            GL.glUseProgram(self.openGlProgram)
            glBindVertexArray(self.VAO_id.value)

            #Send the cameraMatrix to the GPU
            camMatrix = self.cameraMatrix.get_inverse().to_opengl()
            GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, camMatrix)

            # Light must be transformed as well
#            GL.glLight(GL.GL_LIGHT0, GL.GL_POSITION,  (0, 1.5, 1, 0)) 
                    
            #Render the 3D view
            self.drawVBOs()

            GL.glUseProgram(0)

            #Render the HUD (health bar, XP bar, etc...)
            self.drawHUD()
                    
            # Show the screen
            pygame.display.flip()
            
            #If the player took a turn: Let the game play a turn
            if self._gamePlayerTookTurn: 
                self._game.playTurn()
                self._gamePlayerTookTurn = False
           


            
    def centerCameraOnActor(self, actor):
        """
        Centers the camera above the given actor.
        """
        #Set a new camera transform matrix
        self.cameraMatrix = Matrix44()
        #Translate it above the actor
        x = actor.tile.x
        y = actor.tile.y
        self.cameraMatrix.translate = (x * TILESIZE,y * TILESIZE, 4)

    def centerCameraOnMap(self):
        """
        Centers the camera above the current map
        """
        #Set a new camera transform matrix
        self.cameraMatrix = Matrix44()
        #Translate it above the center of the map
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        self.cameraMatrix.translate = (x * TILESIZE,y * TILESIZE-1, 10)

    def firstPersonCamera(self):
        """
        Moves the camera to a first person view for the player
        """
        #Set a new camera transform matrix
        self.cameraMatrix = Matrix44()
        #Translate it above the player
        x = self.game.player.tile.x
        y = self.game.player.tile.y
        self.cameraMatrix.translate = (x * TILESIZE,y * TILESIZE, TILESIZE)
        #Rotate to look ahead
        rotation_matrix = Matrix44.xyz_rotation(90,0,0)
        self.cameraMatrix *= rotation_matrix

    def loadVBOLevel(self):
        """
        Initialize a VBO for the basic level mesh
        To optimize performance this will only be called when a new level is loaded
        """
        #Create the vertex buffer on the GPU and remember the address ID
        self.VBO_level_id = GL.glGenBuffers(1)
        self.VBO_level_elements_id = GL.glGenBuffers(1)

        #Construct the data array that will be loaded into the buffer
        vertexData = []
        elementData = []

        #Store the vertex coordinates
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:
                #4 components per vertex: x, y, z, w
                #4 vertices: bottom of the rectangular tile area
                vertexData.extend((tile.x * TILESIZE,tile.y * TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
                #4 vertices: top of the rectangular tile area
                vertexData.extend((tile.x * TILESIZE,tile.y * TILESIZE, 2 * TILESIZE, 1.0))
                vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 2 * TILESIZE, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 2 * TILESIZE, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 2 * TILESIZE, 1.0))

        # Store the vertex colors
        self.VBO_level_color_offset = len(vertexData)
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:
                # 4 components per color: R, G, B, A, one color for every vertex
                color = self.normalizeColor(tile.color)
                # 4 vertices for the bottom
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                #4 vertices for the top
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))

        self.VBO_level_length = len(vertexData)

        # Create the element array
        offset = 0
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:

                # 2 Triangles for the bottom square
                elementData.extend((0+offset, 2+offset, 1+offset))
                elementData.extend((0+offset, 3+offset, 2+offset))
                if tile.blocked:
                    # 10 extra triangles to create a full block
                    elementData.extend((0+offset, 4+offset, 7+offset))
                    elementData.extend((0+offset, 7+offset, 3+offset))
                    elementData.extend((3+offset, 7+offset, 6+offset))
                    elementData.extend((3+offset, 6+offset, 2+offset))
                    elementData.extend((2+offset, 6+offset, 5+offset))
                    elementData.extend((2+offset, 5+offset, 1+offset))
                    elementData.extend((1+offset, 5+offset, 4+offset))
                    elementData.extend((1+offset, 4+offset, 0+offset))
                    elementData.extend((4+offset, 5+offset, 6+offset))
                    elementData.extend((4+offset, 6+offset, 7+offset))
                offset += 8

        self.VBO_level_elements_length = len(elementData)

        # Load the constructed vertex data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_level_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData), GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)

    def loadVBOActors(self):
        """
        Initialize a VBO for the actors
        This should be called whenever there is a change in actor positions or visibility
        """
        #Create the vertex buffer on the GPU and remember the address ID
        self.VBO_actors_id = GL.glGenBuffers(1)

        #Construct the data array that will be loaded into the buffer
        vertexData = []

        #Store the vertex coordinates
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                tile = actor.tile
                #4 components per vertex: x, y, z, w
                vertexData.extend((tile.x * TILESIZE,tile.y * TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))

        self.VBO_actors_color_offset = len(vertexData)

        #Store the vertex colors
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                #4 components per color: R, G, B, A
                color = self.normalizeColor(actor.color)
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))

        self.VBO_actors_length = len(vertexData)

        #Load the constructed data array into the buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_actors_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    def drawVBOs(self):
        #Draw level VBO
        #TODO: move out all the binding to an init VAO function
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_level_id)
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        colorDataStart = self.VBO_level_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        #Bind the element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        #Draw elements
        GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_level_elements_length, GL.GL_UNSIGNED_INT, None)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)

        #Draw actors VBO
        self.loadVBOActors()
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_actors_id)
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        colorDataStart = self.VBO_actors_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        vertices = self.VBO_actors_length / 2 / VERTEX_COMPONENTS
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, vertices)
        GL.glDisableVertexAttribArray(0)
        GL.glDisableVertexAttribArray(1)
    
        
    # def drawLevel(self, level):
    #     for tilerow in level.map.tiles:
    #         for tile in tilerow:
    #             if not tile.blocked:
    #                 self.drawTile(tile)
    
    # def drawTile(self, tile):
    #     GL.glBegin(GL.GL_QUADS)
    #     self.setDrawColor(tile.color)
    #     GL.glVertex3fv((tile.x * TILESIZE,tile.y * TILESIZE,0))
    #     GL.glVertex3fv((tile.x * TILESIZE + TILESIZE,tile.y * TILESIZE,0))
    #     #GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize,0))
    #     GL.glVertex3fv((tile.x * TILESIZE + TILESIZE,tile.y * TILESIZE + TILESIZE,0))
    #     #GL.glVertex3fv((tile.x * tileSize + tileSize,tile.y * tileSize + tileSize,0))
    #     GL.glVertex3fv((tile.x * TILESIZE,tile.y * TILESIZE + TILESIZE,0))
    #     #GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize + tileSize,0))
    #     #GL.glVertex3fv((tile.x * tileSize,tile.y * tileSize,0))
    #     GL.glEnd()
    
    # def drawActor(self, actor):
    #     tile = actor.tile
    #     GL.glPushMatrix()
    #     GL.glTranslatef(tile.x * TILESIZE + TILESIZE / 2, tile.y * TILESIZE + TILESIZE / 2, TILESIZE / 2)
    #     self.setDrawColor(actor.color)
    #     GLUT.glutSolidSphere(TILESIZE/2,32,32)
    #     GL.glPopMatrix()
        
        
    def normalizeColor(self,color):
        return (float(color[0])/250,float(color[1])/250,float(color[2])/250)

    def setDrawColor(self, color):
        GL.glColor3f(*self.normalizeColor(color))
    
    def drawText(self, position, textString, textSize):     
        font = pygame.font.Font (None, textSize)
        textSurface = font.render(textString, True, (255,255,255,255))#, (0,0,0,255))     
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        GL.glRasterPos3d(*position)     
        GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)
        
    def drawHUD(self):
        """
        For the HUD we use an Orthographic projection and some older style opengl code
        This is not using Vertex Buffers.
        """

        # No longer needed since working with custom Shaders
        # The relevant matrices are sent to the GPU using uniform variables
        #         GL.glMatrixMode(GL.GL_PROJECTION)
        #         GL.glPushMatrix()
        #         GL.glLoadIdentity()
        #         GL.glMatrixMode(GL.GL_MODELVIEW)
        #         GL.glPushMatrix()
        #         GL.glLoadIdentity()

        #Switch to Orthographic projection
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

        # No longer needed since working with custom Shaders
        # The relevant matrices are sent to the GPU using uniform variables
        #        #Switch back to perspective mode
        #        GLU.gluPerspective(60.0, (self.displayWidth/self.displayHeight), .1, 1000.)
        #         GL.glMatrixMode(GL.GL_PROJECTION)
        #         GL.glPopMatrix()
        #         GL.glMatrixMode(GL.GL_MODELVIEW)
        #         GL.glPopMatrix()

    def handleWarrensGameEvents(self):
        #Detect level change
        if self.level is not self.game.currentLevel:
            self.level = self.game.currentLevel
        #React to player death
        if self.game.player.state == Character.DEAD:
            self.centerCameraOnActor(self.game.player)

    def handlePyGameEvent(self, event):
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
            elif event.key == pygame.K_o:
                self.firstPersonCamera()
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