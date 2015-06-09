__author__ = 'Frostlock'

import random

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import randomizeColor
from WarrensGUI.Util.Utilities import *
from WarrensGUI.Util.Constants import TILESIZE

class EffectSceneObject(SceneObject):

    @property
    def effect(self):
        return self._effect

    @property
    def heightMap(self):
        '''
        Height of the top vertices. This allows to set the height based on the x & y coordinates of the vertex.
        This ensures that adjacent corners of tiles end up on the same height.
        :return: Dictionary with (x,y) keys
        '''
        return self._heightMap

    def height(self, key):
        if not key in self.heightMap.keys():
            self.heightMap[key] = self.minHeight + (self.maxHeight - self.minHeight)*random.randint(1, 10)/10
        return self.heightMap[key]

    def updateHeightMap(self, variance):
        for key in self.heightMap.keys():
            self.heightMap[key] += random.choice([-variance/2,variance/2])
            self.heightMap[key] = clamp(self.heightMap[key],self.minHeight, self.maxHeight)

    @property
    def baseColor(self):
        return self._baseColor

    @property
    def colorVariance(self):
        return self._colorVariance

    @property
    def alpha(self):
        return self._alpha

    @property
    def minHeight(self):
        return self._minHeight

    @property
    def maxHeight(self):
        return self._maxHeight

    @property
    def colorMap(self):
        '''
        Color of the top vertices. This allows to set the color based on the x & y coordinates of the vertex.
        This ensures that adjacent corners of tiles end up with same color.
        :return: Dictionary with (x,y) keys
        '''
        return self._colorMap

    def color(self, key):
        if not key in self.colorMap.keys():
            self.colorMap[key] = randomizeColor(self.baseColor, self.colorVariance)
        return self.colorMap[key]

    def updateColorMap(self):
        for key in self.colorMap.keys():
            self.colorMap[key] = randomizeColor(self.baseColor, self.colorVariance)

    def __init__(self, effect):
        super(EffectSceneObject, self).__init__()

        self._effect = effect
        self._heightMap = {}
        self._baseColor = getElementColor(effect.effectElement)
        self._colorVariance = getElementColorVariance(effect.effectElement)
        self._maxHeight = getElementMaxHeight(effect.effectElement)
        self._minHeight = getElementMinHeight(effect.effectElement)
        self._colorMap = {}

        #TODO: set alpha per element type
        self._alpha = 0.5

        self.refreshMesh()

    def refreshMesh(self):
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []
        offset = 0
        TS = TILESIZE

        # Create fluctuation in the heightmap
        variance = 0.1
        self.updateHeightMap(variance)
        self.updateColorMap()

        for tile in self.effect.tiles:
            x = tile.x
            y = tile.y
            
            # Store the vertex coordinates
            # 4 components per vertex: x, y, z, w
            # 4 vertices: bottom of the rectangular tile area
            self.vertices.extend((x * TS, y * TS, 0.0, 1.0))
            self.vertices.extend((x * TS, y * TS + TS, 0.0, 1.0))
            self.vertices.extend((x * TS + TS, y * TS + TS, 0.0, 1.0))
            self.vertices.extend((x * TS + TS, y * TS, 0.0, 1.0))
            # 4 vertices: top of the rectangular tile area
            self.vertices.extend((x * TS, y * TS, self.height((x, y)), 1.0))
            self.vertices.extend((x * TS, y * TS + TS, self.height((x, y+1)), 1.0))
            self.vertices.extend((x * TS + TS, y * TS + TS, self.height((x+1, y+1)), 1.0))
            self.vertices.extend((x * TS + TS, y * TS, self.height((x+1, y)), 1.0))

            # Store the vertex colors
            # 4 components per color: R, G, B, A, one color for every vertex
            # 4 vertices for the bottom
            color = self.color((x,y))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            color = self.color((x,y+1))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            color = self.color((x+1,y+1))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            color = self.color((x+1,y))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            # 4 vertices for the top
            color = self.color((x,y))
            self.colors.extend((color[0], color[1], color[2], self.alpha))
            color = self.color((x,y+1))
            self.colors.extend((color[0], color[1], color[2], self.alpha))
            color = self.color((x+1,y+1))
            self.colors.extend((color[0], color[1], color[2], self.alpha))
            color = self.color((x+1,y))
            self.colors.extend((color[0], color[1], color[2], self.alpha))

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
            self.triangleIndices.extend((0 + offset, 1 + offset, 2 + offset))
            self.triangleIndices.extend((0 + offset, 2 + offset, 3 + offset))
            self.triangleIndices.extend((0 + offset, 7 + offset, 4 + offset))
            self.triangleIndices.extend((0 + offset, 3 + offset, 7 + offset))
            self.triangleIndices.extend((3 + offset, 6 + offset, 7 + offset))
            self.triangleIndices.extend((3 + offset, 2 + offset, 6 + offset))
            self.triangleIndices.extend((2 + offset, 5 + offset, 6 + offset))
            self.triangleIndices.extend((2 + offset, 1 + offset, 5 + offset))
            self.triangleIndices.extend((1 + offset, 4 + offset, 5 + offset))
            self.triangleIndices.extend((1 + offset, 0 + offset, 4 + offset))
            self.triangleIndices.extend((4 + offset, 6 + offset, 5 + offset))
            self.triangleIndices.extend((4 + offset, 7 + offset, 6 + offset))
            offset += 8 # 8 vertices for every tile +8 to set the elementData for the next tile

    def animate(self, timePassed):
        super(EffectSceneObject,self).animate(timePassed)

        if self.timeSinceLastAnimation > 200:
            # Reset timer
            self.timeSinceLastAnimation = 0

            # Refresh the mesh
            self.refreshMesh()