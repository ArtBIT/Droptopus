from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import config
from window import MainWindow

"""
Droptopus
description: Drag'n'drop router that routes the dropped object to the specified action.
author: Djordje Ungar
website: djordjeungar.com
"""
class App(QApplication):

  def __init__(self, args=None):
    super(App, self).__init__([config.APP_NAME])
    self.mainWindow = MainWindow()
    self.mainWindow.show();

