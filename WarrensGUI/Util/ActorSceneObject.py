__author__ = 'pi'

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import normalizeColor, randomizeColor
from WarrensGUI.Util.Utilities import getElementColor
from WarrensGUI.Util.Constants import *

from WarrensGame.Actors import *

class ActorSceneObject(SceneObject):

    @property
    def mainVertex(self):
        '''
        The main vertex for this SceneObject.
        The main vertex can be used as a single vertex representation of the object.
        :return:
        '''
        return self._mainVertex

    @property
    def actor(self):
        '''
        The Actor for which this ActorSceneObject was created.
        :return: Actor
        '''
        return self._actor

    @property
    def baseColor(self):
        '''
        The base color used for this ActorSceneObject.
        :return: GL Color tuple or None
        '''
        return self._baseColor


    STEPS = 20

    @property
    def effectColor(self):
        '''
        The effect color used for this ActorSceneObject.
        :return: GL Color tuple or None
        '''
        return self._effectColor

    @effectColor.setter
    def effectColor(self,rgbColor):
        self._effectColor = rgbColor
        r,g,b = rgbColor
        R,G,B = self.baseColor
        self._colorStep = ((r-R)/self.STEPS,(g-G)/self.STEPS,(b-B)/self.STEPS)
        self.refreshMesh()

    @property
    def color(self):
        if self.selected:
            R,G,B,A = COLOR_GL_SELECTED
            return (R, G, B, self.alpha)
        elif self.effectColor is None:
            R,G,B = self.baseColor
            return (R, G, B, self.alpha)
        else:
            R,G,B = self.baseColor
            r,g,b = self._colorStep
            s= self._currentAnimationStep
            return (R + s * r, G + s * g, B + s *b, self.alpha)

    @property
    def effect(self):
        '''
        Effect currently active on this ActorSceneObject
        :return: Effect object or None
        '''
        return self._effect

    @effect.setter
    def effect(self, effect):
        self._effect = effect
        r,g,b = normalizeColor(getElementColor(effect.effectElement))
        self.effectColor = (r, g, b)

    def __init__(self, actor):
        '''
        Constructor
        :param actor: Actor object for which an ActorSceneObject is generated
        :return:
        '''
        super(ActorSceneObject, self).__init__()

        self._actor = actor
        self.actor.sceneObject = self
        r,g,b = normalizeColor(actor.color)
        self._baseColor = (r, g, b)
        self._effect = None
        self._effectColor = None
        self._currentAnimationStep = 0
        self._animationStepModifier = 1

        # Determine scale
        if isinstance(self.actor, Player):
            self.refreshMesh = self.generatePyramidMesh
            self.scale = 0.9
        elif isinstance(self.actor, Portal):
            self.refreshMesh = self.generateCubeMesh
            self.scale = 0.95
            self.alpha = 0.5
            variance = (100,10,10)
            self.effectColor = randomizeColor(actor.color, variance)
        elif isinstance(self.actor, Monster):
            self.refreshMesh = generatePyramidMesh
            self.scale = 0.7
        elif isinstance(self.actor, Item):
            self.refreshMesh = self.generateCubeMesh
            self.scale = 0.3
        elif isinstance(self.actor, Container):
            self.refreshMesh = self.generateCubeMesh
            self.scale = 0.6
        else:
            raise NotImplementedError("Unknown actor type")

        self.refreshMesh()

    def generatePyramidMesh(self):
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []

        tile = self.actor.tile

        # Offset within the tile area
        offset = ((1 - self.scale) / 2) * TILESIZE

        # Determine height
        if isinstance(self.actor, Character):
            if self.actor.currentHitPoints > 0:
                height = TILESIZE - (2 * offset)
            else:
                height = 0.05
        else:
            height = TILESIZE - (2 * offset)

        # Store the vertex coordinates: 4 components per vertex: x, y, z, w
        self.vertices.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + offset, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + offset, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + (TILESIZE / 2), tile.y * TILESIZE + (TILESIZE / 2), height, 1.0))

        # Select one vertex as mainVertex
        self._mainVertex = (tile.x * TILESIZE + (TILESIZE / 2), tile.y * TILESIZE + (TILESIZE / 2), height, 1.0)

        # Store the vertex color
        color = self.color
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)

        # Store the vertex normals: 3 components per normal: x, y, z
        self.normals.extend((-1.0, 1.0, -0.2))
        self.normals.extend((1.0, 1.0, -0.2))
        self.normals.extend((1.0, -1.0, -0.2))
        self.normals.extend((-1.0, -1.0, -0.2))
        self.normals.extend((0.0, 0.0, -1.0))

        # Store the indices for the element drawing (triangles, clockwise from front)
        self.triangleIndices.extend((0, 1, 2))
        self.triangleIndices.extend((0, 2, 3))
        self.triangleIndices.extend((0, 3, 4))
        self.triangleIndices.extend((3, 2, 4))
        self.triangleIndices.extend((2, 1, 4))
        self.triangleIndices.extend((1, 0, 4))

    def generateCubeMesh(self):
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []

        x = self.actor.tile.x
        y = self.actor.tile.y

        # Offset within the tile area
        offset = ((1 - self.scale) / 2) * TILESIZE

        # Determine height based on scale
        height = TILESIZE - 2 * offset

        # Select one vertex as mainVertex
        self._mainVertex = (x * TILESIZE + (TILESIZE / 2), y * TILESIZE + (TILESIZE / 2), height, 1.0)

        # Store the vertex coordinates
        # 4 components per vertex: x, y, z, w
        # 4 vertices: bottom of the rectangular tile area
        self.vertices.extend((x * TILESIZE + offset, y * TILESIZE + offset, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE + offset, y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE - offset, y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE - offset, y * TILESIZE + offset, 0.0, 1.0))
        # 4 vertices: top of the rectangular tile area
        self.vertices.extend((x * TILESIZE + offset, y * TILESIZE + offset, height, 1.0))
        self.vertices.extend((x * TILESIZE + offset, y * TILESIZE + TILESIZE - offset, height, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE - offset, y * TILESIZE + TILESIZE - offset, height, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE - offset, y * TILESIZE + offset, height, 1.0))

        # Store the vertex colors
        # 4 components per color: R, G, B, A, one color for every vertex
        color = self.color
        # 4 vertices for the bottom
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)
        # 4 vertices for the top
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)
        self.colors.extend(color)

        # Store the vertex normals
        # 3 components per normal: x, y, z
        # 4 vertex normals for the bottom
        self.normals.extend((-1.0, -1.0, -0.01))
        self.normals.extend((1.0, -1.0, -0.01))
        self.normals.extend((1.0, 1.0, -0.01))
        self.normals.extend((-1.0, 1.0, -0.01))
        # 4 vertex normals for the top
        self.normals.extend((-1.0, -1.0, -1.0))
        self.normals.extend((1.0, -1.0, -1.0))
        self.normals.extend((1.0, 1.0, -1.0))
        self.normals.extend((-1.0, 1.0, -1.0))

        # Create the element array (counter clockwise triangles for every face)
        # 12 Triangles for a complete block
        self.triangleIndices.extend((0, 1, 2))
        self.triangleIndices.extend((0, 2, 3))
        self.triangleIndices.extend((0, 7, 4))
        self.triangleIndices.extend((0, 3, 7))
        self.triangleIndices.extend((3, 6, 7))
        self.triangleIndices.extend((3, 2, 6))
        self.triangleIndices.extend((2, 5, 6))
        self.triangleIndices.extend((2, 1, 5))
        self.triangleIndices.extend((1, 4, 5))
        self.triangleIndices.extend((1, 0, 4))
        self.triangleIndices.extend((4, 6, 5))
        self.triangleIndices.extend((4, 7, 6))

    def animate(self, timePassed):
        super(ActorSceneObject,self).animate(timePassed)

        if self.timeSinceLastAnimation > 50:
            # Reset timer
            self.timeSinceLastAnimation = 0
            self._currentAnimationStep += self._animationStepModifier

            # Refresh the mesh
            self.refreshMesh()

            if self._currentAnimationStep == self.STEPS : self._animationStepModifier = -1
            if self._currentAnimationStep == 0 : self._animationStepModifier = 1