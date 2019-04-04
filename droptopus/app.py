import sys
import logging
from os.path import join
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
)
from PyQt5.QtCore import (
    Qt,
)
from droptopus import config, settings, args
from droptopus.window import MainWindow

class App(QApplication):

  def __init__(self, args=None):
    logging.info('Initializing Droptopus App')
    super(App, self).__init__([config.APP_NAME])
    css = """
    MiniWindow,
    DropTitleBar {
        Background: transparent;
    }
    MainWindow {
        font-size: 12px;
        color: black;
        Background: transparent;
        color: white;
        font:12px bold;
        font-weight: bold;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        height: 30px;
    }
    DropTitleBar > QToolButton {
        Background: transparent;
        font-size: 11px;
    }
    DropTitleBar > QToolButton:focus {
        border: none;
        outline: none;
    }
    QLabel {
        color:white;
        Background: transparent;
    }
    EditItemForm QLabel,
    QMessageBox QLabel,
    QInputDialog QLabel {
        color: #333;
    }
    AboutDialog,
    DropTitleBar,
    DropFrame {
        Background: rgba(0,0,0,70%);
        color:white;
        font:13px ;
        font-weight:bold;
    }
    AboutDialog,
    DropTitleBar,
    DropFrame {
        border-radius: 10px;
    }
    AboutDialog QPushButton {
        background-color: gray;
    }
    AboutDialog QLabel#title {
        font-size: 16px;
        font-weight: bold;
    }
    DropWidget {
        background-color: rgba(0,0,0,0%);
    }
    DropWidget[draggedOver=true],
    DropWidget[hover=true] {
        background-color: rgba(255,255,255,5%);
    }
    """
    self.setStyleSheet(css) 
    self.mainWindow = MainWindow()
    self.mainWindow.show();

    iconFilepath = join(config.ASSETS_DIR, 'droptopus.png')
    icon = QIcon(QPixmap(iconFilepath).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    self.setWindowIcon(icon)
