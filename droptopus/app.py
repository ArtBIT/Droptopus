import sys
import config
import args
import logging
import settings
from window import MainWindow
from PyQt4.QtGui import QApplication

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
    AboutDialog QWidget {
    }
    QFrame[frameShape="4"], /* QFrame::HLine == 0x0004 */
    QFrame[frameShape="5"]  /* QFrame::VLine == 0x0005 */
    {
    }
    DropWidget {
        background-color: rgba(0,0,0,0%);
    }
    DropWidget[draggedOver=true],
    DropWidget[hover=true] {
        background-color: rgba(0,0,0,50%);
    }
    """
    self.setStyleSheet(css) 
    self.mainWindow = MainWindow()
    self.mainWindow.show();

