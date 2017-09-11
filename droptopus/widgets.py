import os
import sys
import re
import magic
import urllib
import math
import tempfile
import subprocess
import config
import settings
import utils

from os import rename
from shutil import copyfile
from os.path import isfile, isdir, join , expanduser
from forms import EditItemForm

from PyQt4 import QtGui, QtCore

EVENT_RELOAD_WIDGETS = QtCore.QEvent.registerEventType(1337);
EVENT_COLLAPSE_WINDOW = QtCore.QEvent.registerEventType(1338);
EVENT_CLOSE_WINDOW = QtCore.QEvent.registerEventType(1339);

re_url = re.compile(
        r'^(?:(?:http|ftp)s?://)?' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class IconWidget(QtGui.QWidget):
    def __init__(self, parent, icon, width=48, height=48):
        super(IconWidget, self).__init__(parent)
        self.pixmap = QtGui.QPixmap(icon).scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.setFixedWidth(width)
        self.setFixedHeight(height)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

class BaseDropWidget(QtGui.QWidget):
    def __init__(self, parent, name, index, icon):
        super(BaseDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.in_context_menu = False

        width = 100
        height = 100
        self.name = name
        self.index = index
        self.iconpath = icon
        self.icon = IconWidget(self, icon)
        label = QtGui.QLabel()
        label.setText(name)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding);
        label.setMaximumWidth(width)
        label.setWordWrap(True)
        self.label = label
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.icon)
        layout.setAlignment(self.icon, QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding);
        self.setFixedWidth(width)
        #self.setFixedSize(width,height)

    def handle(self, context):
        context = unicode(context.toUtf8(), encoding="UTF-8")
        return context

    def setStyleProperty(self, prop, value):
        self.setProperty(prop, value)
        self.style().unpolish(self)
        self.style().polish(self)

    def handleDragEvent(self, event):
        self.setStyleProperty("draggedOver", True);
        if event.mimeData().hasUrls():
            event.accept()
        elif event.mimeData().hasImage():
            event.accept()
        elif event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        self.handleDragEvent(event)

    def dragEnterEvent(self, event):
        self.handleDragEvent(event)

    def dragLeaveEvent(self, event):
        self.setStyleProperty("draggedOver", False);

    def dropEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
            self.handle(event.mimeData().text())
        elif event.mimeData().hasUrls():
            event.accept()
            for url in event.mimeData().urls():
                url = str(url.toString())
                self.handle(url)

        utils.propagateEvent(self, QtCore.QEvent(EVENT_COLLAPSE_WINDOW));
        QtGui.QWidget.dropEvent(self, event)
    
    # Have to override this so that QWidget subclasses
    # can update the background via qss
    def paintEvent(self, event):
        opt = QtGui.QStyleOption()
        opt.init(self)
        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtGui.QStyle.PE_Widget, opt, painter, self)

