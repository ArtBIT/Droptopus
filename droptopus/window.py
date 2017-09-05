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
import math
import config

from PyQt4 import QtGui, QtCore 
from droptopus.widgets import IconWidget, DirTarget, ScriptTarget


# Remove all items from the layout
def clearLayout(layout):
    if layout != None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())


class DropTitleBar(QtGui.QDialog):
    def __init__(self, parent, title):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        css = """
        QWidget{
            Background: transparent;
        }
        QDialog{
            font-size: 12px;
            color: black;
            Background: rgba(0,0,0,50%);
            color: white;
            font:12px bold;
            font-weight: bold;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            height: 30px;
        }
        QToolButton {
            Background: transparent;
            font-size: 11px;
        }
        QToolButton:focus {
            border: none;
            outline: none;
        }
        QLabel {
            Background: transparent;
        }
        """
        self.setStyleSheet(css) 
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QtGui.QPalette.Highlight)

        minmax = QtGui.QToolButton(self)
        minmax.setIcon(QtGui.QIcon(join(config.ASSETS_DIR, 'minimize_window_white.png')))
        minmax.setMinimumHeight(10)
        minmax.setWindowOpacity(0.5)
        minmax.clicked.connect(self.minimax)
        minmax.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)

        close=QtGui.QToolButton(self)
        close.setIcon(QtGui.QIcon(join(config.ASSETS_DIR, 'close_window_white.png')))
        close.setMinimumHeight(10)
        close.setWindowOpacity(0.5)
        close.clicked.connect(self.close)
        close.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)

        self.label=QtGui.QLabel(self)
        self.label.setText(title)

        hbox = QtGui.QHBoxLayout(self)
        hbox.addWidget(self.label)
        hbox.addWidget(minmax)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)

    def contextMenuEvent(self, event):
        self.parent.contextMenuEvent(event)

    def setTitle(self, title):
        self.label.setText(title)

    def minimax(self):
        self.parent.parent.collapse()

    def close(self):
        QtGui.QApplication.instance().quit()

    def close(self):
        QtGui.QApplication.instance().quit()

    def reject(self):
        print "" #do not close on escape

class DropTargetGrid(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        layout = QtGui.QGridLayout()
        self.setLayout(layout)
        self.reload()

    def reload(self):
        clearLayout(self.layout())
        items = []
        # Create the config folder if it doesn't exist
        mypath = join(expanduser("~"),".droptopus")
        if not isdir(mypath):
            os.mkdir(mypath)
        for fname in listdir(mypath):
            if fname.endswith('.png'):
                # ignore icons
                continue 
            if isdir(join(mypath, fname)):
                icon_path = join(mypath, fname + '.png')
                if not isfile(icon_path):
                    icon_path = join(config.ASSETS_DIR, fname + '.png')
                if not isfile(icon_path):
                    icon_path = join(config.ASSETS_DIR, 'downloads.png')
                items.append({"type":"dir", "name":fname, "path":join(mypath, fname), "icon":icon_path})
            else:
                icon_path = join(mypath, fname + '.png')
                if not isfile(icon_path):
                    icon_path = join(config.ASSETS_DIR, fname + '.png')
                if not isfile(icon_path):
                    icon_path = join(config.ASSETS_DIR, 'add_file.png')
                items.append({"type":"file", "name":fname, "path":join(mypath, fname), "icon":icon_path})

        total_items = len(items)
        root = math.sqrt(total_items)
        rows = int(root)
        cols = int(total_items/rows) + 1
        m = sys.modules[__name__] # current module
        widget_classes = {"dir": getattr(m, 'DirTarget'), "file": getattr(m, 'ScriptTarget')}

        item_idx = 0
        layout = self.layout()
        for j in range(rows):
            for i in range(cols):
                if item_idx >= total_items:
                    break
                widget_info = items[item_idx]
                widget_class = widget_classes[widget_info['type']]
                widget = widget_class(self, widget_info['name'], widget_info['path'], widget_info['icon'])
                layout.addWidget(widget, j, i)
                item_idx = item_idx + 1

        #layout.setSizeConstraint( QtGui.QLayout.SetFixedSize )

class DropFrame(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.parent = parent
        css = """
        QFrame {
            Background: rgba(0,0,0,70%);
            color:white;
            font:13px ;
            font-weight:bold;
            border-radius: 10px;
        }
        """
        self.setStyleSheet(css) 

        self.titlebar = DropTitleBar(self, "Droptopus")
        self.content = DropTargetGrid(self)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.titlebar)
        vbox.addWidget(self.content)
        vbox.setMargin(0)
        vbox.setSpacing(0)
        self.setLayout(vbox)

    def mouseDoubleClickEvent(self, event):
        self.parent.collapse()

    def sizeHint(self):
        tbs = self.titlebar.sizeHint()
        return QtCore.QSize(tbs.width(), tbs.height()).__add__(self.content.sizeHint())

    def reload(self):
        self.content.reload()

class MiniWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.parent = parent
        icon = join(config.ASSETS_DIR, 'droptopus.png')
        self.pixmap = QtGui.QPixmap(icon)
        self.icon_width = 107
        self.icon_height = 150
        self.setFixedWidth(self.icon_width)
        self.setFixedHeight(self.icon_height)
        self.setAcceptDrops(True)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def mouseDoubleClickEvent(self, event):
        self.parent.expand()

    def sizeHint(self):
        return QtCore.QSize(self.icon_width, self.icon_height)

    def dragEnterEvent(self, event):
        if not self.parent.is_expanded:
            QtCore.QTimer.singleShot(100, self.parent.expand)
        event.ignore()


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.is_visible = True
        self.is_expanded = True
        self.is_move_action = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowIcon(QtGui.QIcon(join(config.ASSETS_DIR, 'droptopus.png')))
        self.setWindowTitle("Droptopus")

        self.miniwin = MiniWindow(self)
        self.frame = DropFrame(self)
        self.frame.show()

        self.content = QtGui.QStackedWidget()
        self.setCentralWidget(self.content)
        self.content.addWidget(self.frame);
        self.content.addWidget(self.miniwin);

        self.setMouseTracking(True)
        rect = QtGui.QDesktopWidget().screenGeometry()
        mini = self.miniwin.sizeHint()
        self.anchor = QtCore.QPoint(rect.right() - mini.width(), rect.bottom() - mini.height())
        self.collapse()

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        label = ('Expand', 'Collapse')[self.is_expanded]
        expand_action = menu.addAction(label)
        reload_action = menu.addAction("Reload")
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
        elif action == quit_action:
            self.close()

    def expand(self):
        if self.is_expanded:
            return
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
        self.is_expanded = False
        self.content.hide()
        mini = self.miniwin.sizeHint()
        self.setMinimumSize(mini)
        self.resize(mini)
        self.move(self.anchor)
        self.content.setCurrentWidget(self.miniwin)
        self.content.show()

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

