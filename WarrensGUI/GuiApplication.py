'''
Created on Mar 16, 2014

@author: pi
'''

from WarrensGame.Game import Game, Application
from WarrensGame.Actors import Character
from WarrensGame.Effects import EffectTarget
from WarrensGame.Maps import TileType

import sys, pygame
from pygame.locals import *

import GuiUtilities
import GuiCONSTANTS
import GuiTextures

#movement keys
movement_keys = {
        pygame.K_h: (-1, +0),       # vi keys
        pygame.K_l: (+1, +0),
        pygame.K_j: (+0, +1),
        pygame.K_k: (+0, -1),
        pygame.K_y: (-1, -1),
        pygame.K_u: (+1, -1),
        pygame.K_b: (-1, +1),
        pygame.K_n: (+1, +1),
        pygame.K_KP4: (-1, +0),     # numerical keypad
        pygame.K_KP6: (+1, +0),
        pygame.K_KP2: (+0, +1),
        pygame.K_KP8: (+0, -1),
        pygame.K_KP7: (-1, -1),
        pygame.K_KP9: (+1, -1),
        pygame.K_KP1: (-1, +1),
        pygame.K_KP3: (+1, +1),
        pygame.K_LEFT: (-1, +0),    # arrows and pgup/dn keys
        pygame.K_RIGHT: (+1, +0),
        pygame.K_DOWN: (+0, +1),
        pygame.K_UP: (+0, -1),
        pygame.K_HOME: (-1, -1),
        pygame.K_PAGEUP: (+1, -1),
        pygame.K_END: (-1, +1),
        pygame.K_PAGEDOWN: (+1, +1),
        }
                    
