import sys

from WarrensGUI.Deprecated import GuiApplication
from WarrensGUI.WarrensOpenGL import GlApplication


"""
Launcher script
Command line options
    -3D : Starts the opengl based implementation
"""
if __name__ == '__main__':
    #This is where it all starts!
    if len(sys.argv) > 1:
        FirstCommandLineArg = sys.argv [1]
        if FirstCommandLineArg == '-3D':
            _application = GlApplication()
            _application.showMainMenu()
        else:
            print 'Bad commandline parameter, exiting'
    else:
        _application = GuiApplication()
        #Start application
        _application.showMainMenu()