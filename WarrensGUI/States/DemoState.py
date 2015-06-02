__author__ = 'Frost'

import pygame

from WarrensGUI.States.State import State
from WarrensGUI.Util.Constants import *
from WarrensGUI.Util.vec3 import vec3
from WarrensGUI.Util import SceneObject

class DemoState(State):
    '''
    State to show some OpenGl demo objects
    '''

    def __init__(self, window, parentState=None):
        '''
        Constructor
        '''
        super(DemoState, self).__init__(window, parentState)

    def loopInit(self):
        # Put some scene objects to test
        self.window.dynamicObjects = []
        plantObj = SceneObject.PlantSceneObject(1.5)
        self.window.dynamicObjects.append(plantObj)

        self.window.staticObjects = []
        axisObj = SceneObject.AxisSceneObject(scale=10)
        cubeObj = SceneObject.Cube()
        self.window.staticObjects.append(axisObj)
        self.window.staticObjects.append(cubeObj)

        # Refresh the static objects meshes
        self.window.loadVAOStaticObjects()

        # Set the camera
        self.window.cameraMode = CAM_FREE
        eye = vec3(10,10,10)
        center = vec3(0,0,0)
        up = vec3(0,0,1)
        self.window.lookAt(eye, center, up)

    def loopDraw(self):
        # Refresh the dynamic meshes
        self.window.loadVAODynamicObjects()

        # Render the 3D view (Vertex Array Buffers
        self.window.drawVBAs()

    def loopEvents(self):
        # handle pygame (GUI) events
        events = pygame.event.get()
        for event in events:
            self.handlePyGameEvent(event)
            # keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    #Grow
                    for obj in self.window.dynamicObjects:
                        if hasattr(obj,"grow"):
                        #if isinstance(obj, SceneObject.PlantSceneObject):
                            obj.grow()
                # Leave state / Close
                elif event.key == pygame.K_ESCAPE:
                    self.close()
