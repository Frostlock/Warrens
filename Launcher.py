import sys

from WarrensGUI.Deprecated.GuiApplication import GuiApplication
from WarrensGUI.MainWindow import MainWindow


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
            # Run the 3D interface
            print ""
            print "Running 3D interface."
            print ""
            _application = MainWindow()
        elif FirstCommandLineArg == '-TEST':
            # Run testing suite
            import unittest
            # Load relevant unittest tests
            suite = unittest.TestLoader().discover('./WarrensTest', pattern = "*_test.py")
            print ""
            print "Running " + str(suite.countTestCases()) + " test cases:"
            print ""
            # Run the discovered suite of tests
            unittest.TextTestRunner(verbosity=2).run(suite)
        else:
            print 'Bad commandline parameter, exiting'
    else:
        _application = GuiApplication()
        #Start application
        _application.showMainMenu()