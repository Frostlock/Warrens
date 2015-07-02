__author__ = 'Frostlock'

import pygame
from pygame.locals import *
from WarrensGUI.Util.Constants import *
import WarrensGUI.Util.Utilities as Utilities

def createInfoPanel(actor, width):
    '''
    function to create a pygame surface object that shows information about an actor.
    :param actor: Actor object for which an InfoPanel has to be created
    :param width: preferred width for the panel
    :return: Pygame surface
    '''
    # Take a minimum of 150 pixels
    if width < 150 : width = 150
    # Take a maximum of 500 pixels
    if width > 300 : width = 300
    # Start with a big height, we will shrink at the end.
    height = 1024
    infoPanel = pygame.Surface((width,height), SRCALPHA)
    infoPanel.fill(COLOR_PG_HUD_BACKGROUND)
    yOffset = 2 * SPACE_INNER

    # Actor name
    if hasattr(actor, "name"):
        text = actor.name.capitalize()
        xOffset = 2 * SPACE_INNER
        textSurface = FONT_HUD_XL.render(text, True, COLOR_PG_HUD_TEXT)
        infoPanel.blit(textSurface, (xOffset, yOffset))
        # Challenge rating
        if hasattr(actor, "challengeRating"):
            rating = actor.challengeRating
            text = "CR: " + str(rating)
            crSurface = FONT_HUD_S.render(text, True, COLOR_PG_HUD_TEXT)
            xOffset = width - 2 * SPACE_INNER - crSurface.get_width()
            infoPanel.blit(crSurface, (xOffset, yOffset + textSurface.get_height() - crSurface.get_height()))
        yOffset += textSurface.get_height() + 2 * SPACE_INNER


    # Actor hitpoints
    if hasattr(actor, "currentHitPoints") and hasattr(actor, "maxHitPoints"):
        current = actor.currentHitPoints
        maximum = actor.maxHitPoints
        xOffset = 4 * SPACE_INNER
        barWidth = width - 2 * xOffset
        barHeight = FONT_HUD_XL.size("HP")[1]
        pygame.draw.rect(infoPanel, COLOR_PG_BAR_HEALTH_BG, (xOffset, yOffset,barWidth,barHeight))
        if current > 0:
            filWidth = int((current*barWidth)/maximum)
            pygame.draw.rect(infoPanel, COLOR_PG_BAR_HEALTH, (xOffset, yOffset,filWidth,barHeight))
        blitText = FONT_HUD_XL.render("HP: " + str(current) + "/" + str(maximum), True, COLOR_PG_HUD_TEXT)
        infoPanel.blit(blitText, (xOffset, yOffset))
        yOffset += barHeight + SPACE_INNER

    # Picture
    #
    # TODO: Decide GO / NOGO for actor pictures
    #  - Get the picture from the actor and only load it once for efficiency
    #  - Define picture URL for every actor, default pictures for actor classes
    #  - Code below works but needs image files
    #
    # yOffset += SPACE_INNER
    # xOffset = 4 * SPACE_INNER
    # picture = "./WarrensGUI/Assets/default.jpg"
    # img = pygame.image.load(picture)
    # scaleWidth = width - 2 * xOffset
    # scaleHeight = int((scaleWidth / float(img.get_width()))* img.get_height())
    # img = pygame.transform.scale(img, (scaleWidth, scaleHeight))
    # rect = infoPanel.blit(img, (xOffset, yOffset))
    # pygame.draw.rect(infoPanel, COLOR_PG_HUD_TEXT, rect, 1)
    # yOffset += img.get_height() + SPACE_INNER

    # Flavor text
    if hasattr(actor, "flavorText"):
        text = actor.flavorText
        xOffset = 4 * SPACE_INNER
        textWidth = width - 2 * xOffset
        textLines = Utilities.wrap_multi_line(text, FONT_HUD_L, textWidth)
        for line in textLines:
            surface = FONT_HUD_L.render(line, True, COLOR_PG_HUD_TEXT)
            infoPanel.blit(surface, (xOffset, yOffset))
            yOffset +=surface.get_height() + SPACE_INNER

    # Shrink to be just big enough
    yOffset += 3 * SPACE_INNER
    borderThickness = SPACE_INNER
    infoPanel = infoPanel.subsurface((0,0,width,yOffset + borderThickness))

    # Border
    pygame.draw.rect(infoPanel, COLOR_PG_HUD_TEXT, infoPanel.get_rect(), borderThickness)

    # Done
    return infoPanel