from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import config
from window import MainWindow

class App(QApplication):

  def __init__(self, args=None):
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
    DropTitleBar,
    DropFrame {
        border-radius: 10px;
    }
    AboutDialog {
        border: 1px solid rgba(255,255,255,10%);
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
    DropWidget[draggedOver=True] {
        Background: rgba(0,0,0,70%);
    }
    QFrame[frameShape="4"], /* QFrame::HLine == 0x0004 */
    QFrame[frameShape="5"]  /* QFrame::VLine == 0x0005 */
    {
    }
    """
    QCoreApplication.setOrganizationName(config.ORG_NAME);
    QCoreApplication.setOrganizationDomain(config.ORG_DOMAIN);
    QCoreApplication.setApplicationName(config.APP_NAME);
    self.settings = QSettings()
    self.setStyleSheet(css) 
    self.mainWindow = MainWindow()
    self.mainWindow.show();
