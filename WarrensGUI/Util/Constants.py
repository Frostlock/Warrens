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
CAM_FOLLOW = 4
CAM_FREE = 5
CAM_LAST = 6 # Leave this one last, used to detect last mode when cycling cameramodes

CAM_MINIMUM_DISTANCE = 0.4
CAM_MAXIMUM_DISTANCE = 5.0
SAVE_FILE = "save.warrens"

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
COLOR_GL_BAR_HEALTH = (0.6, 0.0, 0.0, 1.0)
COLOR_GL_BAR_HEALTH_BG = (0.1, 0.0, 0.0, 1.0)
COLOR_GL_BAR_XP = (0, 0.6, 0, 1)
COLOR_GL_BAR_XP_BG = (0, 0.1, 0, 1)
COLOR_GL_MENU_BG = (0.01, 0.01, 0.01, 0.85)
COLOR_GL_SELECTED = (1.0, 0.5, 0.0, 1.0)
COLOR_GL_SELECTED_TRANSPARANT = (1.0, 0.5, 0.0, 0.5)

# Colors
COLOR_RGB_HEAL = (220,10,10)
COLOR_VAR_HEAL = (20, 2, 2)
COLOR_RGB_WATER = (30,144,255)
COLOR_VAR_WATER = (50,50,150)
COLOR_RGB_AIR = (130,204,255)
COLOR_VAR_AIR = (10,100,10)
COLOR_RGB_FIRE = (240,83,50)
COLOR_VAR_FIRE = (45, 45, 45)
COLOR_RGB_EARTH = (95,60,50)
COLOR_VAR_EARTH = (10, 10, 10)
COLOR_RGB_ELEC = (140,170,205)
COLOR_VAR_ELEC = (45,45,100)
COLOR_RGB_MIND = (50,185,250)
COLOR_VAR_MIND = (25,25,25)

################
# PYGAME FONTS #
################

# Ensure pygame is initialized (According to the pygame doc it is fine to call this multiple times)
pygame.init()

# Attention: FONT HEIGHTS are in pixels!

FONT_HUD_XXL = pygame.font.Font(None, 24)
FONT_HUD_XXL_HEIGHT = (FONT_HUD_XXL.render("Dummy", 1, COLOR_PG_HUD_TEXT)).get_height()
FONT_HUD_XL = pygame.font.Font(None, 20)
FONT_HUD_XL_HEIGHT = (FONT_HUD_XL.render("Dummy", 1, COLOR_PG_HUD_TEXT)).get_height()
FONT_HUD_L = pygame.font.Font(None, 18)
FONT_HUD_L_HEIGHT = (FONT_HUD_L.render("Dummy", 1, COLOR_PG_HUD_TEXT)).get_height()
FONT_HUD_M = pygame.font.Font(None, 16)
FONT_HUD_M_HEIGHT = (FONT_HUD_M.render("Dummy", 1, COLOR_PG_HUD_TEXT)).get_height()
FONT_HUD_S = pygame.font.Font(None, 12)
FONT_HUD_S_HEIGHT = (FONT_HUD_S.render("Dummy", 1, COLOR_PG_HUD_TEXT)).get_height()


# Movement keys
MOVEMENT_KEYS = {
    pygame.K_h: (-1, +0),  # vi keys
    pygame.K_l: (+1, +0),
    pygame.K_j: (+0, -1),
    pygame.K_k: (+0, +1),
    pygame.K_y: (-1, +1),
    pygame.K_u: (+1, +1),
    pygame.K_b: (-1, -1),
    pygame.K_n: (+1, -1),
    pygame.K_KP4: (-1, +0),  # numerical keypad
    pygame.K_KP6: (+1, +0),
    pygame.K_KP2: (+0, -1),
    pygame.K_KP8: (+0, +1),
    pygame.K_KP7: (-1, +1),
    pygame.K_KP9: (+1, +1),
    pygame.K_KP1: (-1, -1),
    pygame.K_KP3: (+1, -1),
}