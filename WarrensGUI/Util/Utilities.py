__author__ = 'pi'

from WarrensGame.CONSTANTS import *
from WarrensGUI.Util.Constants import *

#Thanks to unknow, found following functions at
#https://www.pygame.org/wiki/TextWrapping?parent=CookBook

from itertools import chain

def truncline(text, font, maxwidth):
        real=len(text)
        stext=text
        l=font.size(text)[0]
        cut=0
        a=0
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)
            done=0
        return real, done, stext

def wrapline(text, font, maxwidth):
    done=0
    wrapped=[]

    while not done:
        nl, done, stext=truncline(text, font, maxwidth)
        wrapped.append(stext.strip())
        text=text[nl:]
    return wrapped

def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)

#End of functions found at
#https://www.pygame.org/wiki/TextWrapping?parent=CookBook

def clamp(n, minn, maxn):
    """
    This function returns the number n limited to the range min-max.
    """
    return max(min(maxn, n), minn)

def getElementColor(element):
    '''
    This function looks up the preferred color for the given element
    :param element: Element type
    :return: RGB color tuple
    '''
    if element == HEAL:
        return HEAL_COLOR
    elif element == WATER:
        return WATER_COLOR
    elif element == AIR:
        return AIR_COLOR
    elif element == FIRE:
        return FIRE_COLOR
    elif element == EARTH:
        return EARTH_COLOR
    elif element == ELEC:
        return ELEC_COLOR
    elif element == MIND:
        return MIND_COLOR
    else:
        raise NotImplementedError("Missing element to color mapping.")

def getElementMinHeight(element):
    '''
    This function looks up the minimum height for the given element
    :param element: Element type
    :return: Minimum height
    '''
    #TODO fill in the others
    if element == HEAL:
        return 0.1
    elif element == WATER:
        return WATER_COLOR
    elif element == AIR:
        return AIR_COLOR
    elif element == FIRE:
        return 0.1
    elif element == EARTH:
        return 0.0001
    elif element == ELEC:
        return ELEC_COLOR
    elif element == MIND:
        return MIND_COLOR
    else:
        raise NotImplementedError("Missing element to color mapping.")

def getElementMaxHeight(element):
    '''
    This function looks up the maximum height for the given element
    :param element: Element type
    :return: Maximum height
    '''
    #TODO fill in the others
    if element == HEAL:
        return TILESIZE
    elif element == WATER:
        return WATER_COLOR
    elif element == AIR:
        return AIR_COLOR
    elif element == FIRE:
        return 0.8 * TILESIZE
    elif element == EARTH:
        return 0.1 * TILESIZE
    elif element == ELEC:
        return ELEC_COLOR
    elif element == MIND:
        return MIND_COLOR
    else:
        raise NotImplementedError("Missing element to color mapping.")