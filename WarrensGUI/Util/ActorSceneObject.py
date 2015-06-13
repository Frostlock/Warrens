__author__ = 'pi'

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import normalizeColor
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

    @property
    def effectColor(self):
        '''
        The effect color used for this ActorSceneObject.
        :return: GL Color tuple or None
        '''
        return self._effectColor

    @property
    def color(self):
        if self.selected:
            return COLOR_GL_SELECTED
        elif self.effectColor is None:
            return self.baseColor
        else:
            R,G,B,A = self.baseColor
            r,g,b = self._colorStep
            s= self._currentAnimationStep
            return (R + s * r, G + s * g, B + s *b, A)

    @property
    def effect(self):
        '''
        Effect currently active on this ActorSceneObject
        :return: Effect object or None
        '''
        return self._effect

    STEPS = 20

    @effect.setter
    def effect(self, effect):
        self._effect = effect
        r,g,b = normalizeColor(getElementColor(effect.effectElement))
        self._effectColor = (r, g, b, 1.0)
        R,G,B,A = self.baseColor
        self._colorStep = ((r-R)/self.STEPS,(g-G)/self.STEPS,(b-B)/self.STEPS)
        self.refreshMesh()

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
        self._baseColor = (r, g, b, 1.0)
        self._effect = None
        self._effectColor = None
        self._currentAnimationStep = 0
        self._animationStepModifier = 1
        self.refreshMesh()

    def refreshMesh(self):
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []

        tile = self.actor.tile

        # Determine scale
        if isinstance(self.actor, Player):
            scale = 0.9
        elif isinstance(self.actor, Portal):
            scale = 0.8
        elif isinstance(self.actor, Monster):
            scale = 0.7
        elif isinstance(self.actor, Item):
            scale = 0.4
        else:
            raise NotImplementedError("Unknown actor type")
        # Offset within the tile area
        offset = ((1 - scale) / 2) * TILESIZE

        # Determine height
        if self.actor.currentHitPoints > 0:
            height = TILESIZE - (2 * offset)
        else:
            height = 0.05

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