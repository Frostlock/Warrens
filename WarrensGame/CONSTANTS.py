#!/usr/bin/python

#Load this module to access the global constants

'''
This module contains all the constants that are used by the dungeonGame package.
Note that all constants are CAPITAL letters only for clarity.
'''
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 50
TILE_DEFAULT_COLOR = (175,175,175)

#dungeon generation
DUNGEON_ROOM_MAX_SIZE = 10
DUNGEON_ROOM_MIN_SIZE = 6
DUNGEON_MAX_ROOMS = 30
DUNGEON_COLOR_FLOOR = (134,134,134)
DUNGEON_COLOR_WALL = (75,70,50)
DUNGEON_TEXTURE = './textures/dungeon.png'

#town generation
TOWN_HOUSE_MAX_SIZE = 14
TOWN_HOUSE_MIN_SIZE = 8
TOWN_MAX_HOUSES = 18
TOWN_COLOR_BORDER = (25,25,25)
TOWN_COLOR_DIRT = (127,75,35)
TOWN_COLOR_STONE = (105,105,105)
TOWN_TEXTURE = './textures/town.png'

#cave generation
CAVE_COLOR_ROCK = (75,50,35)
CAVE_COLOR_DIRT = (120,90,70)
CAVE_TEXTURE = './textures/cave.png'

#field of view
TORCH_RADIUS = 10
TOWN_RADIUS = 30

#experience and level-ups
LEVEL_UP_BASE = 200
LEVEL_UP_FACTOR = 150

#data files
DATA_MONSTERS = "./WarrensGame/Monsters.csv"
DATA_ITEMS = "./WarrensGame/Items.csv"
DATA_ITEM_MODIFIERS = "./WarrensGame/ItemModifiers.csv"

#config switches
SHOW_GAME_LOGGING = False
SHOW_AI_LOGGING = False
SHOW_GENERATION_LOGGING = True
QUICKSTART = False

# Enumerator to describe the element of an effect.
HEAL = 0
HEAL_COLOR = (220,10,10)
WATER = 1
WATER_COLOR = (30,144,255)
AIR = 2
AIR_COLOR = (130,204,255)
FIRE = 3
FIRE_COLOR = (240,83,50)
EARTH = 4
EARTH_COLOR = (95,60,50)
ELEC = 5
ELEC_COLOR = (140,170,205)
MIND = 6
MIND_COLOR = (50,185,250)
