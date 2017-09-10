import os
import sys
import re
import magic
import urllib
import tempfile
import subprocess
import config

from os import rename
from shutil import copyfile
from os.path import islink, isfile, isdir, join , expanduser
import utils

from PyQt4 import QtGui, QtCore

EVENT_RELOAD_WIDGETS = QtCore.QEvent.registerEventType(1337);

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
    def __init__(self, parent, title, icon):
        super(BaseDropWidget, self).__init__(parent)
        self.setAcceptDrops(True)

        width = 100
        height = 100
        self.name = title
        self.icon = IconWidget(self, icon)
        label = QtGui.QLabel()
        label.setText(title)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding);
        label.setMaximumWidth(width)
        label.setWordWrap(True)
        self.label = label
        self.actions = [
            ('Paste', self.onPasteFromClipboard),
            ('Choose File', self.onFileOpen),
            ('--', None),
            ('Rename', self.onRename),
            ('Remove', self.onDelete)
        ]

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.icon)
        layout.setAlignment(self.icon, QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Expanding);
        self.setFixedWidth(width)
        #self.setFixedSize(width,height)

    def propagateEvent(self, evt):
        app = QtGui.QApplication.instance()
        target = self.parent()
        while target:
            app.sendEvent(target, evt)
            if not evt.isAccepted():
                if hasattr(target, 'parent'):
                    target = target.parent()
            else:
                target = None
        return evt.isAccepted()

    def contextMenuEvent(self, event):
        if not self.actions:
            return

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

    def onRename(self):
        name, ok = QtGui.QInputDialog.getText(self, "Enter the new name for this action", "Action name:", QtGui.QLineEdit.Normal, self.name)
        if ok and name:
            old_filepath = join(config.ACTIONS_DIR, utils.slugify(self.name))
            new_filepath = join(config.ACTIONS_DIR, utils.slugify(name))
            if old_filepath == new_filepath:
                return
            if isfile(new_filepath):
                return QtGui.QMessageBox.critical(self, 'Error', 'Target action already exists.', QtGui.QMessageBox.Ok)

            if isfile(old_filepath) or isdir(old_filepath):
                os.rename(old_filepath, new_filepath)
            old_filepath = old_filepath + '.png'
            if isfile(old_filepath):
                new_filepath = new_filepath + '.png'
                os.rename(old_filepath, new_filepath)
            self.name = name
            self.propagateEvent(QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def onDelete(self):
        reply = QtGui.QMessageBox.question(self, 'Message', 'Are you sure you want to delete this action?', QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            filepath = join(config.ACTIONS_DIR, self.name)
            if isfile(filepath):
                os.remove(filepath)
            if islink(filepath):
                os.unlink(filepath)
            filepath = filepath + '.png'
            if os.path.isfile(filepath):
                os.remove(filepath)
            self.propagateEvent(QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def onFileOpen(self):
        myhome = expanduser("~")
        fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', myhome)
        self.handle(fname)

    def onPasteFromClipboard(self):
        clipboard = QtGui.QApplication.instance().clipboard()
        self.handle(clipboard.text())

    def handle(self, context):
        context = unicode(context.toUtf8(), encoding="UTF-8")
        print "Context: "+context
        return context

    def setStyleProperty(self, prop, value):
        self.setProperty(prop, value)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def dragLeaveEvent(self, event):
        self.setStyleProperty("draggedOver", False);

    def dragEnterEvent(self, event):
        print event
        self.setStyleProperty("draggedOver", True);
        if event.mimeData().hasUrls():
            event.accept()
        elif event.mimeData().hasImage():
            event.accept()
        elif event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            self.handle(event.mimeData().text())
        elif event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                url = str(url.toString())
                self.handle(url)
        QtGui.QWidget.dropEvent(self, event)

class DropWidget(BaseDropWidget):
    def __init__(self, parent, title, icon, filepath):
        super(DropWidget, self).__init__(parent, title, icon)
        self.filepath = filepath

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

class DirTarget(DropWidget):
    def handle_filepath(self, filepath):
        print "DirTarget.handle_filepath: "+filepath
        dest = join(self.filepath, os.path.basename(filepath))
        copyfile(filepath, dest)

    def handle_text(self, text):
        print "DirTarget.handle_text: "+text
        tmp = next(tempfile._get_candidate_names())
        tmp = join(self.filepath, tmp)
        text_file = open(tmp+".txt", "w")
        text_file.write(text.encode('utf8'))
        text_file.close()

    def handle_url(self, url):
        print "DirTarget.handle_url: "+url
        tmp = tempfile.NamedTemporaryFile(delete=False)
        urllib.urlretrieve(url, tmp.name)
        ext = magic.from_file(tmp.name, mime=True).split('/')[1]
        dest = join(self.filepath, utils.slugify(url.split('/').pop()) + '.' + ext)
        copyfile(tmp.name, dest)

class FileTarget(DropWidget):
    def handle_filepath(self, filepath):
        print "FileTarget.handle_filepath: "+filepath
        subprocess.call([self.filepath, filepath])

    def handle_text(self, text):
        print "FileTarget.handle_text: "+text
        subprocess.call([self.filepath, text])

    def handle_url(self, url):
        print "FileTarget.handle_url: "+url
        subprocess.call([self.filepath, url])

class CreateFileTarget(DropWidget):
    def __init__(self, parent, title, icon, filepath):
        super(CreateFileTarget, self).__init__(parent, title, icon, filepath)
        self.actions = [
            ('Paste', self.onPasteFromClipboard),
            ('Open...', self.onFileOpen)
        ]

    def handle(self, context):
        context = unicode(context.toUtf8(), encoding="UTF-8")
        name = os.path.basename(context)
        name, ok = QtGui.QInputDialog.getText(self, "Enter the name for the new action", "Action name:", QtGui.QLineEdit.Normal, name)
        #name = unicode(name, encoding="UTF-8").strip()
        if ok and name:
            action_filepath = join(config.ACTIONS_DIR, utils.slugify(name))
            if isfile(action_filepath):
                return QtGui.QMessageBox.critical(self, 'Error', 'Target action already exists.', QtGui.QMessageBox.Ok)
            if re_url.match(context):
                # download the url first
                tmp = tempfile.NamedTemporaryFile(delete=False)
                urllib.urlretrieve(context, tmp.name)
                copyfile(tmp.name, action_filepath)
            elif isfile(context):
                copyfile(context, action_filepath)
            else:
                text_file = open(action_filepath, "w")
                text_file.write(context)
                text_file.close()

            icon_filepath = QtGui.QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
            if icon_filepath:
                copyfile(icon_filepath, action_filepath + '.png')
            return self.propagateEvent(QtCore.QEvent(EVENT_RELOAD_WIDGETS));

    def mouseDoubleClickEvent(self, event):
        self.onFileOpen()

class CreateDirTarget(DropWidget):
    def __init__(self, parent, title, icon, filepath):
        super(CreateDirTarget, self).__init__(parent, title, icon, filepath)
        self.actions = [
            ('Paste', self.onPasteFromClipboard),
            ('Open...', self.onFileOpen)
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
            action_filepath = join(config.ACTIONS_DIR, utils.slugify(name))
            if isfile(action_filepath):
                return QtGui.QMessageBox.critical(self, 'Error', 'Target action already exists.', QtGui.QMessageBox.Ok)
            if isdir(context):
                os.symlink(context, action_filepath)
                icon_filepath = QtGui.QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
                if icon_filepath:
                    copyfile(icon_filepath, action_filepath + '.png')
                return self.propagateEvent(QtCore.QEvent(EVENT_RELOAD_WIDGETS));
            else:
                return QtGui.QMessageBox.critical(self, 'Error', 'Target should be a local directory.', QtGui.QMessageBox.Ok)

    def mouseDoubleClickEvent(self, event):
        self.onFileOpen()
