from WarrensGUI.GuiApplication import GuiApplication
from WarrensGUI.WarrensOpenGL import GlApplication

#This is where it all starts!
if __name__ == '__main__':
    print 'Select option:'
    print ' 0: 2D pygame interface'
    print ' 1: 3D pygame opengl interface (needs pyopengl)'
    
    #ans = 1
    ans = input()
    if ans == 0:
        _application = GuiApplication()
        #Start application
        _application.showMainMenu()
    elif ans == 1:
        _application = GlApplication()
        #Start application
        _application.showMainMenu()
    else:
        print 'Bad input, exiting'
    
    """
    from dungeonGame.AI import *
    ai = BasicMonsterAI(None)
    ai.test()
    
    """