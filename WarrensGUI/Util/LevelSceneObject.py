__author__ = 'pi'

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import normalizeColor

class LevelSceneObject(SceneObject):

    def __init__(self, level, TILESIZE):
        super(LevelSceneObject, self).__init__()

        # Store the vertex coordinates
        for tileRow in level.map.tiles:
            for tile in tileRow:
                if tile.blocked:
                    height = TILESIZE
                else:
                    height = 0.0
                # 4 components per vertex: x, y, z, w
                # 4 vertices: bottom of the rectangular tile area
                self._vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, 0.0, 1.0))
                # 4 vertices: top of the rectangular tile area
                self._vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE, height, 1.0))
                self._vertices.extend((tile.x * TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE + TILESIZE, height, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE, tile.y * TILESIZE, height, 1.0))

        # Store the vertex colors
        for tileRow in level.map.tiles:
            for tile in tileRow:
                # 4 components per color: R, G, B, A, one color for every vertex
                color = normalizeColor(tile.color)
                # 4 vertices for the bottom
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                # 4 vertices for the top
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))

        # Store the vertex normals
        for tileRow in level.map.tiles:
            for tile in tileRow:
                # 3 components per normal: x, y, z
                # 4 vertex normals for the bottom
                self._normals.extend((-1.0, -1.0, -0.01))
                self._normals.extend((1.0, -1.0, -0.01))
                self._normals.extend((1.0, 1.0, -0.01))
                self._normals.extend((-1.0, 1.0, -0.01))
                # 4 vertex normals for the top
                self._normals.extend((-1.0, -1.0, -1.0))
                self._normals.extend((1.0, -1.0, -1.0))
                self._normals.extend((1.0, 1.0, -1.0))
                self._normals.extend((-1.0, 1.0, -1.0))

        # Create the element array (counter clockwise triangles for every face)
        offset = 0
        for tileRow in level.map.tiles:
            for tile in tileRow:
                # 12 Triangles for a complete block
                self._triangleIndices.extend((0 + offset, 1 + offset, 2 + offset))
                self._triangleIndices.extend((0 + offset, 2 + offset, 3 + offset))
                self._triangleIndices.extend((0 + offset, 7 + offset, 4 + offset))
                self._triangleIndices.extend((0 + offset, 3 + offset, 7 + offset))
                self._triangleIndices.extend((3 + offset, 6 + offset, 7 + offset))
                self._triangleIndices.extend((3 + offset, 2 + offset, 6 + offset))
                self._triangleIndices.extend((2 + offset, 5 + offset, 6 + offset))
                self._triangleIndices.extend((2 + offset, 1 + offset, 5 + offset))
                self._triangleIndices.extend((1 + offset, 4 + offset, 5 + offset))
                self._triangleIndices.extend((1 + offset, 0 + offset, 4 + offset))
                self._triangleIndices.extend((4 + offset, 6 + offset, 5 + offset))
                self._triangleIndices.extend((4 + offset, 7 + offset, 6 + offset))
                offset += 8 # 8 vertices for every tile +8 to set the elementData for the next tile