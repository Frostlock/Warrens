'''
Created on Mar 21, 2014

@author: pi

This module contains all the constants that are used by the application.
Note that all constants are CAPITAL letters only for clarity.
'''

APPLICATION_NAME = "W@rrens"

#RGB Colors
COLOR_UNEXPLORED = (0,0,0)
COLOR_BLOCKED = (27,27,27)
COLOR_NOTBLOCKED = (47,47,47)
#COLOR_WALL = (100,76,20)
#COLOR_GROUND = (139,105,20)

COLOR_PANEL = (0,0,0)
COLOR_PANEL_FONT = (191,191,191)

COLOR_SELECT = (255,0,0)
COLOR_POPUP = (243,0,0)

COLOR_BAR_HEALTH = (150,0,0)
COLOR_BAR_HEALTH_BG = (25,0,0)
COLOR_BAR_XP = (0,150,0)
COLOR_BAR_XP_BG = (0,25,0)  

COLOR_FONT = (191,191,191)

#RGB + Alpha transparancy
COLOR_MENU_BG = (0, 0, 0, 125)


#Increase in zoom for each zooming operation
ZOOM_MULTIPLIER = 2
#not much sense in going over 64, but if you like you can :)
MAX_ZOOM_FACTOR = 16

#Config switches
SHOW_PERFORMANCE_LOGGING = False