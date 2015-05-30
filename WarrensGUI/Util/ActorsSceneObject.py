__author__ = 'pi'

from WarrensGUI.Util.SceneObject import SceneObject
from WarrensGUI.Util.OpenGlUtilities import normalizeColor

from WarrensGame.Actors import *

class ActorsSceneObject(SceneObject):

    def __init__(self, level, TILESIZE):
        super(ActorsSceneObject, self).__init__()

        elemOffset = 0
        for vTile in level.map.visible_tiles:
            for actor in vTile.actors:
                tile = actor.tile

                # Determine scale
                if isinstance(actor, Player):
                    scale = 0.9
                elif isinstance(actor, Portal):
                    scale = 0.8
                elif isinstance(actor, Monster):
                    scale = 0.7
                elif isinstance(actor, Item):
                    scale = 0.4
                else:
                    scale = 0.2

                # Determine height
                offset = ((1 - scale) / 2) * TILESIZE
                assert isinstance(actor, Actor)
                if actor.currentHitPoints > 0:
                    height = TILESIZE - (2 * offset)
                else:
                    height = 0.05

                # Store the vertex coordinates: 4 components per vertex: x, y, z, w
                self._vertices.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + offset, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + TILESIZE - offset, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + TILESIZE - offset, tile.y * TILESIZE + offset, 0.0, 1.0))
                self._vertices.extend((tile.x * TILESIZE + (TILESIZE / 2), tile.y * TILESIZE + (TILESIZE / 2), height, 1.0))

                # Store the vertex color: 4 components per color: R, G, B, A
                color = normalizeColor(actor.color)
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))
                self._colors.extend((color[0], color[1], color[2], 1.0))

                # Store the vertex normals: 3 components per normal: x, y, z
                self._normals.extend((-1.0, 1.0, -0.2))
                self._normals.extend((1.0, 1.0, -0.2))
                self._normals.extend((1.0, -1.0, -0.2))
                self._normals.extend((-1.0, -1.0, -0.2))
                self._normals.extend((0.0, 0.0, -1.0))

                # Store the indices for the element drawing (triangles, clockwise from front)
                self._triangleIndices.extend((0 + elemOffset, 1 + elemOffset, 2 + elemOffset))
                self._triangleIndices.extend((0 + elemOffset, 2 + elemOffset, 3 + elemOffset))
                self._triangleIndices.extend((0 + elemOffset, 3 + elemOffset, 4 + elemOffset))
                self._triangleIndices.extend((3 + elemOffset, 2 + elemOffset, 4 + elemOffset))
                self._triangleIndices.extend((2 + elemOffset, 1 + elemOffset, 4 + elemOffset))
                self._triangleIndices.extend((1 + elemOffset, 0 + elemOffset, 4 + elemOffset))
                elemOffset += 5 # 5 vertices per actor so offset is 5