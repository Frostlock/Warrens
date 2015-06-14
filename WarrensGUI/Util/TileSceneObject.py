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

    @property
    def height(self):
        if self.tile.blocked:
            return TILESIZE
        elif self.selected:
            return TILESIZE
        else:
            return 0.0
        
    @property
    def color(self):
        if self.selected:
            return COLOR_GL_SELECTED_TRANSPARANT
        else:
            color = randomizeColor(self.tile.color, (10, 10, 10))
            return (color[0], color[1], color[2], 1.0)

    def __init__(self, tile):
        super(TileSceneObject, self).__init__()

        self._tile = tile
        tile.sceneObject = self

        #TODO: Unexplored tiles should not have any vertices. Easy to implement here but since all tiles are static objects they will not get rendered properly.
        # Some ideas for review:
        #   Add sceneobjects for gameobjects as these are encountered.
        #   Add them first to dynamic objects
        #   Move sceneobjects that go out of sight to static
        #   Move tileSceneObjects that are empty to static
        # Alternatively
        #   Update only specific sections of the static buffer
        #   Would need to use https://www.opengl.org/sdk/docs/man3/xhtml/glBufferSubData.xml
        # Alternatively
        #   Create more buffer objects (one per sceneObject is probably too many), only update changed buffer objects
        self.refreshMesh()

    def refreshMesh(self):
        x = self.tile.x
        y = self.tile.y
        self._vertices = []
        self._colors = []
        self._normals = []
        self._triangleIndices = []

        # Store the vertex coordinates
        # 4 components per vertex: x, y, z, w
        # 4 vertices: bottom of the rectangular tile area
        self.vertices.extend((x * TILESIZE, y * TILESIZE, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE, y * TILESIZE + TILESIZE, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE, y * TILESIZE + TILESIZE, 0.0, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE, y * TILESIZE, 0.0, 1.0))
        # 4 vertices: top of the rectangular tile area
        self.vertices.extend((x * TILESIZE, y * TILESIZE, self.height, 1.0))
        self.vertices.extend((x * TILESIZE, y * TILESIZE + TILESIZE, self.height, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE, y * TILESIZE + TILESIZE, self.height, 1.0))
        self.vertices.extend((x * TILESIZE + TILESIZE, y * TILESIZE, self.height, 1.0))

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
        super(TileSceneObject,self).animate(timePassed)

        if self.timeSinceLastAnimation > 300:
            # Reset timer
            self.timeSinceLastAnimation = 0
            # Refresh mesh
            self.refreshMesh()

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
