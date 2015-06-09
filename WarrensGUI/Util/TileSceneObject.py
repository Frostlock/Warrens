__author__ = 'pi'

import random

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import randomizeColor
from WarrensGUI.Util.Constants import *

from WarrensGame.Maps import MaterialType

class TileSceneObject(SceneObject):

    @property
    def tile(self):
        return self._tile

    def __init__(self, tile):
        super(TileSceneObject, self).__init__()

        self._tile = tile

        # Store the vertex coordinates
        offset = 0
        if tile.blocked:
            height = TILESIZE
        else:
            height = 0.0
        # 4 components per vertex: x, y, z, w
        # 4 vertices: bottom of the rectangular tile area
        self.vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
        # 4 vertices: top of the rectangular tile area
        self.vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE, height, 1.0))
        self.vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
        self.vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, height, 1.0))

        # Store the vertex colors
        # 4 components per color: R, G, B, A, one color for every vertex
        color = randomizeColor(self.tile.color, (10, 10, 10))

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
        super(TileSceneObject,self).animate(timePassed)

        if self.timeSinceLastAnimation > 300:
            # Reset timer
            self.timeSinceLastAnimation = 0
            # Animate water
            if self.tile.material == MaterialType.WATER :
                # Refresh the vertex colors
                # 4 components per color: R, G, B, A, one color for every vertex
                self._colors = []

                color = randomizeColor(self.tile.color, (50, 50, 150))
                # 4 vertices for the bottom
                self.colors.extend((color[0], color[1], color[2], 1.0))
                self.colors.extend((color[0], color[1], color[2], 1.0))
                self.colors.extend((color[0], color[1], color[2], 1.0))
                self.colors.extend((color[0], color[1], color[2], 1.0))
                # 4 vertices for the top
                self.colors.extend((color[0], color[1], color[2], 1.0))
                color = randomizeColor(self.tile.color, (50, 50, 150))
                self.colors.extend((color[0], color[1], color[2], 1.0))
                color = randomizeColor(self.tile.color, (50, 50, 150))
                self.colors.extend((color[0], color[1], color[2], 1.0))
                color = randomizeColor(self.tile.color, (50, 50, 150))
                self.colors.extend((color[0], color[1], color[2], 1.0))