class GuiApplication(Application):
    '''
    PyGame implementation for dungeonGame GUI
    '''
   
    @property
    def surfaceDisplay(self):
        '''
        Main PyGame surface, the actual surface of the window that is visible to the user.
        This is the main surface, the other surfaces are helper surfaces which are blitted to this one in every rendering loop.
        '''
        return self._surfaceDisplay

    @property
    def surfaceViewPort(self):
        '''
        Helper surface that contains the current view of the map. 
        '''
        return self._surfaceViewPort  
    
    @property
    def surfacePanel(self):
        '''
        Helper surface for the panel at the bottom of the screen.
        '''
        return self._surfacePanel
    
    @property
    def surfaceDetails(self):
        '''
        Helper surface for the mouse over details.
        '''
        return self._surfaceDetails
    
    @property
    def tileSize(self):
        '''
        Tile size in pixels
        '''
        return self._tileSize

    @property
    def viewPortFont(self):
        '''
        Pygame font used to draw actors in the viewport surface
        '''
        return self._viewPortFont
    
    @property
    def zoomFactor(self):
        '''
        Minimum zoom factor is 1, in this case the entire map is shown on the screen.
        Higher zoom factors will zoom in on specific areas of the map.
        '''
        return self._zoomFactor

    @property
    def renderLevel(self):
        '''
        Gets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        '''
        return self._renderLevel
    
    @renderLevel.setter
    def renderLevel(self, newRenderLevel):
        '''
        Sets the Level object that is currently rendered in the viewport.
        This property helps identifying if the currentLevel in the game changes.
        '''
        self._renderLevel = newRenderLevel
    
    @property
    def targetingMode(self):
        '''
        Returns boolean indicating whether GUI is in targeting mode or not.
        Targeting mode is used when the game requires the GUI to target something.
        '''
        return self._targetingMode
    
    @property 
    def draggingMode(self):
        '''
        Returns boolean indicating whether a mouse dragging operation is going on at the moment.
        '''
        return self._draggingMode
    
    @property
    def game(self):
        """
        Returns the current game.
        """
        return self._game
    
    def __init__(self):
        '''
        Constructor
        '''
        #Initialize PyGame
        pygame.init()
        
        #Initialize fonts
        GuiUtilities.initFonts()
        
        #Initialize properties
        self._game = None
        self.renderLevel = None
        self._draggingMode = False
        self._targetingMode = False
        
        #Initialize display surface
        size = (1000, 750)
        self.setupSurfaces(size)
        
        #Set mouse cursor
        pygame.mouse.set_cursor(*pygame.cursors.tri_left)
        
        #Initialize window title
        pygame.display.set_caption(GuiCONSTANTS.APPLICATION_NAME)


    def setupSurfaces(self,displaySize):
        '''
        creates the surfaces in the game interface
        displaySize should be (width, height) tuple
        '''
        #Main display surface
        self._surfaceDisplay = pygame.display.set_mode(displaySize,RESIZABLE)
        
        #Panel at the bottom of the screen
        width = displaySize[0]
        height = int(displaySize[1]/6)
        self._surfacePanel = pygame.Surface((width,height))
        self.surfacePanel.fill(GuiCONSTANTS.COLOR_PANEL)
        
        #Viewport for the map gets remaining space above the panel
        width = displaySize[0]
        height = displaySize[1] - self.surfacePanel.get_height()        
        self._surfaceViewPort = pygame.Surface((width,height))
        self._renderViewPortWidth = self.surfaceViewPort.get_width()
        self._renderViewPortHeight  = self.surfaceViewPort.get_height()

        #clear helper surface for pop up window
        self._surfaceDetails = None
        
        #Initialize rendering parameters
        self.renderInit()
          
    def showMainMenu(self):
  
        #Welcome sequence
        #GuiUtilities.showMessage(self.surfaceDisplay,'Welcome!', 'Welcome to this bit of python code!\n It sure is not nethack :-).\n Now I only need to find a really really good intro story, maybe something about an evil wizard with a ring and bunch of small guys with hairy feet that are trying to destroy the ring. I bet that would be original. But hey in all seriousness, this is just some text to make sure that the auto wrapping feature works correctly.\n \n-Frost')
        
        options = ['New game', ' Controls', 'Quit']
        selection = GuiUtilities.showMenu(self.surfaceDisplay, 'Main Menu',options)
        
        if selection is None:
            #sys.exit()
            return
        elif selection == 0:
            # first option
            print 'Main Menu: Starting new game'
            self.playNewGame()
        elif selection == 1:
            # second option
            print 'Main Menu: ' + options[1]
            GuiUtilities.showMessageControls(self.surfaceDisplay)
        elif selection == 2:
            # third option
            print 'Main Menu: Quit!'
            sys.exit()
        else:
            print 'unknown selection...?'
    
    def playNewGame(self):
        #Initialize a basic game
        self._game = Game(self)
        
        #Initialize rendering variables
        self._renderSelectedTile = None
        self._zoomFactor = 1
        self._renderViewPortX = 0
        self._renderViewPortY = 0
        
        clock = pygame.time.Clock()
        
        if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING: import time
        #main loop
        loop = True
        self._gamePlayerTookTurn = False
        while loop:
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING: start_time = time.time()
            #render the screen
            self.renderGame()
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING: render_time = time.time() - start_time

            #handle pygame (GUI) events
            events = pygame.event.get()
            for event in events:
                self.handleEvent(event)
            
            #handle game events
            if self.game.player.state == Character.DEAD:
                #zoom in on player corpse
                self.eventZoomOnTile(self.game.player.tile)
                
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING:event_time = time.time() - start_time - render_time

            #If the player took a turn: Let the game play a turn
            if self._gamePlayerTookTurn: 
                self._game.playTurn()
                self._gamePlayerTookTurn = False
            
            #limit framerate (kinda optimistic since with current rendering we don't achieve this framerate :) )
            frameRateLimit = 30
            clock.tick(frameRateLimit)
            
            if GuiCONSTANTS.SHOW_PERFORMANCE_LOGGING: print "LOOP! FrameRateLimit: " + str(frameRateLimit) + " Rendering: " + str(render_time) + "s " + str(len(events)) + " events: " + str(event_time) + "s"
 
    def handleEvent(self, event):
        #Quit
        if event.type == pygame.QUIT: sys.exit()
        
        #Window resize
        elif event.type == VIDEORESIZE:
            self.setupSurfaces(event.dict['size'])
        
        #mouse
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.targetingMode:
                    self.eventTargetingAcquire()
            elif event.button == 2:
                self.eventDraggingStart()
            elif event.button == 4:
                self.eventZoomIn()
            elif event.button == 5:
                self.eventZoomOut()
        elif event.type == MOUSEMOTION:
            self.eventMouseMovement()           
        elif event.type == MOUSEBUTTONUP:
            if event.button == 2:
                self.eventDraggingStop()
        
        #keyboard    
        elif event.type == pygame.KEYDOWN:
            #Handle keys that are always active
            if event.key == pygame.K_ESCAPE:
                if self.targetingMode: 
                    #get out of targeting mode
                    self.eventTargetingStop()
                else:
                    #Show Menu 
                    self.showMainMenu() 
            #Handle keys that are active while playing
            if self.game.state == Game.PLAYING:
                player = self.game.player
                if player.state == Character.ACTIVE:
                    #movement
                    global movement_keys
                    if event.key in movement_keys:
                        player.tryMoveOrAttack(*movement_keys[event.key])
                        #TODO: Decide in the game code if turn is taken or not, tookATurn should be bool on player which can be reset by the game.
                        self._gamePlayerTookTurn = True
                    
                    #portal keys
                    elif event.key == pygame.K_LESS:
                        #check for shift modifier to detect ">" key.
                        mods = pygame.key.get_mods()
                        if (mods & KMOD_LSHIFT) or (mods & KMOD_RSHIFT): 
                            player.tryFollowPortalDown()
                        else:
                            player.tryFollowPortalUp()
                    #inventory
                    elif event.key == pygame.K_i:
                        self.useInventory()
                    elif event.key == pygame.K_d:
                        self.dropInventory()
                    #interact
                    elif event.key == pygame.K_COMMA:
                        player.tryPickUp()
                    
                    # update field of vision
                    if self._gamePlayerTookTurn:
                        self.game.currentLevel.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)
           
    
    def renderGame(self):
        '''
        Main render function
        '''
        #Detect new level loaded
        if not self.renderLevel is self.game.currentLevel:
            self.renderLevel = self.game.currentLevel
            self.renderInit()
        
        #Update viewport
        self.renderViewPort()
        
        #Update panel
        self.renderPanel()
        
        #Blit the viewport to the main display
        self._viewPortOffset = (0,0)
        self.surfaceDisplay.blit(self.surfaceViewPort, self._viewPortOffset)
        
        #Blit the panel to the main display
        self.surfaceDisplay.blit(self.surfacePanel, (0,self.surfaceViewPort.get_height() -1))
        
        #refresh display
        pygame.display.flip()
        
        #show effects
        self.showEffects()
        
        
    def renderInit(self):
        '''
        Initializes rendering parameters.
        This function should be called on window resizing, loading a new level and changing zoom levels.
        '''
        if self.game is None: return
        
        #Initialize maximum tile size for current viewport
        vpWidth = self.surfaceViewPort.get_size()[0]
        vpHeight = self.surfaceViewPort.get_size()[1]
        maxTileWidth = vpWidth / self.game.currentLevel.map.width
        maxTileHeight = vpHeight / self.game.currentLevel.map.height
        if maxTileWidth < maxTileHeight:
            maxTileSize = maxTileWidth
        else:
            maxTileSize = maxTileHeight
        #take into account the zoom factor
        self._tileSize = maxTileSize * self.zoomFactor
        
        #Initialize render font, a size of roughly 1,5 times the tileSize gives good results
        self._viewPortFont = pygame.font.Font(None, self.tileSize + self.tileSize/2)
        
        #initialize textures
        GuiTextures.initTextures(self.renderLevel.map.textureFile,self.tileSize)
        
        #determine max coords for view port location
        totalWidth = self.renderLevel.map.width * self.tileSize
        totalHeight = self.renderLevel.map.height *self.tileSize
        self._renderViewPortMaxX = totalWidth - self._renderViewPortWidth 
        self._renderViewPortMaxY = totalHeight - self._renderViewPortHeight
        if self._renderViewPortMaxX < 0: self._renderViewPortMaxX = 0
        if self._renderViewPortMaxY < 0: self._renderViewPortMaxY = 0

    def renderPanel(self):
        '''
        Update the content of the Panel surface
        '''
        #erase panel
        self.surfacePanel.fill(GuiCONSTANTS.COLOR_PANEL)
        
        #Left side (1/3) is used for player information
        #Right side (2/3) is used for game messages
        widthOffset = int(self.surfacePanel.get_width()/3) 
        heightOffset = self.surfacePanel.get_height()
        
        #Left side: render player information
        availableWidth = widthOffset
        xOffset = int(availableWidth/10)
        yOffset = 0
        spacer = 5
        if self.game.player is None: return
        #Player name
        blitText = GuiUtilities.FONT_PANEL.render(self.game.player.name + " (Lvl " + str(self.game.player.playerLevel) + ")", 1, GuiCONSTANTS.COLOR_PANEL_FONT)
        self.surfacePanel.blit(blitText, (int(xOffset/2), 2))
        yOffset += spacer
        #Determine bar width & height
        barWidth = availableWidth - 2*xOffset
        barHeight = GuiUtilities.FONT_PANEL.size("HP")[1]
        #Health bar
        yOffset += barHeight
        current = self.game.player.currentHitPoints
        maximum = self.game.player.maxHitPoints
        pygame.draw.rect(self.surfacePanel,GuiCONSTANTS.COLOR_BAR_HEALTH_BG, (xOffset, yOffset,barWidth,barHeight))
        if current > 0:
            filWidth = int((current*barWidth)/maximum)
            pygame.draw.rect(self.surfacePanel,GuiCONSTANTS.COLOR_BAR_HEALTH, (xOffset, yOffset,filWidth,barHeight))
        blitText = GuiUtilities.FONT_PANEL.render("HP: " + str(current) + "/" + str(maximum), 1, GuiCONSTANTS.COLOR_PANEL_FONT)
        self.surfacePanel.blit(blitText, (xOffset, yOffset))
        yOffset += barHeight + spacer
        #XP bar
        current = self.game.player.xp
        maximum = self.game.player.nextLevelXp
        pygame.draw.rect(self.surfacePanel,GuiCONSTANTS.COLOR_BAR_XP_BG, (xOffset, yOffset,barWidth,barHeight))
        if current > 0:
            filWidth = int((current*barWidth)/maximum)
            pygame.draw.rect(self.surfacePanel,GuiCONSTANTS.COLOR_BAR_XP, (xOffset, yOffset,filWidth,barHeight))
        blitText = GuiUtilities.FONT_PANEL.render("XP: " + str(current) + "/" + str(maximum), 1, GuiCONSTANTS.COLOR_PANEL_FONT)
        self.surfacePanel.blit(blitText, (xOffset, yOffset))
        
        #Right side: render game messages
        messageCounter = 1
        nbrOfMessages = len (self.game.messageBuffer)
        while heightOffset > 0:
            if messageCounter > nbrOfMessages: break
            #get messages from game message buffer, starting from the back
            message = self.game.messageBuffer[nbrOfMessages - messageCounter]
            #create textLines for message
            textLines = GuiUtilities.wrap_multi_line(message,GuiUtilities.FONT_PANEL,self.surfacePanel.get_width()-widthOffset)
            nbrOfLines = len(textLines)
            #blit the lines
            for l in range(1,nbrOfLines+1):
                blitLine = GuiUtilities.FONT_PANEL.render(textLines[nbrOfLines-l], 1, GuiCONSTANTS.COLOR_PANEL_FONT)
                heightOffset = heightOffset - blitLine.get_height()
                #only blit the line if there is enough remaining space to show it completely
                if heightOffset > blitLine.get_height():
                    self.surfacePanel.blit(blitLine, (widthOffset, heightOffset))
            messageCounter += 1
            
    def renderViewPort(self):
        '''
        Update the content of the Viewport surface
        '''
        #ensure viewport does not go over the edges off the map
        if self._renderViewPortX > self._renderViewPortMaxX:
            self._renderViewPortX = self._renderViewPortMaxX
        if self._renderViewPortX < 0:
            self._renderViewPortX = 0
        if self._renderViewPortY > self._renderViewPortMaxY:
            self._renderViewPortY = self._renderViewPortMaxY
        elif self._renderViewPortY < 0:
            self._renderViewPortY = 0
        
        #clear viewport    
        self.surfaceViewPort.fill(GuiCONSTANTS.COLOR_UNEXPLORED)
        
        #make sure field of view is up to date
        self.game.currentLevel.map.updateFieldOfView(self.game.player.tile.x, self.game.player.tile.y)
        
        #render tiles that are in the viewport area
        startX = int(self._renderViewPortX / self.tileSize)
        startY = int(self._renderViewPortY / self.tileSize)
        stopX = startX + int(self._renderViewPortWidth / self.tileSize)+1
        stopY = startY + int(self._renderViewPortHeight / self.tileSize)+1
        if stopX > self.renderLevel.map.width: stopX = self.renderLevel.map.width
        if stopY > self.renderLevel.map.height: stopY = self.renderLevel.map.height
        
        #calculate offset in viewport
        #basically the viewport is not aligned perfectly with the tiles, we need to track the offset.
        self._renderViewPortXOffSet = startX * self.tileSize - self._renderViewPortX
        self._renderViewPortYOffSet = startY * self.tileSize - self._renderViewPortY
        
        #prepare fog of war tile (used as overlay later)
        fogOfWar = pygame.Surface((self.tileSize,self.tileSize), pygame.SRCALPHA)
        fogOfWar.fill((0,0,0,180))
        
        tileCount = 0
        for curX in range(startX, stopX):
            for curY in range (startY, stopY):
                tile = self.renderLevel.map.tiles[curX][curY]
                vpX = (tile.x - startX) * self.tileSize + self._renderViewPortXOffSet
                vpY = (tile.y - startY) * self.tileSize + self._renderViewPortYOffSet
                tileRect = pygame.Rect(vpX, vpY, self.tileSize, self.tileSize)
                if tile.explored:
                    tileCount += 1
                    #blit empty tile first (empty tile underneath transparant overlay)
                    tex = GuiTextures.getTextureSurface(TileType.EMPTY)
                    self.surfaceViewPort.blit(tex,tileRect)
                    #blit possible tile texture (transparant overlay)
                    tex = GuiTextures.getTextureSurface(tile.type)
                    self.surfaceViewPort.blit(tex,tileRect)
                    #blit rect for tile border (this shows a black border for every tile)
                    #pygame.draw.rect(self.surfaceViewPort, (0,0,0), tileRect,1)
                    if tile.inView:
                        # draw any actors standing on this tile (monsters, portals, items, ...)
                        for myActor in tile.actors:
                            if myActor.inView:
                                textImg = self.viewPortFont.render(myActor.char, 1, myActor.color)
                                #Center                    
                                x = tileRect.x + (tileRect.width / 2 - textImg.get_width() /2)
                                y = tileRect.y + (tileRect.height / 2 - textImg.get_height() /2)
                                self.surfaceViewPort.blit(textImg, (x,y))
                                #===============================================
                                # #Change letter color to red based on monster health, it works but I don't think it is pretty enough.
                                # textImg = self.viewPortFont.render(myActor.char, 1, (255,0,0))
                                # factor = myActor.maxHitPoints / myActor.currentHitPoints
                                # factorRect = (0,0, textImg.get_width(), textImg.get_height() - int(textImg.get_height()/factor))
                                # self.surfaceViewPort.blit(textImg, (x,y), factorRect)
                                #===============================================
                    else:
                        #tile not in view: apply fog of war
                        self.surfaceViewPort.blit(fogOfWar,tileRect)
        
        #Draw portals on explored tiles (remain visible even when out of view)
        portals = self.game.currentLevel.portals
        for portal in portals:
            if portal.tile.explored:
                vpX = (portal.tile.x - startX) * self.tileSize + self._renderViewPortXOffSet
                vpY = (portal.tile.y - startY) * self.tileSize + self._renderViewPortYOffSet
                tileRect = pygame.Rect(vpX, vpY, self.tileSize, self.tileSize)
                textImg = self.viewPortFont.render(portal.char, 1, portal.color)
                #Center                    
                x = tileRect.x + (tileRect.width / 2 - textImg.get_width() /2)
                y = tileRect.y + (tileRect.height / 2 - textImg.get_height() /2)
                self.surfaceViewPort.blit(textImg, (x,y))
        
        #Redraw player character (makes sure it is on top of other characters)
        player = self.game.player
        vpX = (player.tile.x - startX) * self.tileSize + self._renderViewPortXOffSet
        vpY = (player.tile.y - startY) * self.tileSize + self._renderViewPortYOffSet
        tileRect = pygame.Rect(vpX, vpY, self.tileSize, self.tileSize)
        textImg = self.viewPortFont.render(player.char, 1, player.color)
        #Center                    
        x = tileRect.x + (tileRect.width / 2 - textImg.get_width() /2)
        y = tileRect.y + (tileRect.height / 2 - textImg.get_height() /2)
        self.surfaceViewPort.blit(textImg, (x,y))

        if self.targetingMode:
            #Indicate we are in targeting mode
            blitText = GuiUtilities.FONT_PANEL.render("Select target (Escape to cancel)", 1, (255,0,0))
            self.surfaceViewPort.blit(blitText, (6, 2 + blitText.get_height()))
            #highlight selected tile with a crosshair
            if self._renderSelectedTile is not None:
                tile = self._renderSelectedTile
                vpX = (tile.x - startX) * self.tileSize + self._renderViewPortXOffSet + self.tileSize/2
                vpY = (tile.y - startY) * self.tileSize + self._renderViewPortYOffSet + self.tileSize/2
                tileRect = pygame.Rect(vpX, vpY, self.tileSize, self.tileSize)
                pygame.draw.circle(self.surfaceViewPort,GuiCONSTANTS.COLOR_SELECT, (vpX, vpY), self.tileSize/2, 2)
        else:
            #highlight selected tile
            if self._renderSelectedTile is not None:
                tile = self._renderSelectedTile
                vpX = (tile.x - startX) * self.tileSize + self._renderViewPortXOffSet
                vpY = (tile.y - startY) * self.tileSize + self._renderViewPortYOffSet
                tileRect = pygame.Rect(vpX, vpY, self.tileSize, self.tileSize)
                pygame.draw.rect(self.surfaceViewPort,GuiCONSTANTS.COLOR_SELECT, tileRect, 2)
                self.renderDetailSurface(tile)
                #Show tile detail pop up
                if self.surfaceDetails is not None: 
                    pygame.draw.rect(self.surfaceViewPort,GuiCONSTANTS.COLOR_SELECT, tileRect)
                    self.surfaceViewPort.blit(self.surfaceDetails, (tileRect.x-self.surfaceDetails.get_width(), tileRect.y))
                
        #show level name in top left hand
        if self.game.currentLevel is not None:
            blitText = GuiUtilities.FONT_PANEL.render(self.game.currentLevel.name, 1, GuiCONSTANTS.COLOR_PANEL_FONT)
            self.surfaceViewPort.blit(blitText, (6, 2))
            
    def renderDetailSurface(self, tile):
        '''
        renders a surface containing info details for the given tile
        '''
        # create a component for every actor on the tile
        panelFont = GuiUtilities.FONT_PANEL
        components = []
        xOffSet , yOffSet = 3 , 3
        width , height = 2*xOffSet , 2*yOffSet
        for myActor in tile.actors:
            if myActor.inView:
                myText = myActor.char + ': ' + myActor.name + ' (' + str(myActor.currentHitPoints) + '/' + str(myActor.maxHitPoints) + ')'
                textImg = panelFont.render(myText, 1, myActor.color)
                components.append((xOffSet, yOffSet, textImg))
                height += textImg.get_height()
                yOffSet = height
                neededWidth = xOffSet + textImg.get_width() + xOffSet
                if neededWidth > width : width = neededWidth 
        if len(components) == 0:
            #nothing to see here (empty tile)
            self._surfaceDetails = None
        else:
            #create the new surface
            self._surfaceDetails = pygame.Surface((width,height), pygame.SRCALPHA)
            self.surfaceDetails.fill((0, 0, 0, 125))
            #border in selection color
            pygame.draw.rect(self.surfaceDetails,GuiCONSTANTS.COLOR_POPUP,(0,0,width,height),3)
            #add the components
            for (x,y,s) in components:
                self.surfaceDetails.blit(s, (x,y))

    def showEffects(self):
        for effectTuple in self.game.effectBuffer:
            effect, effectTiles = effectTuple
            
            #Current implementation looks at effect targetType to decide on a visualization option.
            
            if effect.targetType == EffectTarget.SELF:
                #flash tile on which actor is standing
                self.animationFlashTiles(effect.effectColor, effectTiles)
            elif effect.targetType == EffectTarget.CHARACTER:
                #circle around the target character
                self.animationNova(effect.effectColor, effectTiles[0], effect.effectRadius)
            elif effect.targetType == EffectTarget.TILE:
                #circular blast around centerTile
                self.animationNova(effect.effectColor, effect.centerTile, effect.effectRadius)
            else:
                print ('WARNING: Unknown visualization type, skipping.')
            self.game.effectBuffer.remove(effectTuple)
                    
    def animationFlashTiles(self, color, tiles):
        '''
        Animation of a colored flash effect on specified tiles
        color is an RGB tuple
        '''
        R, G, B = color
        flashOnSurface = pygame.Surface((self.tileSize,self.tileSize), pygame.SRCALPHA, 32)
        flashOnSurface.fill((R, G, B, 125))
        clock = pygame.time.Clock()
        #nbr of flashes per second
        flashes = 2
        #run an effectLoop
        for i in range (0,flashes):
            #flash on
            dirtyRects = []
            for tile in tiles:
                #translate to coords in the display
                displayX, displayY = self.calculateDisplayCoords(tile) 
                dirty = self.surfaceDisplay.blit(flashOnSurface, (displayX, displayY))
                dirtyRects.append(dirty)
            #render
            pygame.display.update(dirtyRects)
            #limit framerate
            frameRateLimit = 5 * flashes
            clock.tick(frameRateLimit)
            #flash of
            dirtyRects = []
            for tile in tiles:
                #translate to coords in the display
                viewPortX, viewPortY = self.calculateViewPortCoords(tile)
                displayX, displayY = self.calculateDisplayCoords(tile)
                #restore original tile from viewport surface
                vpRect = (viewPortX, viewPortY, self.tileSize, self.tileSize)
                dirty = self.surfaceDisplay.blit(self.surfaceViewPort, (displayX, displayY),vpRect)
                dirtyRects.append(dirty)
            #render
            pygame.display.update(dirtyRects)
            #limit framerate
            frameRateLimit = 5 * flashes
            clock.tick(frameRateLimit)

    def animationNova(self, color, centerTile, radius=0):
        R, G, B = color
        if radius == 0: 
            ripples = 1
            radius = self.tileSize
        else: 
            ripples = radius * 2
            radius = radius * self.tileSize
        #origin of Nova will be the middle of centerTile
        displayX, displayY = self.calculateDisplayCoords(centerTile)
        origX = displayX + int(self.tileSize / 2)
        origY = displayY + int(self.tileSize / 2)
        
        clock = pygame.time.Clock()
        rippleRadius = 0
        radiusIncrement = int(radius/ripples)
        #run an effectLoop
        for i in range (0,ripples):
            rippleRadius += radiusIncrement
            #render circle
            dirtyRects = []
            dirtyRect = pygame.draw.circle(self.surfaceDisplay, color, (origX, origY), rippleRadius, 3)
            dirtyRects.append(dirtyRect)
            #render
            pygame.display.update(dirtyRects)
            #limit framerate
            frameRateLimit = 5*ripples
            clock.tick(frameRateLimit)

    def calculateViewPortCoords(self, tile):
        '''
        calculates the (x, y) coordinate of the given tile on the surfaceViewPort
        '''
        x = tile.x * self.tileSize - self._renderViewPortX
        y = tile.y * self.tileSize - self._renderViewPortY
        return (x, y)

    def calculateDisplayCoords(self, tile):
        '''
        calculates the (x, y) coordinate of the given tile on the surfaceDisplay
        '''
        viewPortX, viewPortY = self.calculateViewPortCoords(tile)
        x = viewPortX + self._viewPortOffset[0]
        y = viewPortY + self._viewPortOffset[1]
        return (x, y) 

    def eventDraggingStart(self):
        self._draggingMode = True
        #call pygame.mouse.get_rel() to make pygame correctly register the starting point of the drag
        pygame.mouse.get_rel()

    def eventDraggingStop(self):
        self._draggingMode = False

    def eventMouseMovement(self):
        #check for on going drag
        if self.draggingMode:
            #get relative distance of mouse since last call to get_rel()
            rel = pygame.mouse.get_rel()
            #calculate new viewport coords
            self._renderViewPortX = self._renderViewPortX - rel[0]
            self._renderViewPortY = self._renderViewPortY - rel[1]
        else:
            pos = pygame.mouse.get_pos()
            #Coords relevant to viewport
            mouseX = pos[0]
            mouseY = pos[1]
            #Coords relevant to entire map
            mapX = self._renderViewPortX + mouseX
            mapY = self._renderViewPortY + mouseY
            #Determine Tile
            gameMap = self.game.currentLevel.map
            tileX = int(mapX/self.tileSize)
            tileY = int(mapY/self.tileSize)
            if tileX > 0 and tileX < gameMap.width-1 and tileY > 0 and tileY < gameMap.height-1:
                self._renderSelectedTile = gameMap.tiles[tileX][tileY]
            else:
                self._renderSelectedTile = None

    def eventZoomIn(self):
        '''
        Zoom in while centering on current mouse position.
        '''
        #zoom in limit
        if self.zoomFactor == GuiCONSTANTS.MAX_ZOOM_FACTOR: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoomFactor * ZoomMultiplier
        #Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        #Coords relevant to viewport
        mouseX = pos[0]
        mouseY = pos[1]
        #Coords relevant to entire map
        mapX = self._renderViewPortX + mouseX
        mapY = self._renderViewPortY + mouseY
        #viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = mapX*ZoomMultiplier - (self._renderViewPortWidth/2)
        self._renderViewPortY = mapY*ZoomMultiplier - (self._renderViewPortHeight/2)
        #Reset rendering parameters
        self.renderInit()

    def eventZoomOut(self):
        '''
        Zoom out while centering on current mouse position.
        '''
        #zoom out limit
        if self.zoomFactor == 1: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoomFactor / ZoomMultiplier
        if self.zoomFactor < 1: self._zoomFactor = 1
        #Center viewport on mouse location
        pos = pygame.mouse.get_pos()
        #Coords relevant to viewport
        mouseX = pos[0]
        mouseY = pos[1]
        #Coords relevant to entire map
        mapX = self._renderViewPortX + mouseX
        mapY = self._renderViewPortY + mouseY
        #viewport coords after zoom operation (center viewport on map coords)
        self._renderViewPortX = mapX/ZoomMultiplier - (self._renderViewPortWidth/2)
        self._renderViewPortY = mapY/ZoomMultiplier - (self._renderViewPortHeight/2)
        #Reset rendering parameters
        self.renderInit()

    def eventZoomOnTile(self, tile):
        '''
        zooms in on provided tile
        '''
        if self.zoomFactor == GuiCONSTANTS.MAX_ZOOM_FACTOR: return
        ZoomMultiplier = GuiCONSTANTS.ZOOM_MULTIPLIER
        #change zoom factor
        self._zoomFactor = self.zoomFactor * ZoomMultiplier
        #set new viewport coords
        self._renderViewPortX = tile.x * self.tileSize * ZoomMultiplier - (self._renderViewPortWidth/2)
        self._renderViewPortY = tile.y * self.tileSize * ZoomMultiplier - (self._renderViewPortHeight/2)
        #Reset rendering parameters
        self.renderInit()
        
    def useInventory(self):
        '''
        Present inventory to player with possibility to use an item.
        '''
        if self.game is not None and self.game.player is not None:
            header = "Select item to use, escape to cancel"
            options = []
            items = self.game.player.inventoryItems
            for item in items:
                options.append(item.name)
            selection = GuiUtilities.showMenu(self.surfaceDisplay, header, options)
            if selection is not None:
                useItem = items[selection]
                if useItem.targeted:
                    #ask player for target
                    self.eventTargetingStart(useItem)
                else:
                    #try to use the item
                    self.game.player.tryUseItem(useItem)

    def eventTargetingStart(self, item):
        self._targetingMode = True
        self._targetingItem = item
        self._targetType = item.effect.targetType
    
    def eventTargetingAcquire(self):
        #targeted tile is currently selected
        targetTile = self._renderSelectedTile
        #hack to avoid lingering selection tile 
        self._renderSelectedTile = None
        #find target based on targetType
        if self._targetType == EffectTarget.TILE:
            myTarget = targetTile
        elif self._targetType == EffectTarget.CHARACTER:
            #TODO: currently this finds all ACTORS, not limited to CHARACTERS
            #find target actor on tile
            if len(targetTile.actors) == 0: return
            if len(targetTile.actors) == 1: 
                myTarget = targetTile.actors[0]
            else:
                #show menu with options to target
                header = 'Select target (escape to cancel)'
                options = []
                for a in targetTile.actors:
                    options.append(a.name + ' (' + str(a.currentHitPoints) + '/' + str(a.maxHitPoints) + ')')
                selection = GuiUtilities.showMenu(self.surfaceDisplay, header,options)
                if selection is None: return
                else: myTarget = targetTile.actors[selection]

        #use target item on target
        self.game.player.tryUseItem(self._targetingItem, myTarget)
        #Leave targeting mode
        self.eventTargetingStop()
    
    def eventTargetingStop(self):
        self._targetingMode = False
        self._renderSelectedTile = None    
        
    def dropInventory(self):
        '''
        Present inventory to player with possibility to drop an item.
        '''
        if self.game is not None and self.game.player is not None:
            header = "Select item to drop, escape to cancel"
            options = []
            items = self.game.player.inventoryItems
            for item in items:
                options.append(item.name)
            selection = GuiUtilities.showMenu(self.surfaceDisplay, header, options)
            if selection is not None:
                self.game.player.tryDropItem(items[selection])