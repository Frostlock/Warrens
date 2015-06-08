__author__ = 'Frostlock'

import random

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import randomizeColor

class EffectSceneObject(SceneObject):

    @property
    def effect(self):
        return self._effect

    def __init__(self, effect, TILESIZE):
        super(EffectSceneObject, self).__init__()

        self._effect = effect
        self.TILESIZE = TILESIZE

        self.refreshMesh()

    def refreshMesh(self):
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []

        offset = 0
        TS = self.TILESIZE
        heights = {}

        def height(heights,key):
            if not key in heights.keys():
                heights[key] = (self.TILESIZE / 10 )* random.randint(1, 10)
            return heights[key]

        #TODO: don't recalculate completely, vary a base height map to make it more fluid

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
            self.vertices.extend((x * TS, y * TS, height(heights, (x, y)), 1.0))
            self.vertices.extend((x * TS, y * TS + TS, height(heights, (x, y+1)), 1.0))
            self.vertices.extend((x * TS + TS, y * TS + TS, height(heights, (x+1, y+1)), 1.0))
            self.vertices.extend((x * TS + TS, y * TS, height(heights, (x+1, y)), 1.0))

            # Store the vertex colors
            # 4 components per color: R, G, B, A, one color for every vertex
            color = randomizeColor(self.effect.effectColor, 50, 50, 50)

            # 4 vertices for the bottom
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            # 4 vertices for the top
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            self.colors.extend((color[0], color[1], color[2], 1.0))
            #TODO: transparency????

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