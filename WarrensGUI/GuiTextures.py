'''
Created on Mar 24, 2014

@author: pi
'''

"""
TODO: In case we pull out all the texture related code this module can be discarded.
"""

import pygame
from WarrensGame.Maps import TileType

textureImage = None
textureRects = {}
 
def initTextures(texture=None,tileSize=32):
    global textureImage, textureRects
    if texture is None: texture = "./textures/default.png"
    textureImage = pygame.image.load(texture).convert_alpha()
    tectureRects = {}
    print 'Initializing textures ' + texture
    #EMPTY
    rect = pygame.Rect(0,0,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.EMPTY]= subsurf
    
    #FULL
    rect = pygame.Rect(32,96,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.FULL]= subsurf

    #INNER_NW
    rect = pygame.Rect(32,0,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.INNER_NW]= subsurf
 
    #INNER_NE
    rect = pygame.Rect(64,0,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.INNER_NE]= subsurf
    
    #INNER_SW
    rect = pygame.Rect(32,32,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.INNER_SW]= subsurf
    
    #INNER_SE
    rect = pygame.Rect(64,32,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.INNER_SE]= subsurf

    #OUTER_N
    rect = pygame.Rect(32,64,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_N]= subsurf
    
    #OUTER_NW
    rect = pygame.Rect(0,64,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_NW]= subsurf
    
    #OUTER_NE
    rect = pygame.Rect(64,64,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_NE]= subsurf
    
    #OUTER_S
    rect = pygame.Rect(32,128,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_S]= subsurf
    
    #OUTER_SW
    rect = pygame.Rect(0,128,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_SW]= subsurf
    
    #OUTER_SE
    rect = pygame.Rect(64,128,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_SE]= subsurf
    
    #OUTER_W
    rect = pygame.Rect(0,96,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_W]= subsurf
    
    #OUTER_E
    rect = pygame.Rect(64,96,32,32)
    subsurf = textureImage.subsurface(rect)
    if tileSize <> 32:
        subsurf = pygame.transform.smoothscale(subsurf, (tileSize, tileSize))
    textureRects[TileType.OUTER_E]= subsurf
    
def getTextureSurface(key):
    global textureRects
    return textureRects[key]

if __name__ == '__main__':
    #Texture testing code
    import sys
    
    pygame.init()
    window = pygame.display.set_mode((300, 300))

    
    
    initTextures('./textures/town.png',64)
    tex = getTextureSurface(TileType.FULL)
        
    
    #background = pygame.Surface((window.get_size()))
    window.fill((255, 255, 255))
    image = image2 = pygame.image.load('./media/terrain.png').convert_alpha()
    
    #image = image.convert()
    rect = image.get_rect()
    
    #image2 = image2.convert_alpha()
    image2 = image
    rect2 = image2.get_rect()
    
    rect2.left = rect.width + 1
    
    i = 0
    while True:
      for event in pygame.event.get():
        if event.type == 12:
          pygame.quit()
          sys.exit()
    
      image.set_alpha(i)
      image2.set_alpha(i)
    
      window.fill((255, 0, 0))
      #window.blit(background, background.get_rect())
      window.blit(image, rect)
      #window.blit(image2, rect2)
      window.blit(tex, (10,10))
    
      if i == 255:
        i = 0
      else:
        i += 1
    
      pygame.display.update()
      pygame.time.Clock().tick(60)