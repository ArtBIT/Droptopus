import os
import sys
import re
import magic
import requests
import math
import tempfile
import subprocess
import logging

from os import rename
from shutil import copyfile
from os.path import isfile, isdir, join , expanduser
from droptopus import config, settings, utils
from droptopus.forms import EditItemForm

from PyQt5.QtCore import (
    QEvent,
    QSettings,
    QSize,
    Qt,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStyle,
    QStyleOption,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from PyQt5.QtGui import (
    QPixmap,
    QPainter,
    QIcon,
    QPalette,
)

events = utils.dotdict({
    "RELOAD_WIDGETS": QEvent.registerEventType(1337),
    "COLLAPSE_WINDOW": QEvent.registerEventType(1338),
    "EXPAND_WINDOW": QEvent.registerEventType(1339),
    "CLOSE_WINDOW": QEvent.registerEventType(1340),
})

re_url = re.compile(
        r'^(?:(?:http|ftp)s?://)?' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class IconWidget(QWidget):
    def __init__(self, parent, icon, width=48, height=48):
        logging.info('Creating IconWidget with icon: %s', icon)
        super(IconWidget, self).__init__(parent)
        self.pixmap = QPixmap(icon).scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setFixedWidth(width)
        self.setFixedHeight(height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

class BaseDropWidget(QWidget):
    def __init__(self, parent, conf):
        super(BaseDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.in_context_menu = False

        width = 100
        height = 100
        self.name = conf["name"]
        self.index = conf["index"]
        self.iconpath = conf["icon"]
        self.icon = IconWidget(self, conf["icon"])
        label = QLabel()
        label.setText(conf["name"])
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding);
        label.setMaximumWidth(width)
        label.setWordWrap(True)
        self.label = label
        layout = QVBoxLayout()
        layout.addWidget(self.icon)
        layout.setAlignment(self.icon, Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, Qt.AlignCenter)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding);
        self.setFixedWidth(width)
        #self.setFixedSize(width,height)

    def handle(self, context):
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
                url = str(url)
                self.handle(url)

        utils.propagateEvent(self, QEvent(events.COLLAPSE_WINDOW));
        QWidget.dropEvent(self, event)
    
    # Have to override this so that QWidget subclasses
    # can update the background via qss
    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)

class DropWidget(BaseDropWidget):
    def __init__(self, parent, conf):
        super(DropWidget, self).__init__(parent, conf)
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        self.type = conf["type"]
        self.filepath = conf["path"]
        self.desc = conf["desc"]
        if self.desc:
            self.setToolTip(self.desc)
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
            return self.handle_url(context)
        elif isfile(context):
            return self.handle_filepath(context)
        else:
            return self.handle_text(context)

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
        menu = QMenu(self)
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
        """
        Opens and executes the edit form, which allows the user to edit the selected DropTarget
        """
        item = {
            "index": self.index,
            "type": self.type,
            "name": self.name,
            "path": self.filepath,
            "icon": self.iconpath,
            "desc": self.desc,
        }
        form = EditItemForm(item, self)
        form.setModal(True)
        form.exec_()
        utils.propagateEvent(self, QEvent(events.RELOAD_WIDGETS))

    def onDelete(self):
        """
        After confirming the delete action, removes the item from the settings file.
        """
        reply = QMessageBox.question(self, 'Message', 'Are you sure you want to delete this action?', QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            settings.removeItem(self.index)
            utils.propagateEvent(self, QEvent(events.RELOAD_WIDGETS));

    def onFileOpen(self):
        """
        Opens a standard file dialog and processess the selected filepath.
        """
        myhome = expanduser("~")
        fname, _filter = QFileDialog.getOpenFileName(self, 'Open file', myhome)
        self.handle(fname)

    def onPasteFromClipboard(self):
        """
        Handles clipboard paste event.
        """
        clipboard = QApplication.instance().clipboard()
        self.handle(clipboard.text())


class DirTarget(DropWidget):
    """
    A DropWidget that processes the dropped context and saves it to a directory.
    """
    def handle_filepath(self, filepath):
        """
        Processes passed filepath.
        """
        dest = join(self.filepath, os.path.basename(filepath))
        copyfile(filepath, dest)
        return 0, dest

    def handle_text(self, text):
        """
        Processes passed raw text.
        """
        tmp = next(tempfile._get_candidate_names())
        tmp = join(self.filepath, tmp) + '.txt'
        text_file = open(tmp, "w")
        text_file.write(text.encode('utf8'))
        text_file.close()
        return 0, tmp

    def handle_url(self, url):
        """
        Processes passed URL.
        """
        tmp = tempfile.NamedTemporaryFile(delete=False)
        r = requests.get(url)
        with open(tmp.name, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
            fd.close()
        ext = magic.from_file(tmp.name, mime=True).split('/')[1]
        dest = join(self.filepath, utils.slugify(url.split('/').pop())[:20] + '.' + ext)
        copyfile(tmp.name, dest)
        return 0, dest

class FileTarget(DropWidget):
    """
    A DropWidget that processes the dropped context processes it through a script.
    """
    def handle_filepath(self, filepath):
        """
        Processes passed filepath.
        """
        return subprocessCall([self.filepath, filepath])

    def handle_text(self, text):
        """
        Processes passed raw text.
        """
        return subprocessCall([self.filepath, text])

    def handle_url(self, url):
        """
        Processes passed URL.
        """
        return subprocessCall([self.filepath, url])

    def mouseDoubleClickEvent(self, event):
        subprocessCall([self.filepath])

class CreateTarget(DropWidget):
    """
    A DropWidget that creates a DirTarget or FileTarget
    """
    def __init__(self, parent, conf):
        conf["type"] = 'builtin'
        super(CreateTarget, self).__init__(parent, conf)
        self.actions = [
            ('Create Folder Action...', self.onCreateFolderAction),
            ('Create Executable Action...', self.onCreateFileAction),
            #('Create From Template...', self.onCreateFromTemplate),
        ]

    def onCreateFileAction(self):
        """
        Create a new FileTarget.
        """
        context, _filter = QFileDialog.getOpenFileName(self, 'Open file', expanduser('~'))
        context = str(context)
        if not context:
            return 1, 'Missing argument' 
        logging.info('Create file target: %s', context)
        name = os.path.basename(context)
        name, ok = QInputDialog.getText(self, "Enter the name for the new action", "Action name:", QLineEdit.Normal, name)
        if ok and name:
            if not isfile(context):
                QMessageBox.critical(self, 'Error', 'Target action must be a local file.', QMessageBox.Ok)
                return 1, 'Target action must be a local file' 

            icon_filepath, _filter = QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
            if not icon_filepath:
                icon_filepath = join(config.ASSETS_DIR, 'downloads.png')
            settings.pushItem({
                "type": 'file',
                "name": name,
                "desc": name,
                "path": context,
                "icon": icon_filepath
            })
            utils.propagateEvent(self, QEvent(events.RELOAD_WIDGETS));
            return 0, context

    def onCreateFolderAction(self):
        """
        Create a new DirTarget.
        """
        context = QFileDialog.getExistingDirectory(self, 'Choose a directory', expanduser('~'))
        context = str(context)
        if not context:
            return 1, 'Missing argument' 
        name = os.path.basename(context)
        name, ok = QInputDialog.getText(self, "Enter the name for the new action", "Action name:", QLineEdit.Normal, name)
        if ok and name:
            if not isdir(context):
                QMessageBox.critical(self, 'Error', 'Target should be a local directory.', QMessageBox.Ok)
                return 1, 'Target action must be a local directory' 

            icon_filepath, _filter = QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
            if not icon_filepath:
                icon_filepath = join(config.ASSETS_DIR, 'downloads.png')
            settings.pushItem({
                "type": 'dir',
                "name": name,
                "desc": name,
                "path": context,
                "icon": icon_filepath
            })
            utils.propagateEvent(self, QEvent(events.RELOAD_WIDGETS));
            return 0, context

    def onCreateFromTemplate(self):
        """
        TODO: make templates for standard actions like emails, twitter, etc.
        """
        pass

    def mousePressEvent(self, event):
        self.contextMenuEvent(event)

    def mouseDoubleClickEvent(self, event):
        pass

    def handle(self, context):
        pass



class DropTitleBar(QDialog):
    """
    TitleBar widget for our custom dialog.
    """
    def __init__(self, parent, title):
        QWidget.__init__(self, parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Highlight)

        minmax = QToolButton(self)
        minmax.setIcon(QIcon(join(config.ASSETS_DIR, 'minimize_window_white.png')))
        minmax.setMinimumHeight(10)
        minmax.setWindowOpacity(0.5)
        minmax.clicked.connect(self.minimax)
        minmax.setAttribute(Qt.WA_MacShowFocusRect, 0)

        close=QToolButton(self)
        close.setIcon(QIcon(join(config.ASSETS_DIR, 'close_window_white.png')))
        close.setMinimumHeight(10)
        close.setWindowOpacity(0.5)
        close.clicked.connect(self.close)
        close.setAttribute(Qt.WA_MacShowFocusRect, 0)

        self.label=QLabel(self)
        self.label.setText(title)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.label)
        hbox.addWidget(minmax)
        hbox.addWidget(close)
        hbox.insertStretch(1,500)
        hbox.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def contextMenuEvent(self, event):
        self.parent().contextMenuEvent(event)

    def setTitle(self, title):
        self.label.setText(title)

    def minimax(self):
        utils.propagateEvent(self, QEvent(events.COLLAPSE_WINDOW));

    def close(self):
        utils.propagateEvent(self, QEvent(events.CLOSE_WINDOW));

    def reject(self):
        return

class DropTargetGrid(QWidget):
    """
    The body of our custom dialog which contains a grid of DropTargets.
    """
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.grid_layout = QGridLayout(self)
        self.settings = QSettings()
        self.reload()

    def event(self, evt):
        if evt.type() == events.RELOAD_WIDGETS:
            self.reload()
        return super(DropTargetGrid, self).event(evt)


    def reload(self):
        logging.info('Reloading grid items')
        layout = self.grid_layout;
        utils.clearLayout(layout)
        items = settings.readItems()
        items.insert(0, {"type":"builtin", "name": "Create Action", "path": "", "icon": join(config.ASSETS_DIR, 'plus_white.png'), "desc": "Create a new drop action"})
        total_items = len(items)
        # Try to make the grid as close to a square as possible, but favour horizontal rectangles
        root = math.sqrt(total_items)
        rows = int(root)
        if rows == 0:
            rows = 1
        cols = int(total_items/rows) + 1

        item_idx = 0
        for j in range(rows):
            for i in range(cols):
                if item_idx >= total_items:
                    break
                conf = items[item_idx].copy()
                conf["index"] = item_idx-1
                layout.addWidget(self.instantiateWidget(conf), j, i)
                item_idx = item_idx + 1


    def instantiateWidget(self, conf):
        """
        A helper method to instantiat DropWidgets depeneding on the type.
        """
        m = sys.modules[__name__] # current module
        widget_classes = {
            "dir": getattr(m, 'DirTarget'), 
            "file": getattr(m, 'FileTarget'),
            "builtin": getattr(m, 'CreateTarget'),
        }
        widget_class = widget_classes[conf['type']]
        widget = widget_class(self, conf)
        return widget

class DropFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.setFrameShape(QFrame.StyledPanel)

        self.titlebar = DropTitleBar(self, "Droptopus")
        self.content = DropTargetGrid(self)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.titlebar)
        vbox.addWidget(self.content)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        self.setLayout(vbox)

    def sizeHint(self):
        tbs = self.titlebar.sizeHint()
        return QSize(tbs.width(), tbs.height()).__add__(self.content.sizeHint())

    def reload(self):
        self.content.reload()

def showError(text, details):
   msg = QMessageBox()
   msg.setIcon(QMessageBox.Critical)

   msg.setWindowTitle("Error")
   msg.setText(text)
   """
   msg.setInformativeText("This is additional information")
   """
   msg.setDetailedText("The details are as follows: " + details)
   msg.setStandardButtons(QMessageBox.Ok)
   retval = msg.exec_()
   print("value of pressed message box button:", retval)

def subprocessCall(args):
    cmd = args[0:1]
    filepath = args[1:2]
    ret = 0

    try:
        ret = subprocess.check_call(args)
    except subprocess.CalledProcessError:
        showError("Error executing subprocess call", "The subprocess failed for the following command " + "".join(args))
    except OSError:
        showError("Could not find executable", cmd)

    return ret, filepath
