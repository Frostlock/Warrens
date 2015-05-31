'''
Created on Mar 20, 2014

@author: pi

This module contains utility functions to show Messages and Menu's on a pygame surface.
'''
import pygame
import sys

from WarrensGUI.Deprecated import GuiCONSTANTS
from WarrensGUI.Util import Utilities


FONT_PANEL = None
FONT_HEADER = None
FONT_NORMAL = None

def initFonts():
    '''
    This function will initialize the fonts
    '''
    global FONT_PANEL, FONT_HEADER, FONT_NORMAL
    FONT_PANEL = pygame.font.Font(None, 20)
    FONT_HEADER = pygame.font.Font(None, 30)
    FONT_NORMAL = pygame.font.Font(None, 20)  

def showMessageControls(target):
    header = "Controls"
    message = "  Movement: keypad or arrowkeys\n" + \
              "  Attack: move towards target\n" + \
              "  Portals: > to go down, < to go up.\n" + \
              "  Pick up item: , \n" + \
              "  View and use inventory: i\n" + \
              "  Drop from inventory: d\n"
              
    showMessage(target, header, message)
    
def showMessage(target, header, message):
    '''
    This function will show a pop up message in the middle of the target surface.
    It waits for the user to acknowledge the message by hitting enter or escape.
    '''
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msgWidth = int(target.get_width()/2) 
    
    #Render the header
    line = FONT_HEADER.render(header, 1, GuiCONSTANTS.COLOR_FONT)
    lines.append(line)
    headerWidth = line.get_rect().size[0]
    if headerWidth > msgWidth: msgWidth = headerWidth
    msgHeight = line.get_rect().size[1]

    #Render the lines of the message
    split_message = Utilities.wrap_multi_line(message, FONT_NORMAL, msgWidth)
    for part in split_message:
        line = FONT_NORMAL.render(part, 1, GuiCONSTANTS.COLOR_FONT)
        lines.append(line)
        lineWidth = line.get_rect().size[0]
        if lineWidth > msgWidth: msgWidth = lineWidth
        msgHeight += line.get_rect().size[1]

    #center message on the screen
    x = target.get_width() / 2 - msgWidth / 2
    y = target.get_height() / 2 - msgHeight / 2
    
    
    #take copy of current screen
    originalSurface = target.copy()
    
    #display message background
    msgBackground = pygame.Surface((msgWidth,msgHeight), pygame.SRCALPHA)
    msgBackground.fill(GuiCONSTANTS.COLOR_MENU_BG)
    target.blit(msgBackground, (x,y))

    #display message
    xOfset = x
    yOfset = y
    for line in lines:
        target.blit(line, (xOfset,yOfset))
        yOfset += line.get_rect().size[1]
    
    #refresh display
    pygame.display.flip()
    
    #wait for user to acknowledge message
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE:
                    loop = False
            
    #restore original screen
    target.blit(originalSurface, (0,0))
    #refresh display
    pygame.display.flip()        

def showMenu(target, header, items):
    '''
    shows a menu with multiple items centered on the target surface
    returns integer index of selected item or None
    '''
    global FONT_HEADER, FONT_NORMAL
    lines = []
    msgWidth = int(target.get_width()/2)
    
    #Render the header
    line = FONT_HEADER.render(header, 1, GuiCONSTANTS.COLOR_FONT)
    lines.append(line)
    headerWidth = line.get_rect().size[0]
    if headerWidth > msgWidth: msgWidth = headerWidth
    msgHeight = line.get_rect().size[1]

    #Render a line for every item
    selectionCodes = []
    for i in range(0, len(items)):
        selectionCode = str(i)
        selectionCodes.append(selectionCode)
        line = FONT_NORMAL.render(selectionCode + ": " + items[i], 1, GuiCONSTANTS.COLOR_FONT)
        lines.append(line)
        lineWidth = line.get_rect().size[0]
        if lineWidth > msgWidth: msgWidth = lineWidth
        msgHeight += line.get_rect().size[1]
        
    #center message on the screen
    x = target.get_width() / 2 - msgWidth / 2
    y = target.get_height() / 2 - msgHeight / 2
    
    #take copy of current screen
    originalSurface = target.copy()
    
    #display message background
    msgBackground = pygame.Surface((msgWidth,msgHeight), pygame.SRCALPHA)
    msgBackground.fill(GuiCONSTANTS.COLOR_MENU_BG)
    target.blit(msgBackground, (x,y))

    #display message
    xOfset = x
    yOfset = y
    for line in lines:
        target.blit(line, (xOfset,yOfset))
        yOfset += line.get_rect().size[1]
    
    #refresh display
    pygame.display.flip()
    
    #wait for the user to choose an option
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    selection = None
                    loop = False
                elif event.unicode in selectionCodes:
                    #TODO: problem in current implementation option 10 and above can not be selected, hitting 1 will select option 1
                    selection = int(event.unicode)
                    loop = False       
            
    #restore original screen
    target.blit(originalSurface, (0,0))
    #refresh display
    pygame.display.flip()
    
    #return selected value 
    return selection
