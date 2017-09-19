#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Droptopus Main Window

author: Djordje Ungar
website: djordjeungar.com
"""
import os
from os.path import isfile, isdir, join, expanduser
import sys

from droptopus import config, settings, utils, __version__
from droptopus.widgets import DropFrame, events

from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QPixmap,
)
from PyQt5.QtCore import (
    QEvent,
    QSettings,
    QSize,
    Qt,
    QPoint,
    QTimer,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QStyle,
    QStyleOption,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

class MiniWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.parent = parent
        icon = join(config.ASSETS_DIR, 'droptopus.png')
        self.pixmap = QPixmap(icon).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_width = self.pixmap.width()
        self.icon_height = self.pixmap.height()
        self.setFixedWidth(self.icon_width)
        self.setFixedHeight(self.icon_height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return QSize(self.icon_width, self.icon_height)

class DarkDialog(QDialog):
    def __init__(self, parent):
        super(DarkDialog, self).__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WA_MacAlwaysShowToolWindow )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        self.is_move_action = False
        self.offset = None

    def mousePressEvent(self, event):
        if not event.button() == Qt.LeftButton:
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
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)


class AboutDialog(DarkDialog):
    def __init__(self, parent = None):
        super(AboutDialog, self).__init__(parent)

        main_layout = QVBoxLayout(self)
        margin = 20
        main_layout.setContentsMargins(margin, margin, margin, margin)

        layout = QHBoxLayout()
        # add icon
        icon = join(config.ASSETS_DIR, 'droptopus.png')
        label = QLabel()
        label.setPixmap(QPixmap(icon).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(label)

        info_layout = QVBoxLayout()
        # add title
        label = QLabel()
        label.setObjectName('title')
        label.setText('Droptopus')
        info_layout.addWidget(label)
        label = QLabel()
        label.setText('v'+__version__.__version__)
        info_layout.addWidget(label)
        info_layout.addStretch()
        # about text
        self.label = QLabel(self)
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
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        self.resize(300,200)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.settings = QSettings()

        self.is_visible = True
        self.is_expanded = True
        self.is_move_action = False
        self.should_confirm_close = False
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_QuitOnClose)
        self.setWindowIcon(QIcon(join(config.ASSETS_DIR, 'droptopus.png')))
        self.setWindowTitle("Droptopus")

        self.miniwin = MiniWindow(self)
        self.frame = DropFrame(self)
        self.frame.show()

        self.readSettings()

        self.content = QStackedWidget()
        self.setCentralWidget(self.content)
        self.content.addWidget(self.frame);
        self.content.addWidget(self.miniwin);

        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.collapse()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        label = ('Expand', 'Collapse')[self.is_expanded]
        expand_action = menu.addAction(label)
        about_action = menu.addAction("About")
        menu.addSeparator()
        quit_action = menu.addAction("Quit")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == expand_action:
            if self.is_expanded:
                self.collapse()
            else:
                self.expand()
        elif action == about_action:
            self.showAbout()
        elif action == quit_action:
            self.should_confirm_close = True
            self.close()

    def expand(self):
        if self.is_expanded:
            return
        self.is_expanded = True
        self.setAcceptDrops(False)
        self.content.hide()
        expanded = self.frame.sizeHint()
        self.setMinimumSize(expanded)
        self.content.setCurrentWidget(self.frame)
        self.content.show()
        self.resize(expanded)

        # on OSX the window will not automatically stay inside the screen like on Linux
        # we have to do it manually
        screen_rect = QDesktopWidget().screenGeometry()
        window_rect = self.frameGeometry()
        intersection = window_rect & screen_rect
        dx = window_rect.width() - intersection.width()
        dy = window_rect.height() - intersection.height()
        unseen = window_rect & intersection
        if dx != 0 or dy != 0:
            if window_rect.left() > screen_rect.left():
                dx = dx * -1
            if window_rect.bottom() > screen_rect.bottom():
                dy = dy * -1
            self.move(window_rect.left() + dx, window_rect.top() + dy)

    def collapse(self):
        if not self.is_expanded:
            return
        self.is_expanded = False
        self.setAcceptDrops(True)
        self.content.hide()
        mini = self.miniwin.sizeHint()
        self.setMinimumSize(mini)
        self.move(self.anchor)
        self.content.setCurrentWidget(self.miniwin)
        self.content.show()
        self.resize(mini)

    def showAbout(self):
        about = AboutDialog(self)
        about.setModal(True)
        about.show()

    def mouseReleaseEvent(self, event):
        self.is_move_action = False

    def mousePressEvent(self, event):
        if not event.button() == Qt.LeftButton:
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
            self.anchor = saved_anchor;
        else:
            rect = QDesktopWidget().screenGeometry()
            mini = self.miniwin.sizeHint()
            self.anchor = QPoint(rect.right() - mini.width(), rect.bottom() - mini.height())
        self.settings.endGroup();

    def userReallyWantsToQuit(self):
        if not self.should_confirm_close:
            return True
        reply = QMessageBox.question(self, 'Close Droptopus', 'Are you sure you want to close the application?', QMessageBox.Yes, QMessageBox.No)
        return reply == QMessageBox.Yes

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
            QTimer.singleShot(200, self.expand)
        else:
            super(MainWindow, self).dragEnterEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()

    def event(self, evt):
        et = evt.type()
        if et == events.COLLAPSE_WINDOW:
            evt.accept()
            self.collapse()
            return True
        if evt.type() == events.RELOAD_WIDGETS:
            evt.accept()
            if self.is_expanded:
                self.resize(self.sizeHint())
        if et == events.EXPAND_WINDOW:
            evt.accept()
            self.expand()
            return True
        elif et == events.CLOSE_WINDOW:
            evt.accept()
            self.should_confirm_close = True
            self.close()
            return True
        return super(MainWindow, self).event(evt)