class DropWidget(BaseDropWidget):
    def __init__(self, parent, widget_type, name, index, icon, filepath):
        super(DropWidget, self).__init__(parent, name, index, icon)
        self.setAttribute(QtCore.Qt.WA_OpaquePaintEvent)
        self.type = widget_type
        self.filepath = filepath
        self.actions = [
            ('Process Clipboard', self.onPasteFromClipboard),
            ('Process File...', self.onFileOpen),
            ('--', None),
            ('Edit...', self.onEdit),
            ('Remove', self.onDelete)
        ]


    def handle(self, context):
        context = super(DropWidget, self).handle(context)
        if re_url.match(context):
            self.handle_url(context)
        elif isfile(context):
            self.handle_filepath(context)
        else:
            self.handle_text(context)

    def mouseDoubleClickEvent(self, event):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', self.filepath))
        elif os.name == 'nt':
            os.startfile(self.filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', self.filepath))

    def enterEvent(self,event):
        self.setStyleProperty('hover', True)

    def leaveEvent(self,event):
        if self.in_context_menu:
            return
        self.setStyleProperty('hover', False)

    def contextMenuEvent(self, event):
        if not self.actions:
            return
        # context menu happens before leaveEvent
        # so we have to have a flag to prevent it
        self.in_context_menu = True
        self.setStyleProperty('hover', True)
        menu = QtGui.QMenu(self)
        actions = {}
        for k, v in self.actions:
            if k == '--':
                menu.addSeparator()
                continue
            action = menu.addAction(k)
            actions[action] = v

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action in actions:
            actions[action]()
        self.setStyleProperty('hover', False)
        self.in_context_menu = False

    def onEdit(self):
        item = {
            "index": self.index,
            "type": self.type,
            "name": self.name,
            "path": self.filepath,
            "icon": self.iconpath,
        }
        form = EditItemForm(item, self)
        form.setModal(True)
        form.exec_()
        utils.propagateEvent(self, QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def onDelete(self):
        reply = QtGui.QMessageBox.question(self, 'Message', 'Are you sure you want to delete this action?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            settings.removeItem(self.index)
            utils.propagateEvent(self, QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def onFileOpen(self):
        myhome = expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', myhome)
        self.handle(fname)

    def onPasteFromClipboard(self):
        clipboard = QtGui.QApplication.instance().clipboard()
        self.handle(clipboard.text())


class DirTarget(DropWidget):
    def handle_filepath(self, filepath):
        dest = join(self.filepath, os.path.basename(filepath))
        copyfile(filepath, dest)

    def handle_text(self, text):
        tmp = next(tempfile._get_candidate_names())
        tmp = join(self.filepath, tmp)
        text_file = open(tmp+".txt", "w")
        text_file.write(text.encode('utf8'))
        text_file.close()

    def handle_url(self, url):
        tmp = tempfile.NamedTemporaryFile(delete=False)
        urllib.urlretrieve(url, tmp.name)
        ext = magic.from_file(tmp.name, mime=True).split('/')[1]
        dest = join(self.filepath, utils.slugify(url.split('/').pop()) + '.' + ext)
        copyfile(tmp.name, dest)

class FileTarget(DropWidget):
    def handle_filepath(self, filepath):
        subprocess.call([self.filepath, filepath])

    def handle_text(self, text):
        subprocess.call([self.filepath, text])

    def handle_url(self, url):
        subprocess.call([self.filepath, url])

class CreateFileTarget(DropWidget):
    def __init__(self, parent, widget_type, name, index, icon, filepath):
        super(CreateFileTarget, self).__init__(parent, widget_type, name, index, icon, filepath)
        self.actions = [
            ('Process Clipboard', self.onPasteFromClipboard),
            ('Process File...', self.onFileOpen)
        ]

    def handle(self, context):
        context = unicode(context.toUtf8(), encoding="UTF-8")
        name = os.path.basename(context)
        name, ok = QtGui.QInputDialog.getText(self, "Enter the name for the new action", "Action name:", QtGui.QLineEdit.Normal, name)
        #name = unicode(name, encoding="UTF-8").strip()
        if ok and name:
            if not isfile(context):
                return QtGui.QMessageBox.critical(self, 'Error', 'Target action must be a local file.', QtGui.QMessageBox.Ok)

            icon_filepath = QtGui.QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
            if not icon_filepath:
                icon_filepath = join(config.ASSETS_DIR, 'downloads.png')
            settings.pushItem({
                "type": self.type,
                "name": name,
                "path": context,
                "icon": icon_filepath
            })
            return utils.propagateEvent(self, QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def mouseDoubleClickEvent(self, event):
        self.onFileOpen()

class CreateDirTarget(DropWidget):
    def __init__(self, parent, widget_type, name, index, icon, filepath):
        super(CreateDirTarget, self).__init__(parent, widget_type, name, index, icon, filepath)
        self.actions = [
            ('Process Clipboard', self.onPasteFromClipboard),
            ('Process File...', self.onFileOpen)
        ]

    def onFileOpen(self):
        myhome = expanduser("~")
        fname = QtGui.QFileDialog.getExistingDirectory(self, 'Choose a directory', myhome)
        self.handle(fname)

    def handle(self, context):
        context = unicode(context.toUtf8(), encoding="UTF-8")
        name = os.path.basename(context)
        name, ok = QtGui.QInputDialog.getText(self, "Enter the name for the new action", "Action name:", QtGui.QLineEdit.Normal, name)
        #name = unicode(name, encoding="UTF-8").strip()
        if ok and name:
            if not isdir(context):
                return QtGui.QMessageBox.critical(self, 'Error', 'Target should be a local directory.', QtGui.QMessageBox.Ok)

            icon_filepath = QtGui.QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
            if not icon_filepath:
                icon_filepath = join(config.ASSETS_DIR, 'downloads.png')
            settings.pushItem({
                "type": self.type,
                "name": name,
                "path": context,
                "icon": icon_filepath
            })
            return utils.propagateEvent(self, QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def mouseDoubleClickEvent(self, event):
        self.onFileOpen()


class DropTitleBar(QtGui.QDialog):
    def __init__(self, parent, title):
        QtGui.QWidget.__init__(self, parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
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
        self.parent().contextMenuEvent(event)

    def setTitle(self, title):
        self.label.setText(title)

    def minimax(self):
        utils.propagateEvent(self, QtCore.QEvent(EVENT_COLLAPSE_WINDOW));

    def close(self):
        utils.propagateEvent(self, QtCore.QEvent(EVENT_CLOSE_WINDOW));

    def reject(self):
        print "" #do not close on escape

class DropTargetGrid(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.init_layout()
        self.settings = QtCore.QSettings()
        self.reload()

    def init_layout(self):
        layout = QtGui.QHBoxLayout(self)
        sidebar_layout = QtGui.QVBoxLayout()
        sidebar_layout.addWidget(self.instantiateWidget({"type":"create_dir", "name": "Add Directory", "path": "", "icon": join(config.ASSETS_DIR, 'add_folder.png')}))
        sidebar_layout.addWidget(self.instantiateWidget({"type":"create_file", "name": "Add Executable", "path": "", "icon": join(config.ASSETS_DIR, 'add_file.png')}))
        sidebar_layout.addStretch()
        layout.addLayout(sidebar_layout)
        vline = QtGui.QFrame()
        vline.setFrameShape(QtGui.QFrame.VLine)
        vline.setFrameShadow(QtGui.QFrame.Plain)
        layout.addWidget(vline)
        self.grid_layout = QtGui.QGridLayout()
        layout.addLayout(self.grid_layout)

    def event(self, evt):
        if evt.type() == EVENT_RELOAD_WIDGETS:
            evt.accept()
            self.reload()
        return super(DropTargetGrid, self).event(evt)


    def reload(self):
        layout = self.grid_layout;
        utils.clearLayout(layout)
        items = settings.readItems()
        total_items = len(items)
        root = math.sqrt(total_items)
        rows = int(root)
        cols = int(total_items/rows) + 1
        settings.writeItems(items)

        item_idx = 0
        for j in range(rows):
            for i in range(cols):
                if item_idx >= total_items:
                    break
                layout.addWidget(self.instantiateWidget(items[item_idx], item_idx), j, i)
                item_idx = item_idx + 1


    def instantiateWidget(self, widget_info, index = None):
        m = sys.modules[__name__] # current module
        widget_classes = {
            "dir": getattr(m, 'DirTarget'), 
            "file": getattr(m, 'FileTarget'),
            "create_file": getattr(m, 'CreateFileTarget'),
            "create_dir": getattr(m, 'CreateDirTarget')
        }
        widget_class = widget_classes[widget_info['type']]
        widget = widget_class(self, widget_info['type'], widget_info['name'], index, widget_info['icon'], widget_info['path'])
        return widget

class DropFrame(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        self.setFrameShape(QtGui.QFrame.StyledPanel)

        self.titlebar = DropTitleBar(self, "Droptopus")
        self.content = DropTargetGrid(self)

        vbox = QtGui.QVBoxLayout(self)
        vbox.addWidget(self.titlebar)
        vbox.addWidget(self.content)
        vbox.setMargin(0)
        vbox.setSpacing(0)
        self.setLayout(vbox)

    def sizeHint(self):
        tbs = self.titlebar.sizeHint()
        return QtCore.QSize(tbs.width(), tbs.height()).__add__(self.content.sizeHint())

    def reload(self):
        self.content.reload()
