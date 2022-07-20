import sys
import logging
from os.path import dirname, join
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from droptopus import config, settings, args
from droptopus.window import MainWindow

class App(QApplication):
    def __init__(self, args=None):
        logging.info("Initializing Droptopus App " + config.VERSION)
        super(App, self).__init__([config.APP_NAME])
        script_dir = dirname(__file__)
        self.setStyleSheet(open(join(script_dir, 'assets', 'app.css')).read())
        self.mainWindow = MainWindow()
        self.mainWindow.show()

        iconFilepath = join(config.ASSETS_DIR, "droptopus.png")
        icon = QIcon(
            QPixmap(iconFilepath).scaled(
                50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.setWindowIcon(icon)
