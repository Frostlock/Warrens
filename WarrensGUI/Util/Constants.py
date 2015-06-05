__author__ = 'pi'

import pygame
# This module contains a number of shared constants used by the GUI

DISPLAY_SIZE = (800, 600)

# TileSize in OpenGl space
TILESIZE = 0.25

# 4 bytes in a python float, we need to make this explicit while passing values to OpenGl
# TODO: Find a better way to deal with this
SIZE_OF_FLOAT = 4

# 4 components in a vector: X, Y, Z, W
VERTEX_COMPONENTS = 4

# Camera modes
CAM_MAP = 0
CAM_ACTOR = 1
CAM_ISOMETRIC = 2
CAM_FIRSTPERSON = 3
CAM_FREE = 4

# Fonts
# Ensure pygame is initialized (According to the pygame doc it is fine to call this multiple times)
pygame.init()
FONT_HUD_XXL = pygame.font.Font(None, 24)
FONT_HUD_XL = pygame.font.Font(None, 20)
FONT_HUD_L = pygame.font.Font(None, 18)
FONT_HUD_M = pygame.font.Font(None, 14)
FONT_HUD_S = pygame.font.Font(None, 12)

##########
# COLORS #
######################################################################
# The following constants define the GUI color scheme                #
# The GUI requires two different color formats.                      #
#   - RGBA for opengl -> Normalized format (values between 0 and 1)  #
#   - RGBA for pygame -> 255 based format (values between 0 and 255) #
######################################################################

# Colors used by PyGame
COLOR_PG_HUD_TEXT = (255, 255, 255, 255)
COLOR_PG_HUD_TEXT_SELECTED = (250, 125, 0, 255)

# Colors used by OpenGl
COLOR_GL_BAR_HEALTH = (0.6, 0, 0, 1)
COLOR_GL_BAR_HEALTH_BG = (0.1, 0, 0, 1)
COLOR_GL_BAR_XP = (0, 0.6, 0, 1)
COLOR_GL_BAR_XP_BG = (0, 0.1, 0, 1)
COLOR_GL_MENU_BG = (0.01, 0.01, 0.01, 0.85)