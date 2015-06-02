"""
Created on Jan 12, 2015

Gui based on PyGame and PyOpenGl.

Special thanks to these two for getting me started!
http://www.arcsynthesis.org/gltut/
http://www.willmcgugan.com/blog/tech/2007/6/4/opengl-sample-code-for-pygame/

@author: Frost
"""

import pygame
from pygame.locals import *

from OpenGL import GL
from OpenGL.GL.ARB.vertex_array_object import glBindVertexArray
from OpenGL import GLUT
from ctypes import c_void_p

from math import sin, cos, sqrt, radians
import numpy as np

from WarrensGame.Game import Game
from WarrensGame.Actors import Character

from WarrensGUI.Util import Utilities
import WarrensGUI.Util.OpenGlUtilities as og_util

from WarrensGUI.Util.LevelSceneObject import LevelSceneObject
from WarrensGUI.Util.ActorsSceneObject import ActorsSceneObject
from WarrensGUI.Util.vec3 import vec3
from WarrensGUI.Util.Constants import *
from WarrensGUI.States.MainMenuState import MainMenuState
from WarrensGUI.States.GameState import GameState

class MainWindow(object):
    '''
    This class represents the main window of the application.
    To avoid this class becoming too big and to allow for different draw loops and key handlers within different
    screens in the application we use State objects to govern the state of the GUI.
    '''
    @property
    def game(self):
        """
        Returns the current game.
        """
        return self._game

    @game.setter
    def game(self, game):
        self._game = game
        self.refreshStaticObjects()

    @property
    def level(self):
        """
        Returns the current level.
        """
        return self.game.currentLevel

    @property
    def state(self):
        '''
        Current state of this window. The state governs the key handling and drawing.
        :return: State object
        '''
        return self._state

    @state.setter
    def state(self,state):
        self._state = state
        # Enter main loop of the new state
        state.mainLoop()

    @property
    def clock(self):
        '''
        PyGame clock utility
        :return: PyGame clock object
        '''
        return self._clock

    @property
    def FPS(self):
        '''
        FPS - Frames per second
        This property returns the number of frames based on previous calls to this property.
        :return:
        '''
        time_passed_seconds = self.clock.tick() / 1000.
        if time_passed_seconds <> 0: return 1 / time_passed_seconds
        else: return 0

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
        """
        Property to store the program ID of the openGl Program that is in use
        :return: OpenGl ID
        """
        return self._openGlProgram

    @openGlProgram.setter
    def openGlProgram(self, program):
        """
        Sets the OpenGl program ID.
        :param program: OpenGl program ID to be stored
        :return:
        """
        self._openGlProgram = program

    @property
    def cameraMatrix(self):
        """
        Returns the camera matrix

        For reference:

        RT = right
        UP = up
        BK = back
        POS = position/translation
        US = uniform scale

                       | [RT.x] [UP.x] [BK.x] [POS.x] |
        cameraMatrix = | [RT.y] [UP.y] [BK.y] [POS.y] |
                       | [RT.z] [UP.z] [BK.z] [POS.z] |
                       | [    ] [    ] [    ] [US   ] |
        """
        return self._cameraMatrix

    @cameraMatrix.setter
    def cameraMatrix(self, matrix):
        """
        Sets the camera matrix
        """
        self._cameraMatrix = matrix

    @property
    def cameraMode(self):
        return self._cameraMode

    @cameraMode.setter
    def cameraMode(self, mode):
        self._cameraMode = mode

    @property
    def cameraDistance(self):
        return self._cameraDistance

    @cameraDistance.setter
    def cameraDistance(self,distance):
        self._cameraDistance = distance

    @property
    def cameraAngleXY(self):
        """
        Camera angle in the XY plane.
        :return: Angle in degrees
        """
        return self._cameraAngleXY

    @cameraAngleXY.setter
    def cameraAngleXY(self, angle):
        """
        Set camera angle in the XY plane. The give angle will be normalized to a 0-360 value.
        :param angle: New camera angle
        :return: None
        """
        if angle > 360:
            self.cameraAngleXY= angle - 360
        elif angle < 0:
            self.cameraAngleXY = 360 + angle
        else:
            self._cameraAngleXY = angle

    @property
    def cameraAngleXZ(self):
        """
        Camera angle in the XZ plane.
        :return: Angle in degrees
        """
        return self._cameraAngleXZ

    @cameraAngleXZ.setter
    def cameraAngleXZ(self, angle):
        """
        Set camera angle in the XZ plane. The give angle will be normalized to a 0-90 value.
        :param angle: New camera angle
        :return: None
        """
        if angle > 90:
            self.cameraAngleXZ= angle - 90
        elif angle < 0:
            self.cameraAngleXZ = 90 + angle
        else:
            self._cameraAngleXZ = angle

    @property
    def perspectiveMatrix(self):
        """
        Returns the perspective matrix
        """
        return self._perspectiveMatrix

    @perspectiveMatrix.setter
    def perspectiveMatrix(self, matrix):
        """
        Sets the perspective matrix
        """
        self._perspectiveMatrix = matrix

    @property
    def lightingMatrix(self):
        """
        Returns the lighting matrix
        """
        return self._lightingMatrix

    @lightingMatrix.setter
    def lightingMatrix(self, matrix):
        """
        Sets the lighting matrix
        """
        self._lightingMatrix = matrix

    @property
    def lightPosition(self):
        return (10.866, 5, -15.001)

    @property
    def fogActive(self):
        return False

    @property
    def staticObjects(self):
        return self._staticObjects

    @staticObjects.setter
    def staticObjects(self, objectsArray):
        self._staticObjects = objectsArray

    @property
    def dynamicObjects(self):
        return self._dynamicObjects

    @dynamicObjects.setter
    def dynamicObjects(self, objectsArray):
        self._dynamicObjects = objectsArray


    def __init__(self):
        """
        Constructor to create a new main window.
        """
        # Initialize class properties
        self._game = None
        self.previousPassLevel = None
        self._displaySize = DISPLAY_SIZE
        self._openGlProgram = None
        self._cameraMatrix = None
        self._cameraMode = 0
        self._cameraDistance = 4.0
        self._cameraAngleXY = 0
        self._cameraAngleXZ = 45
        self._perspectiveMatrix = None
        self._lightingMatrix = None
        self._dragging = False
        self._rotating = False
        self._state = None
        self._clock = pygame.time.Clock()
        # Initialize uniform class variables
        self.perspectiveMatrixUnif = None
        self.cameraMatrixUnif = None
        self.lightPosUnif = None
        self.lightIntensityUnif = None
        self.ambientIntensityUnif = None
        self.lightingMatrixUnif = None
        self.playerPositionUnif = None
        self.fogDistanceUnif = None
        self.fogActiveUnif = None

        self.dynamicObjects = []
        self.staticObjects = []

        # Init pygame
        pygame.init()
        self.resizeWindow(self.displaySize)

        #Init OpenGl
        self.initOpenGl()

        #switch to main menu state
        self.state = MainMenuState(self)

    def resizeWindow(self, displaySize):
        """
        Function to be called whenever window is resized.
        This function will ensure pygame display, glviewport and perspective matrix is recalculated
        """
        self._displaySize = displaySize
        width, height = displaySize
        pygame.display.set_mode(self.displaySize, RESIZABLE | HWSURFACE | DOUBLEBUF | OPENGL)
        # Uncomment to run in fullscreen
        # pygame.display.set_mode(self.displaySize,FULLSCREEN|HWSURFACE|DOUBLEBUF|OPENGL)
        GL.glViewport(0, 0, width, height)
        self.calculatePerspectiveMatrix()

    def calculatePerspectiveMatrix(self):
        """
        Sets the perspective matrix
        """
        pMat = np.zeros((4, 4), 'f')

        fFrustumScale = 1.0
        fzNear = 0.1
        fzFar = 1000.0

        pMat[0, 0] = fFrustumScale * 1
        pMat[1, 1] = fFrustumScale * (float(self.displayWidth) / self.displayHeight)
        pMat[2, 2] = (fzFar + fzNear) / (fzNear - fzFar)
        pMat[3, 2] = (2 * fzFar * fzNear) / (fzNear - fzFar)
        pMat[2, 3] = -1.0

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
        self.lightPosUnif = GL.glGetUniformLocation(self.openGlProgram, "lightPos")
        self.lightIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "lightIntensity")
        self.ambientIntensityUnif = GL.glGetUniformLocation(self.openGlProgram, "ambientIntensity")
        self.lightingMatrixUnif = GL.glGetUniformLocation(self.openGlProgram, "lightingMatrix")
        # Fog of War
        self.playerPositionUnif = GL.glGetUniformLocation(self.openGlProgram, "playerPosition")
        self.fogDistanceUnif = GL.glGetUniformLocation(self.openGlProgram, "fogDistance")
        GL.glUniform1f(self.fogDistanceUnif, 4.0)
        self.fogActiveUnif = GL.glGetUniformLocation(self.openGlProgram, "fogActive")

        # Generate Vertex Array Object for the static objects
        self.VAO_static = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_static)

        # Generate Vertex Array Object for the dynamic objects
        self.VAO_dynamic = GL.GLuint(0)
        GL.ARB.vertex_array_object.glGenVertexArrays(1, self.VAO_dynamic)

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
        GL.glCullFace(GL.GL_BACK)  # back side of each face will be culled
        GL.glFrontFace(GL.GL_CCW)  # front of the face is based on counter clockwise order of vertices

    def legacyGui(self):
        '''
        This function switches to the legacy GUI.
        :return:
        '''
        # Switch to legacy GUI
        # To achieve a clean re-initialization of pygame we explicitly quit pygame before starting the legacy GUI.
        pygame.quit()
        from WarrensGUI.Deprecated.GuiApplication import GuiApplication
        application = GuiApplication()
        application.showMainMenu()
        # Switch back to regular GUI
        pygame.quit()
        pygame.init()
        self.resizeWindow(self.displaySize)
        self.initOpenGl()

    def playNewGame(self):
        #Initialize a new game
        self.game = Game()
        self.game.resetGame()
        # Set Game state (which contains the main loop)
        self.state = GameState(self,self.state)

    #TODO: loading and saving to be implemented
    def saveGame(self):
        print "Called Save but not implemented yet"
        pass

    def loadGame(self):
        print "Called Load but not implemented yet"
        pass

    def DEPRECATED_playGame(self):
        # #Init Game
        # self._game = Game()
        # self.game.resetGame()

        ### clock = pygame.time.Clock()

        # #self.centerCameraOnActor(self.game.player)
        # self.centerCameraOnMap()

        # Initialize speeds
        rotation_speed = radians(90.0)
        movement_speed = 25.0

        while True:
            # # handle pygame (GUI) events
            # events = pygame.event.get()
            # for event in events:
            #     self.handlePyGameEvent(event)
            #
            # # handle game events
            # self.handleWarrensGameEvents()

            # # Clear the screen, and z-buffer
            # GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

            # time_passed = self.clock.tick()
            # time_passed_seconds = time_passed / 1000.
            # if time_passed_seconds <> 0: self.FPS = 1 / time_passed_seconds

            #get a tuple with the press status of all keys
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
                self.cameraMode = CAM_FREE
            elif pressed[K_RIGHT]:
                # rotation_direction.y = -1.0
                rotation_direction[1] = -1.0
                self.cameraMode = CAM_FREE
            if pressed[K_UP]:
                # rotation_direction.x = -1.0
                rotation_direction[0] = -1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_DOWN]:
                # rotation_direction.x = +1.0
                rotation_direction[0] = +1.0
                self.cameraMode = CAM_FREE
            if pressed[K_PAGEUP]:
                # rotation_direction.z = -1.0
                rotation_direction[2] = -1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_PAGEDOWN]:
                # rotation_direction.z = +1.0
                rotation_direction[2] = +1.0
                self.cameraMode = CAM_FREE
            if pressed[K_HOME]:
                # movement_direction.z = -1.0
                movement_direction[2] = +1.0
                self.cameraMode = CAM_FREE
            elif pressed[K_END]:
                # movement_direction.z = +1.0
                movement_direction[2] = -1.0
                self.cameraMode = CAM_FREE

            # Calculate rotation matrix and multiply by camera matrix    
            rotation = rotation_direction * rotation_speed * time_passed_seconds
            rotation_matrix = og_util.rotationMatrix44(*rotation)
            #print rotation_matrix
            # "rotate the world around the origin"
            #self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)
            # "rotate the camera"
            self.cameraMatrix = self.cameraMatrix.dot(rotation_matrix)

            # Calcluate movment and add it to camera matrix translate
            heading = self.cameraMatrix[:3, 2]  # Forward direction
            movement = heading * movement_direction * movement_speed * time_passed_seconds
            movement_matrix = og_util.translationMatrix44(*movement)
            # "move the world"
            #Since the camera direction is always the Z-axis this would just move the world up and down along the Z-axis
            #self.cameraMatrix = movement_matrix.dot(self.cameraMatrix)
            # "move the camera
            self.cameraMatrix = self.cameraMatrix.dot(movement_matrix)

            ## MOVED # First person camera
            ## if self.cameraMode == CAM_FIRSTPERSON:
            ##     self.firstPersonCamera()
            ## elif self.cameraMode == CAM_ACTOR:
            ##     self.centerCameraOnActor(self.game.player)

            # # Refresh the actors VAO (some actors might have moved)
            # self.refreshDynamicObjects()
            # self.loadVAODynamicObjects()

            # # Refresh the actors VAO (some actors might have moved)
            # self.refreshDynamicObjects()
            # self.loadVAODynamicObjects()
            #
            # # Render the 3D view (Vertex Array Buffers
            # self.drawVBAs()
            #
            # # Render the HUD (health bar, XP bar, etc...)
            # self.drawHUD()

            # # Show the screen
            # pygame.display.flip()

    def cycleCameraMode(self):
        """
        Cycle through the different camera modes.
        :return: None
        """
        self.cameraMode += 1
        if self.cameraMode > 3: self.cameraMode = 0

    def setCameraIsometricView(self):
        """
        Sets the camera to an isometric view based on the current camera angle in the XY plane and the camera distance.
        :return: None
        """
        self.cameraMode = CAM_ISOMETRIC

        x, y, z, w = self.getPlayerPosition()

        zOffset = sin(radians(self.cameraAngleXZ)) * self.cameraDistance
        XYplaneDistance = sqrt(self.cameraDistance * self.cameraDistance - zOffset * zOffset)
        xOffset = sin(radians(self.cameraAngleXY)) * XYplaneDistance
        yOffset = cos(radians(self.cameraAngleXY)) * XYplaneDistance
        eye = vec3(x + xOffset, y + yOffset, z + zOffset)

        lookAt = vec3(x,y,z)

        up = vec3(0,0,1)

        self.lookAt(eye,lookAt,up)

    def setCameraCenterOnActor(self, actor):
        """
        Centers the camera above the given actor.
        :return: None
        """
        self.cameraMode = CAM_ACTOR
        x = actor.tile.x
        y = actor.tile.y
        self.cameraMatrix = og_util.translationMatrix44(-1 * x * TILESIZE, -1 * y * TILESIZE, -1 * self.cameraDistance)

    def setCameraCenterOnMap(self):
        """
        Centers the camera above the current map.
        :return: None
        """
        self.cameraMode = CAM_MAP
        map = self.level.map
        x = map.width / 2
        y = map.height / 2
        yOffset = 1 #moves the view on the map slightly so it does not overlap with the hud
        self.cameraMatrix = og_util.translationMatrix44(-1 * x * TILESIZE, -1 * y * TILESIZE + yOffset, -10)

    def setCameraFirstPersonView(self):
        """
        Moves the camera to a first person view for the player.
        :return: None
        """
        self.cameraMode = CAM_FIRSTPERSON

        #OLD CODE
        # # Translate above the player
        # x, y, z, w = self.getPlayerPosition()
        # self.cameraMatrix = og_util.translationMatrix44(-x, -y, -z)
        # # Rotate to look in player direction
        # print self.game.player.direction
        # dx = self.game.player.direction[0]
        # dy = self.game.player.direction[1]
        # import numpy as np
        # directionAngle = -1 * np.arcsin(dx/(np.sqrt(dx*dx + dy*dy)))
        # if dy < 0 :
        #     directionAngle= np.pi + np.arcsin(dx/(np.sqrt(dx*dx + dy*dy)))
        #
        # playerRotation = og_util.rotationMatrix44(0, 0, directionAngle)
        # # Rotate upward to look ahead
        # rotation_matrix = og_util.rotationMatrix44(radians(90), 0, 0).dot(playerRotation)
        # print rotation_matrix
        # self.cameraMatrix = rotation_matrix.dot(self.cameraMatrix)

        #Eye at player position
        x, y, z, w = self.getPlayerPosition()
        eye = vec3(x,y,z)
        dx = self.game.player.direction[0]
        dy = self.game.player.direction[1]
        lookAt = vec3(x + dx, y + dy, z)
        up = vec3(0,0,1)
        self.cameraMatrix = og_util.lookAtMatrix44(eye,lookAt,up)

    # Window utility functions, these are used by the window states.

    def drawText(self, position, textString, textSize, color):
        font = pygame.font.Font(None, textSize)
        textSurface = font.render(textString, True, color)
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        GL.glRasterPos3d(*position)
        GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textData)

    def lookAt(self, eye, center, up):
        self.cameraMatrix = og_util.lookAtMatrix44(eye, center, up)

    def getPlayerPosition(self):
        """
        Returns the current position of the player in model space
        :rtype : Tuple (x, y, z, w)
        :return: The position in 3D model space of the player
        """
        if self.game is None: return (0, 0, 0, 1.0)
        playerX = self.game.player.tile.x * TILESIZE + (TILESIZE / 2)
        playerY = self.game.player.tile.y * TILESIZE + (TILESIZE / 2)
        playerZ = TILESIZE / 2
        return (playerX, playerY, playerZ, 1.0)

    # End of Window utility functions

    def refreshStaticObjects(self):
        self.staticObjects = []
        if self.level is not None:
            levelObj = LevelSceneObject(self.level, TILESIZE)
            self.staticObjects.append(levelObj)
            # Load the static objects in vertex buffers
            self.loadVAOStaticObjects()

    def loadVAOStaticObjects(self):
        """
        Initializes the context of the VAO for static objects
        The level VAO contains the basic level mesh
        To optimize performance this will only be called when a new level is loaded
        """
        # Create vertex buffers on the GPU, remember the address IDs
        self.VBO_static_id = GL.glGenBuffers(1)
        self.VBO_static_elements_id = GL.glGenBuffers(1)

        # Construct the data arrays that will be loaded into the buffer
        vertexData = []
        colorData = []
        normalsData = []
        elementData = []

        elemOffset = 0
        for obj in self.staticObjects:
            vertexData.extend(obj.vertices)
            colorData.extend(obj.colors)
            normalsData.extend(obj.normals)
            for elem in obj.triangleIndices:
                 elementData.append(elem + elemOffset)
            elemOffset += obj.vertexCount

        # Merge the datasets into one buffer object
        # Remember where each data set begins
        self.VBO_static_color_offset = len(vertexData)
        vertexData.extend(colorData)
        self.VBO_static_normals_offset = len(vertexData)
        vertexData.extend(normalsData)
        self.VBO_static_length = len(vertexData)
        self.VBO_static_elements_length = len(elementData)

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_static)

        # Load the constructed vertex and color data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_static_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_static_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_static_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_static_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData),
                        GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def refreshDynamicObjects(self):
        self.dynamicObjects = []
        if self.level is not None:
            actorsObj = ActorsSceneObject(self.level, TILESIZE)
            self.dynamicObjects.append(actorsObj)
            # Load the dynamic objects in vertex buffers
            self.loadVAODynamicObjects()

    def loadVAODynamicObjects(self):
        """
        Initializes the context of the VAO for dynamic objects
        This should be called whenever there is a change in actor positions or visibility
        """
        # Create the vertex buffer on the GPU and remember the address ID
        self.VBO_dynamic_id = GL.glGenBuffers(1)
        self.VBO_dynamic_elements_id = GL.glGenBuffers(1)

        # Construct the data arrays that will be loaded into the buffer
        vertexData = []
        colorData = []
        normalsData = []
        elementData = []

        elemOffset = 0
        for obj in self.dynamicObjects:
            vertexData.extend(obj.vertices)
            colorData.extend(obj.colors)
            normalsData.extend(obj.normals)
            for elem in obj.triangleIndices:
                 elementData.append(elem + elemOffset)
            elemOffset += obj.vertexCount

        # Merge the datasets into one buffer object
        # Remember where each data set begins
        self.VBO_dynamic_color_offset = len(vertexData)
        vertexData.extend(colorData)
        self.VBO_dynamic_normals_offset = len(vertexData)
        vertexData.extend(normalsData)
        self.VBO_dynamic_length = len(vertexData)
        self.VBO_dynamic_elements_length = len(elementData)

        # Set up the VAO context
        GL.glUseProgram(self.openGlProgram)
        glBindVertexArray(self.VAO_dynamic)

        # Load the constructed vertex data array into the created array buffer
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO_dynamic_id)
        array_type = (GL.GLfloat * len(vertexData))
        GL.glBufferData(GL.GL_ARRAY_BUFFER, len(vertexData) * SIZE_OF_FLOAT, array_type(*vertexData), GL.GL_STATIC_DRAW)
        # Enable Vertex inputs and define pointer
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, None)
        # Enable Color inputs and define pointer
        GL.glEnableVertexAttribArray(1)
        colorDataStart = self.VBO_dynamic_color_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(1, VERTEX_COMPONENTS, GL.GL_FLOAT, False, 0, c_void_p(colorDataStart))
        # Enable Normals inputs and define pointer
        GL.glEnableVertexAttribArray(2)
        normalsDataStart = self.VBO_dynamic_normals_offset * SIZE_OF_FLOAT
        GL.glVertexAttribPointer(2, 3, GL.GL_FLOAT, False, 0, c_void_p(normalsDataStart))

        # Load the constructed element data array into the created element array buffer
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_dynamic_elements_id)
        array_type = (GL.GLint * len(elementData))
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, len(elementData) * SIZE_OF_FLOAT, array_type(*elementData),
                        GL.GL_STATIC_DRAW)

        # Done
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, 0)
        GL.glUseProgram(0)

    def drawAll(self):
        # set camera matrix based on current camera mode
        if self.cameraMode == CAM_MAP:
            self.setCameraCenterOnMap()
        elif self.cameraMode == CAM_ACTOR:
            self.setCameraCenterOnActor(self.game.player)
        elif self.cameraMode == CAM_FIRSTPERSON:
            self.setCameraFirstPersonView()
        elif self.cameraMode == CAM_ISOMETRIC:
            self.setCameraIsometricView()
        # draw HUD
        self.drawHUD()
        # draw Vector Buffer Arrays
        self.drawVBAs()

    def drawVBAs(self):
        DEBUG_GLSL = False
        if DEBUG_GLSL: print '\n\nDEBUG MODE: Simulating GLSL calculation:\n'

        GL.glUseProgram(self.openGlProgram)

        if len(self.staticObjects) > 0:
            # Bind VAO context for static objects
            glBindVertexArray(self.VAO_static)
            # Load uniforms
            GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix, (16)))
            if DEBUG_GLSL: print "perspectiveMatrix"
            if DEBUG_GLSL: print self.perspectiveMatrix

            #camMatrix = np.linalg.inv(self.cameraMatrix)
            GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.cameraMatrix, (16)))
            if DEBUG_GLSL: print "cameraMatrix"
            if DEBUG_GLSL: print self.cameraMatrix

            lightMatrix = self.cameraMatrix[:3, :3]  # Extracts 3*3 matrix out of 4*4
            if DEBUG_GLSL: print "LightMatrix"
            if DEBUG_GLSL: print lightMatrix
            GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix, (9)))

            if DEBUG_GLSL: print "Light position: " + self.lightPosition
            GL.glUniform3f(self.lightPosUnif, self.lightPosition[0], self.lightPosition[1], self.lightPosition[2])
            if DEBUG_GLSL: print "Light intensity: (0.8, 0.8, 0.8, 1.0)"
            GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
            if DEBUG_GLSL: print "Ambient intensity: (0.2, 0.2, 0.2, 1.0)"
            GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)

            GL.glUniform4f(self.playerPositionUnif, *self.getPlayerPosition())
            GL.glUniform1i(self.fogActiveUnif, 1 if self.fogActive else 0)

            # Bind element array
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_static_elements_id)
            # Draw elements
            GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_static_elements_length, GL.GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

        if len(self.dynamicObjects) > 0:
            # Bind VAO context for dynamic objects
            glBindVertexArray(self.VAO_dynamic)
            # Load uniforms
            GL.glUniformMatrix4fv(self.perspectiveMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.perspectiveMatrix, (16)))

            #camMatrix = np.linalg.inv(self.cameraMatrix)
            GL.glUniformMatrix4fv(self.cameraMatrixUnif, 1, GL.GL_FALSE, np.reshape(self.cameraMatrix, (16)))

            lightMatrix = self.cameraMatrix[:3, :3]  # Extracts 3*3 matrix out of 4*4
            GL.glUniformMatrix3fv(self.lightingMatrixUnif, 1, GL.GL_FALSE, np.reshape(lightMatrix, (9)))

            GL.glUniform3f(self.lightPosUnif, self.lightPosition[0], self.lightPosition[1], self.lightPosition[2])
            GL.glUniform4f(self.lightIntensityUnif, 0.8, 0.8, 0.8, 1.0)
            GL.glUniform4f(self.ambientIntensityUnif, 0.2, 0.2, 0.2, 1.0)
            GL.glUniform4f(self.playerPositionUnif, *self.getPlayerPosition())

            # Bind element array
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, self.VBO_dynamic_elements_id)
            # Draw elements
            GL.glDrawElements(GL.GL_TRIANGLES, self.VBO_dynamic_elements_length, GL.GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

            GL.glUseProgram(0)

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
        self.drawText((-0.98, 0.9, 0), self.level.name, 24, COLOR_PG_HUD_TEXT)

        # Player name
        GL.glLoadIdentity()
        self.drawText((-0.98, -0.85, 0), self.game.player.name + " (Lvl " + str(self.game.player.playerLevel) + ")", 18, COLOR_PG_HUD_TEXT)

        # Health Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98, -0.94, 0)
        current = self.game.player.currentHitPoints
        maximum = self.game.player.maxHitPoints
        barWidth = 0.46
        barHeight = 0.08
        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(*COLOR_GL_BAR_HEALTH_BG)
        # Draw vertices (counter clockwise for face culling!)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(0.0, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth / maximum
            GL.glBegin(GL.GL_QUADS)
            GL.glColor4f(*COLOR_GL_BAR_HEALTH)
            # Draw vertices (counter clockwise for face culling!)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(0.0, 0.0)
            GL.glEnd()

        # Xp Bar
        GL.glLoadIdentity()
        GL.glTranslatef(-0.98, -0.99, 0)
        current = self.game.player.xp
        maximum = self.game.player.nextLevelXp
        barWidth = 0.46
        barHeight = 0.04
        GL.glBegin(GL.GL_QUADS)
        GL.glColor4f(*COLOR_GL_BAR_XP_BG)
        # Draw vertices (counter clockwise for face culling!)
        GL.glVertex2f(barWidth, 0.0)
        GL.glVertex2f(barWidth, barHeight)
        GL.glVertex2f(0.0, barHeight)
        GL.glVertex2f(0.0, 0.0)
        GL.glEnd()
        if current > 0:
            filWidth = current * barWidth / maximum
            GL.glBegin(GL.GL_QUADS)
            GL.glColor4f(*COLOR_GL_BAR_XP)
            # Draw vertices (counter clockwise for face culling!)
            GL.glVertex2f(filWidth, 0.0)
            GL.glVertex2f(filWidth, barHeight)
            GL.glVertex2f(0.0, barHeight)
            GL.glVertex2f(0.0, 0.0)
            GL.glEnd()

        # FPS
        GL.glLoadIdentity()
        self.drawText((-0.98, -1, 0), str(self.FPS), 12, COLOR_PG_HUD_TEXT)

        # Right side: render game messages
        GL.glLoadIdentity()
        widthOffset = 200
        heightOffset = 100
        messageCounter = 1
        nbrOfMessages = len(self.game.messageBuffer)
        font = pygame.font.Font(None, 20)
        while heightOffset > 0:
            if messageCounter > nbrOfMessages: break
            # get messages from game message buffer, starting from the back
            message = self.game.messageBuffer[nbrOfMessages - messageCounter]
            #create textLines for message
            textLines = Utilities.wrap_multi_line(message, font, self.displayWidth - widthOffset)
            nbrOfLines = len(textLines)
            #blit the lines
            for l in range(1, nbrOfLines + 1):
                textSurface = font.render(textLines[nbrOfLines - l], 1, (191,191,191))
                heightOffset = heightOffset - 2 * textSurface.get_height()
                textData = pygame.image.tostring(textSurface, "RGBA", True)
                GL.glRasterPos3d(-0.5, -0.88 - (heightOffset / float(self.displayHeight)), 0)
                GL.glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL.GL_RGBA, GL.GL_UNSIGNED_BYTE,
                                textData)
            messageCounter += 1

    def progressGame(self):
        # Let the game move forward
        self.game.play()
        # Detect level change
        if self.level is not self.previousPassLevel:
            self.previousPassLevel = self.level
            # On level change we refresh the static objects
            self.refreshStaticObjects()
        # React to player death
        if self.game.player.state == Character.DEAD:
            self.setCameraCenterOnActor(self.game.player)

    def eventDraggingStart(self):
        self.cameraMode = CAM_FREE
        self._dragging = True
        # call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventDraggingStop(self):
        self._dragging = False

    def eventRotatingStart(self):
        self.cameraMode = CAM_FREE
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

            cameraTranslation = vec3(self.cameraMatrix[3, :3])
            mouseSensitivity = 1 / cameraTranslation.length()

            # Get the left right direction of the camera from the current camera matrix
            right = vec3(self.cameraMatrix[:3, 0])
            mouseFactor = mouseMove[0] * mouseSensitivity
            right_translate = og_util.translationMatrix44(right.x * mouseFactor, right.y * mouseFactor, right.z * mouseFactor)

            # Get the up down direction of the camera from the current camera matrix
            up = vec3(self.cameraMatrix[:3, 1])
            mouseFactor = -1 * mouseMove[1] * mouseSensitivity
            up_translate = og_util.translationMatrix44(up.x * mouseFactor, up.y * mouseFactor, up.z * mouseFactor)

            self.cameraMatrix = up_translate.dot(right_translate.dot(self.cameraMatrix))

        elif self._rotating:
            # get relative distance of mouse since last call to get_rel()
            mouseMove = pygame.mouse.get_rel()
            mouseSensitivity = 0.01
            mouseLeftRight = mouseMove[0] * mouseSensitivity
            mouseUpDown = mouseMove[1] * mouseSensitivity

            # Rotate the camera up-down: since the camera is fixed in OpenGl we need to rotate on the X axis
            X = vec3(1, 0, 0)
            rotationUpDown = og_util.rotationMatrix(mouseUpDown, X)

            # Rotate the camera left-right: since the camera is fixed in OpenGl we need to rotate on the Y axis
            Y = vec3(0, 1, 0)
            rotationLeftRight = og_util.rotationMatrix(mouseLeftRight, Y)

            # TODO: There is some rotation along the forward axis happening as well now and then :( Maybe better to work out the mouse movements using angle in xy, angle in xz and distance?
            # I guess it happens due to combined movements of x and y above.

            self.cameraMatrix = (self.cameraMatrix.dot(rotationLeftRight)).dot(rotationUpDown)

    def eventZoomIn(self):
        """
        Event handler for ZoomIn event.
        This will translate the camera matrix to zoom in.
        """
        self.cameraMode = CAM_FREE
        # Get the direction of the camera from the camera matrix
        heading = vec3(self.cameraMatrix[:3, 2])  # Forward
        # Translate the camera along this direction
        translation_matrix = og_util.translationMatrix44(heading.x, heading.y, heading.z)
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)

    def eventZoomOut(self):
        """
        Event handler for ZoomOut event.
        This will translate the camera matrix to zoom out.
        """
        self.cameraMode = CAM_FREE
        # Get the direction of the camera from the camera matrix
        heading = vec3(self.cameraMatrix[:3, 2] * -1)  # backward
        # Translate the camera along this direction
        translation_matrix = og_util.translationMatrix44(heading.x, heading.y, heading.z)
        self.cameraMatrix = translation_matrix.dot(self.cameraMatrix)