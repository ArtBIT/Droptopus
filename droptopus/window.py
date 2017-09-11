#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Droptopus Main Window

author: Djordje Ungar
website: djordjeungar.com
"""
import os
from os import listdir
from os.path import isfile, isdir, join, expanduser
import sys
import config
import settings
import utils
import __version__

from PyQt4 import QtGui, QtCore 
from widgets import IconWidget, DirTarget, FileTarget, CreateFileTarget, CreateDirTarget, DropFrame
from widgets import EVENT_COLLAPSE_WINDOW, EVENT_CLOSE_WINDOW

class MiniWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        icon = join(config.ASSETS_DIR, 'droptopus.png')
        self.pixmap = QtGui.QPixmap(icon).scaled(100, 100, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.icon_width = self.pixmap.width()
        self.icon_height = self.pixmap.height()
        self.setFixedWidth(self.icon_width)
        self.setFixedHeight(self.icon_height)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return QtCore.QSize(self.icon_width, self.icon_height)

class DarkDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(DarkDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.is_move_action = False
        self.offset = None

    def mousePressEvent(self, event):
        if not event.button() == QtCore.Qt.LeftButton:
            return
        self.is_move_action = True
        self.offset = event.pos()

    def mouseReleaseEvent(self, event):
        self.is_move_action = False

    def mouseMoveEvent(self, event):
        if not self.is_move_action:
            return
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)

    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)


class AboutDialog(DarkDialog):
    def __init__(self, parent = None):
        super(AboutDialog, self).__init__(parent)

        main_layout = QtGui.QVBoxLayout(self)
        margin = 20
        main_layout.setContentsMargins(margin, margin, margin, margin)

        layout = QtGui.QHBoxLayout()
        # add icon
        icon = join(config.ASSETS_DIR, 'droptopus.png')
        label = QtGui.QLabel()
        label.setPixmap(QtGui.QPixmap(icon).scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        layout.addWidget(label)

        info_layout = QtGui.QVBoxLayout()
        # add title
        label = QtGui.QLabel()
        label.setObjectName('title')
        label.setText('Droptopus')
        info_layout.addWidget(label)
        label = QtGui.QLabel()
        label.setText('v'+__version__.__version__)
        info_layout.addWidget(label)
        info_layout.addStretch()
        # about text
        self.label = QtGui.QLabel(self)
        self.label.setOpenExternalLinks(True)
        self.label.setText("""
            <div><strong>Author:</strong> Djordje Ungar</div>
            <div><strong>Source:</strong> <a href="https://github.com/ArtBIT/Droptopus" style="color:white">GitHub</a></div>
            <div><strong>Icons:</strong> <a href="http://icons8.com/license" style="color:white">Icons8</a></div>
            <br>
        """);
        info_layout.addWidget(self.label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        layout.addStretch()

        main_layout.addLayout(layout)

        # OK and Cancel buttons
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        self.resize(300,200)

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.settings = QtCore.QSettings()

        self.is_visible = True
        self.is_expanded = True
        self.is_move_action = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setAttribute(QtCore.Qt.WA_QuitOnClose)
        self.setWindowIcon(QtGui.QIcon(join(config.ASSETS_DIR, 'droptopus.png')))
        self.setWindowTitle("Droptopus")

        self.miniwin = MiniWindow(self)
        self.frame = DropFrame(self)
        self.frame.show()

        self.readSettings()

        self.content = QtGui.QStackedWidget()
        self.setCentralWidget(self.content)
        self.content.addWidget(self.frame);
        self.content.addWidget(self.miniwin);

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.collapse()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        label = ('Expand', 'Collapse')[self.is_expanded]
        expand_action = menu.addAction(label)
        reload_action = menu.addAction("Reload")
        about_action = menu.addAction("About")
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == expand_action:
            if self.is_expanded:
                self.collapse()
            else:
                self.expand()
        elif action == reload_action:
            self.collapse()
            self.frame.reload()
            self.expand()
        elif action == about_action:
            self.showAbout()
        elif action == quit_action:
            self.close()

    def expand(self):
        if self.is_expanded:
            return
        self.setAcceptDrops(False)
        self.is_expanded = True
        self.content.hide()
        expanded = self.frame.sizeHint()
        self.setMinimumSize(expanded)
        self.resize(expanded)
        self.content.setCurrentWidget(self.frame)
        self.content.show()

    def collapse(self):
        if not self.is_expanded:
            return
        self.setAcceptDrops(True)
        self.is_expanded = False
        self.content.hide()
        mini = self.miniwin.sizeHint()
        self.setMinimumSize(mini)
        self.resize(mini)
        self.move(self.anchor)
        self.content.setCurrentWidget(self.miniwin)
        self.content.show()

    def showAbout(self):
        about = AboutDialog(self)
        about.setModal(True)
        about.show()

    def mouseReleaseEvent(self, event):
        self.is_move_action = False

    def mousePressEvent(self, event):
        if not event.button() == QtCore.Qt.LeftButton:
            return
        self.is_move_action = True
        self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if not self.is_move_action:
            return
        x = event.globalX()
        y = event.globalY()
        x_w = self.offset.x()
        y_w = self.offset.y()
        self.move(x-x_w, y-y_w)
        if self.content.currentWidget() == self.miniwin:
            self.anchor = self.pos()

    def writeSettings(self):
        self.settings.beginGroup("MainWindow");
        self.settings.setValue("anchor", self.anchor);
        self.settings.endGroup();

    def readSettings(self):
        self.settings.beginGroup("MainWindow");
        saved_anchor = self.settings.value("anchor", None);
        if saved_anchor != None:
            self.anchor = saved_anchor.toPoint();
        else:
            rect = QtGui.QDesktopWidget().screenGeometry()
            mini = self.miniwin.sizeHint()
            self.anchor = QtCore.QPoint(rect.right() - mini.width(), rect.bottom() - mini.height())
        self.settings.endGroup();

    def userReallyWantsToQuit(self):
        reply = QtGui.QMessageBox.question(self, 'Close Droptopus', 'Are you sure you want to close the application?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        return reply == QtGui.QMessageBox.Yes

    def closeEvent(self, event):
        if self.userReallyWantsToQuit():
            self.writeSettings();
            event.accept();
        else:
            event.ignore();

    #def dragMoveEvent(self, event):
    #    super(MainWindow, self).dragMoveEvent(event)

    def dragEnterEvent(self, event):
        if not self.is_expanded:
            QtCore.QTimer.singleShot(200, self.expand)
        else:
            super(MainWindow, self).dragEnterEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def event(self, evt):
        et = evt.type()
        if et == EVENT_COLLAPSE_WINDOW:
            evt.accept()
            self.collapse()
            return True
        elif et == EVENT_CLOSE_WINDOW:
            evt.accept()
            self.close()
            return True
        return super(MainWindow, self).event(evt)

