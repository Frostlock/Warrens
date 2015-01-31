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

import numpy as np
from math import radians, sqrt
import WarrensGUI.OpenGlUtilities as util

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
        self.loadVAOLevel()

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

    @property
    def lightingMatrix(self):
        """
        Returns the lighting matrix
        """
        return self._lightingMatrix

    @lightingMatrix.setter
    def lightingMatrix(self,matrix):
        """
        Sets the lighting matrix
        """
        self._lightingMatrix = matrix

    @property
    def directionTowardTheLight(self):
        return (0.866, 0.5, -5.001)

    #constructor
    def __init__(self):
        """
        Constructor to create a new GlApplication object.
        """
        # Initialize class variables
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

    def resizeWindow(self,displaySize):
        """
        Function to be called whenever window is resized.
        This function will ensure pygame display, glviewport and perspective matrix is recalculated
        """
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize,RESIZABLE|HWSURFACE|DOUBLEBUF|OPENGL)
        # Uncomment to run in fullscreen
        # pygame.display.set_mode(self.displaySize,FULLSCREEN|HWSURFACE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
        self.calculatePerspectiveMatrix()

    def calculatePerspectiveMatrix(self):
        """
        Sets the perspective matrix
        """
        pMat = np.zeros((4,4), 'f')

        fFrustumScale = 1.0
        fzNear = 0.1
        fzFar = 1000.0

        pMat[0,0] = fFrustumScale * 1
        pMat[1,1] = fFrustumScale * (float(self.displayWidth) / self.displayHeight)
        pMat[2,2] = (fzFar + fzNear) / (fzNear - fzFar)
        pMat[3,2] = (2 * fzFar * fzNear) / (fzNear - fzFar)
        pMat[2,3] = -1.0

        self.perspectiveMatrix = pMat

    def initOpenGl(self):
        """
        Initializes OpenGl settings and shaders
        """
        GLUT.glutInit([])

        # Compile Shaders into program object
        from OpenGL.GL.shaders import compileShader, compileProgram
        strVertexShader = open("WarrensGUI/Shaders/VertexShader.glsl").read()
        strFragmentShader = open("WarrensGUI/Shaders/FragmentShader.glsl").read()
        self.openGlProgram = compileProgram(
            compileShader(strVertexShader, GL.GL_VERTEX_SHADER),
            compileShader(strFragmentShader, GL.GL_FRAGMENT_SHADER)
        )

        # Create uniform variables for the compiled shaders
        GL.glUseProgram(self.openGlProgram)
        # Camera and perspective projection
        self.perspectiveMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "perspectiveMatrix")
        self.cameraMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "cameraMatrix")
        # Lighting
        self.dirToLightUnif = GL.glGetUniformLocation(self.openGlProgram, "dirToLight")
        self.lightIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "lightIntensity")
        self.ambientIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "ambientIntensity")
        self.lightingMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "lightingMatrix")
        # Fog of War
        self.playerPositionUnif = GL.glGetUniformLocation(self.openGlProgram, "playerPosition")
        self.fogDistanceUnif = GL.glGetUniformLocation(self.openGlProgram, "fogDistance")
        GL.glUniform1f(self.fogDistanceUnif, 4.0)

        # Generate Vertex Array Object for the level
        self.VAO_level = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_level)

        # Generate Vertex Array Object for the actors
        self.VAO_actors = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_actors)

        # Recalculate the perspective matrix
        self.calculatePerspectiveMatrix()

        GL.glUseProgram(0)

        # Enable depth testing
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthMask(GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glDepthRange(0.0, 1.0)

        # Enable alpha testing
        GL.glEnable(GL.GL_ALPHA_TEST)
        GL.glAlphaFunc(GL.GL_GREATER, 0.5)

        # Enable face culling
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK) # back side of each face will be culled
        GL.glFrontFace(GL.GL_CW) # front of the face is based on clockwise order of vertices

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

        #self.centerCameraOnActor(self.game.player)
        self.centerCameraOnMap()
        
        # Initialize speeds
        rotation_speed = radians(90.0)
        movement_speed = 5.0    
    
        while True:
            # handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handlePyGameEvent(event)
            
            # handle game events
            self.handleWarrensGameEvents()

            # Clear the screen, and z-buffer
            GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT);
                            
            time_passed = clock.tick()
            time_passed_seconds = time_passed / 1000.
            if time_passed_seconds <> 0 : self.FPS=1/time_passed_seconds
            
            pressed = pygame.key.get_pressed()
            
            # Reset rotation and movement directions
            # rotation_direction.set(0.0, 0.0, 0.0)
            rotation_direction = np.array((0.0, 0.0, 0.0), 'f')
            # movement_direction.set(0.0, 0.0, 0.0)
            movement_direction = np.array((0.0, 0.0, 0.0), 'f')

            # Modify direction vectors for key presses
            if pressed[K_LEFT]:
                # rotation_direction.y = +1.0
                rotation_direction[1] = +1.0
            elif pressed[K_RIGHT]:
                # rotation_direction.y = -1.0
                rotation_direction[1] = -1.0
            if pressed[K_UP]:
                # rotation_direction.x = -1.0
                rotation_direction[0] = -1.0
            elif pressed[K_DOWN]:
                # rotation_direction.x = +1.0
                rotation_direction[0] = +1.0
            if pressed[K_PAGEUP]:
                # rotation_direction.z = -1.0
                rotation_direction[2] = -1.0
            elif pressed[K_PAGEDOWN]:
                # rotation_direction.z = +1.0
                rotation_direction[2] = +1.0
            if pressed[K_HOME]:
                # movement_direction.z = -1.0
                movement_direction[2] = -1.0
            elif pressed[K_END]:
                # movement_direction.z = +1.0
                movement_direction[2] = +1.0
            
            # Calculate rotation matrix and multiply by camera matrix    
            rotation = rotation_direction * rotation_speed * time_passed_seconds
            rotation_matrix = util.rotationMatrix44(*rotation)
            # if you do this the other way around you rotate the world before moving the camera
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

            # Calcluate movment and add it to camera matrix translate
            heading = self.cameraMatrix[:3,2] #forward
            movement = heading * movement_direction * movement_speed * time_passed_seconds
            movement_matrix = util.translationMatrix44(*movement)
            # if you do this the other way around you move the world before moving the camera
            self.cameraMatrix = movement_matrix.dot(self.cameraMatrix)

            # Refresh the actors VAO (some actors might have moved)
            self.loadVAOActors()
                    
            # Render the 3D view (Vertex Array Buffers
            self.drawVBAs()

            # Render the HUD (health bar, XP bar, etc...)
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
        x = actor.tile.x
        y = actor.tile.y
        self.cameraMatrix = util.translationMatrix44(x * TILESIZE, y * TILESIZE, 4.0)

    def centerCameraOnMap(self):
        """
        Centers the camera above the current map
        """
        map = self.game.currentLevel.map
        x = map.width / 2
        y = map.height / 2
        self.cameraMatrix = util.translationMatrix44(x * TILESIZE,y * TILESIZE -1, 10)

    def firstPersonCamera(self):
        """
        Moves the camera to a first person view for the player
        """
        #Translate above the player
        x = self.game.player.tile.x
        y = self.game.player.tile.y
        #TODO: Fix this routine, also why is there -1 in next line?
        self.cameraMatrix = util.translationMatrix44(x * TILESIZE,y * TILESIZE-1, TILESIZE)
        #Rotate to look ahead
        rotation_matrix = util.rotationMatrix44(-180,0,0)
        self.cameraMatrix = self.cameraMatrix.dot(rotation_matrix)

    def playerPosition(self):
        """
        :return: The position in 3D modelspace of the player
        """
        playerX = self.game.player.tile.x * TILESIZE + (TILESIZE / 2)
        playerY = self.game.player.tile.y * TILESIZE + (TILESIZE / 2)
        playerZ = TILESIZE / 2
        return (playerX, playerY, playerZ, 1.0)

    def loadVAOLevel(self):
        """
        Initializes the context of the level VAO
        The level VAO contains the basic level mesh
        To optimize performance this will only be called when a new level is loaded
        """
        # Create vertex buffers on the GPU, remember the address IDs
        self.VBO_level_id = GL.glGenBuffers(1)
        self.VBO_level_elements_id = GL.glGenBuffers(1)

        # Construct the data array that will be loaded into the buffer
        vertexData = []
        elementData = []

        # Store the vertex coordinates
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:
                if tile.blocked:
                    height = TILESIZE
                else:
                    height = 0.0
                # 4 components per vertex: x, y, z, w
                # 4 vertices: bottom of the rectangular tile area
                vertexData.extend((tile.x * TILESIZE,tile.y * TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
                # 4 vertices: top of the rectangular tile area
                vertexData.extend((tile.x * TILESIZE,tile.y * TILESIZE, height, 1.0))
                vertexData.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, height, 1.0))

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
                # 4 vertices for the top
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))

        # Store the vertex normals
        self.VBO_level_normals_offset = len(vertexData)
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:
                # 3 components per normal: x, y, z
                # 4 vertex normals for the bottom
                vertexData.extend((-1.0,-1.0,-0.01))
                vertexData.extend((1.0,-1.0,-0.01))
                vertexData.extend((1.0,1.0,-0.01))
                vertexData.extend((-1.0,1.0,-0.01))
                # 4 vertex normals for the top
                vertexData.extend((-1.0,-1.0,-1.0))
                vertexData.extend((1.0,-1.0,-1.0))
                vertexData.extend((1.0,1.0,-1.0))
                vertexData.extend((-1.0,1.0,-1.0))


        self.VBO_level_length = len(vertexData)

        # Create the element array
        offset = 0
        for tileRow in self.game.currentLevel.map.tiles:
            for tile in tileRow:
                # 12 Triangles for a complete block
                elementData.extend((0+offset, 2+offset, 1+offset))
                elementData.extend((0+offset, 3+offset, 2+offset))
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

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_level)

        # Load the constructed vertex and color data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_level_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_level_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_level_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData), GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def loadVAOActors(self):
        """
        Initializes the context of the actors VAO
        This should be called whenever there is a change in actor positions or visibility
        """
        # Create the vertex buffer on the GPU and remember the address ID
        self.VBO_actors_id = GL.glGenBuffers(1)
        self.VBO_actors_elements_id = GL.glGenBuffers(1)

        # Construct the data array that will be loaded into the buffer
        vertexData = []
        elementData = []

        # Store the vertex coordinates
        offset = 0.2
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                tile = actor.tile
                # 4 components per vertex: x, y, z, w
                vertexData.extend((tile.x * TILESIZE + offset,tile.y * TILESIZE + offset, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + offset, 0.0, 1.0))
                vertexData.extend((tile.x * TILESIZE + (TILESIZE / 2) , tile.y * TILESIZE + (TILESIZE / 2), TILESIZE, 1.0))

        self.VBO_actors_color_offset = len(vertexData)

        # Store the vertex colors
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                # 4 components per color: R, G, B, A
                color = self.normalizeColor(actor.color)
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))
                vertexData.extend((color[0],color[1],color[2],1.0))

        # Store the vertex normals
        self.VBO_actors_normals_offset = len(vertexData)
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                # 3 components per normal: x, y, z
                # 4 vertex normals for the bottom
                vertexData.extend((-1.0,1.0,-0.2))
                vertexData.extend((1.0,1.0,-0.2))
                vertexData.extend((1.0,-1.0,-0.2))
                vertexData.extend((-1.0,-1.0,-0.2))
                # 1 vertex normals for the top
                vertexData.extend((0.0,0.0,-1.0))

        self.VBO_actors_length = len(vertexData)

        # Create the element array
        offset = 0
        for vTile in self.game.currentLevel.map.visible_tiles:
            for actor in vTile.actors:
                # Triangles
                elementData.extend((0+offset, 2+offset, 1+offset))
                elementData.extend((0+offset, 3+offset, 2+offset))
                elementData.extend((0+offset, 4+offset, 3+offset))
                elementData.extend((3+offset, 4+offset, 2+offset))
                elementData.extend((2+offset, 4+offset, 1+offset))
                elementData.extend((1+offset, 4+offset, 0+offset))
                offset += 5

        self.VBO_actors_elements_length = len(elementData)

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_actors)

        # Load the constructed vertex and color data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_actors_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_actors_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_actors_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_actors_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData), GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def drawVBAs(self):
        DEBUG_GLSL = False
        if DEBUG_GLSL: print '\n\nDEBUG MODE: Simulating GLSL calculation:\n'

        GL.glUseProgram(self.openGlProgram)

        # Bind Level VAO context
        glBindVertexArray(self.VAO_level)
        # Load uniforms
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix,(16)))
        if DEBUG_GLSL: print "perspectiveMatrix"
        if DEBUG_GLSL: print self.perspectiveMatrix

        camMatrix = np.linalg.inv(self.cameraMatrix)
        GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(camMatrix,(16)))
        if DEBUG_GLSL: print "camMatrix"
        if DEBUG_GLSL: print camMatrix

        lightMatrix = camMatrix[:3,:3] # Extracts 3*3 matrix out of 4*4
        if DEBUG_GLSL: print "LightMatrix"
        if DEBUG_GLSL: print lightMatrix
        GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix,(9)))

        if DEBUG_GLSL: print "Light intensity: (0.8, 0.8, 0.8, 1.0)"
        GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
        if DEBUG_GLSL: print "Ambient intensity: (0.2, 0.2, 0.2, 1.0)"
        GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)
        GL.glUniform4f(self.playerPositionUnif, *self.playerPosition())

        # Calculate direction of light in camera space
        lightDirCameraSpace = lightMatrix.dot(self.directionTowardTheLight)
        if DEBUG_GLSL: print "Direction to light in Camera Space"
        if DEBUG_GLSL: print lightDirCameraSpace
        GL.glUniform3f(self.dirToLightUnif, lightDirCameraSpace[0],lightDirCameraSpace[1],lightDirCameraSpace[2])

        #LM = self.cameraMatrix.get_inverse()
        #print LM
        #normCamSpace = LM.transform_vec3((1,-1,-1)).normalize()
        #if DEBUG_GLSL: print "Normalized normal in cameraspace"
        #if DEBUG_GLSL: print normCamSpace
        #cosAngIncidence = normCamSpace.dot(lightDirCameraSpace)
        #if DEBUG_GLSL: print "cosine (dot product between normal and direction to light "
        #if DEBUG_GLSL: print cosAngIncidence
        #if DEBUG_GLSL: print "negative means no color output!"

        # Bind element array
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_level_elements_id)
        # Draw elements
        GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_level_elements_length, GL.GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # Bind Actors VAO context
        glBindVertexArray(self.VAO_actors)
        # Load uniforms
        GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix,(16)))

        camMatrix = np.linalg.inv(self.cameraMatrix)
        GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(camMatrix,(16)))

        lightMatrix = camMatrix[:3,:3] # Extracts 3*3 matrix out of 4*4
        GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix, (9)))

        GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
        GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)
        GL.glUniform4f(self.playerPositionUnif, *self.playerPosition())

        # Calculate direction of light in camera space
        lightDirCameraSpace = lightMatrix.dot(self.directionTowardTheLight)
        GL.glUniform3f(self.dirToLightUnif, lightDirCameraSpace[0],lightDirCameraSpace[1],lightDirCameraSpace[2])

        # Bind element array
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_actors_elements_id)
        # Draw elements
        GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_actors_elements_length, GL.GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        GL.glUseProgram(0)
        
        
    def normalizeColor(self,color):
        return (float(color[0])/250,float(color[1])/250,float(color[2])/250)

    def setDrawColor(self, color):
        GL.glColor3f(*self.normalizeColor(color))
    
    def drawText(self, position, textString, textSize):     
        font = pygame.font.Font (None, textSize)
        textSurface = font.render(textString, True, (255,255,255,255))# , (0,0,0,255))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        GL.glRasterPos3d(*position)     
        GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)
        
    def drawHUD(self):
        """
        For the HUD we use an Orthographic projection and some older style opengl code
        This is not using Vertex Buffers.
        """
        # Switch to Orthographic projection
        GL.glOrtho(0.0, self.displayWidth, self.displayHeight, 0.0, -1.0, 10.0)
        
        GL.glClear(GL.GL_DEPTH_BUFFER_BIT)
        
        # Level name
        GL.glLoadIdentity()
        self.drawText((-0.98,0.9,0), self.game.currentLevel.name,24)
        
        # Player name
        GL.glLoadIdentity()
        self.drawText((-0.98,-0.85,0), self.game.player.name + " (Lvl " + str(self.game.player.playerLevel) + ")",18)
        
        # Health Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98,-0.94,0)
        current = self.game.player.currentHitPoints
        maximum = self.game.player.maxHitPoints
        barWidth = 0.46
        barHeight =0.08
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(GuiCONSTANTS.COLOR_BAR_HEALTH_BG)
        # Draw vertices (clockwise for face culling!)
        GL.glVertex2f(0.0, 0.0)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(barWidth, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth/maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(GuiCONSTANTS.COLOR_BAR_HEALTH)
            # Draw vertices (clockwise for face culling!)
            GL.glVertex2f(0.0, 0.0)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(filWidth, 0.0)
            GL.glEnd()
        
        # Xp Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98,-0.99,0)
        current = self.game.player.xp
        maximum = self.game.player.nextLevelXp
        barWidth = 0.46
        barHeight =0.04
        GL.glBegin(GL.GL_QUADS);
        self.setDrawColor(GuiCONSTANTS.COLOR_BAR_XP_BG)
        # Draw vertices (clockwise for face culling!)
        GL.glVertex2f(0.0, 0.0)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(barWidth, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth/maximum
            GL.glBegin(GL.GL_QUADS);
            self.setDrawColor(GuiCONSTANTS.COLOR_BAR_XP)
            # Draw vertices (clockwise for face culling!)
            GL.glVertex2f(0.0, 0.0)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(filWidth, 0.0)
            GL.glEnd()

        # FPS
        GL.glLoadIdentity()
        self.drawText((-0.98,-1,0), str(self.FPS),12)

        # Right side: render game messages
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

    def handleWarrensGameEvents(self):
        # Detect level change
        if self.level is not self.game.currentLevel:
            self.level = self.game.currentLevel
        # React to player death
        if self.game.player.state == Character.DEAD:
            self.centerCameraOnActor(self.game.player)

    def handlePyGameEvent(self, event):
        # Quit
        if event.type == pygame.QUIT: sys.exit()
        
        # Window resize
        elif event.type == VIDEORESIZE:
            self.resizeWindow(event.dict['size'])
        
        # mouse
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
        
        # keyboard
        elif event.type == pygame.KEYDOWN:
            # Handle keys that are always active
            if event.key == pygame.K_ESCAPE:
                sys.exit() 
            elif event.key == pygame.K_p:
                self.centerCameraOnActor(self.game.player)
            elif event.key == pygame.K_m:
                self.centerCameraOnMap()
            elif event.key == pygame.K_o:
                self.firstPersonCamera()
            # Handle keys that are active while playing
            if self.game.state == Game.PLAYING:
                player = self.game.player
                if player.state == Character.ACTIVE:
                    # movement
                    global movement_keys
                    if event.key in movement_keys:
                        player.tryMoveOrAttack(*movement_keys[event.key])
                        #TODO: Decide in the game code if turn is taken or not, tookATurn should be bool on player which can be reset by the game.
                        self._gamePlayerTookTurn = True
                    
                    # portal keys
                    elif event.key == pygame.K_LESS:
                        # check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT): 
                            player.tryFollowPortalDown()
                        else:
                            player.tryFollowPortalUp()
                    # inventory
                    elif event.key == pygame.K_i:
                        self.useInventory()
                    elif event.key == pygame.K_d:
                        self.dropInventory()
                    # interact
                    elif event.key == pygame.K_COMMA:
                        player.tryPickUp()
                    
                    # update field of vision
                    if self._gamePlayerTookTurn:
                        self.game.currentLevel.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)

    def eventDraggingStart(self):
        self._dragging = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventDraggingStop(self):
        self._dragging = False

    def eventRotatingStart(self):
        self._rotating = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventRotatingStop(self):
        self._rotating = False
        
    def eventMouseMovement(self):
        # check for on going drag
        if self._dragging:
            # get relative distance of mouse since last call to get_rel()
            mouseMove = pygame.mouse.get_rel()
            
            # Get the left right direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,0]
            y= self.cameraMatrix[1,0]
            z= self.cameraMatrix[2,0]
            w= self.cameraMatrix[3,0]
            factor =  -1.0 * mouseMove[0] / (w*w)
            # Translate along this direction
            translation_matrix = util.translationMatrix44(factor * x, factor * y, factor * z)
            self.cameraMatrix = translation_matrix .dot(self.cameraMatrix)
            
            # Get the up down direction of the camera from the current modelview matrix
            x= self.cameraMatrix[0,1]
            y= self.cameraMatrix[1,1]
            z= self.cameraMatrix[2,1]
            w= self.cameraMatrix[3,1]
            factor = 1.0 * mouseMove[1] / (w*w)
            print self.cameraMatrix[:,1]
            # Translate along this direction
            translation_matrix = util.translationMatrix44(factor * x,factor * y, factor * z)
            self.cameraMatrix = translation_matrix .dot(self.cameraMatrix)
            
        elif self._rotating:
            # get relative distance of mouse since last call to get_rel()
            mouseMove = pygame.mouse.get_rel()
                     
            # Get the left right direction of the camera from the current modelview matrix
            # We'll use this as the rotation axis for the up down movement
            x= self.cameraMatrix[0,0] * mouseMove[1]
            y= self.cameraMatrix[1,0] * mouseMove[1]
            z= self.cameraMatrix[2,0] * mouseMove[1]
            w= self.cameraMatrix[3,0] * 100
            rotation_matrix = util.rotationMatrix44(x/w,y/w,z/w)
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)
            
            #Get the up down direction of the camera from the current modelview matrix
            # We'll use this as the rotation axis for the left right movement
            x= self.cameraMatrix[0,1] * -1.0 * mouseMove[0]
            y= self.cameraMatrix[1,1] * -1.0 * mouseMove[0]
            z= self.cameraMatrix[2,1] * -1.0 * mouseMove[0]
            w= self.cameraMatrix[3,1] * 100
            rotation_matrix = util.rotationMatrix44(x/w,y/w,z/w)
            self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)
            
    def eventZoomIn(self):
        """
        Event handler for ZoomIn event.
        This will translate the camera matrix to zoom in.
        """
        # Get the direction of the camera from the camera matrix
        heading = self.cameraMatrix[:3,2] * -1 #backward
        # Translate the camera along z component of this direction
        translation_matrix = util.translationMatrix44(0.,0.,heading[2])
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)

    def eventZoomOut(self):
        """
        Event handler for ZoomOut event.
        This will translate the camera matrix to zoom out.
        """
        # Get the direction of the camera from the camera matrix
        heading = self.cameraMatrix[:3,2] #forward
        # Translate the camera along z component of this direction
        translation_matrix = util.translationMatrix44(0.,0.,heading[2])
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)