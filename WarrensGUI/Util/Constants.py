__author__ = 'pi'

# This module contains a number of shared constants used by the GUI




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