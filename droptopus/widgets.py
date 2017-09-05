import os
import sys
import re
import magic
import urllib
import tempfile
import subprocess

from os import rename
from shutil import copyfile
from os.path import isfile, isdir, join , expanduser
from droptopus import utils

from PyQt4 import QtGui, QtCore

re_url = re.compile(
        r'^(?:(?:http|ftp)s?://)?' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class DropWidget(QtGui.QWidget):
    def __init__(self, parent, title, filepath, icon):
        super(DropWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.filepath = filepath

        self.icon = IconWidget(self, icon)
        self.label = QtGui.QLabel()
        self.label.setStyleSheet("QtGui.QLabel {color:#AAA}")
        self.label.setText(title)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.icon)
        layout.setAlignment(self.icon, QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.setAlignment(self.label, QtCore.Qt.AlignCenter)
        self.setLayout(layout)
        self.setFixedSize(100,100)

    def contextMenuEvent(self, event):
        menu = QtGui.QMenu(self)
        openAction = menu.addAction("Open file...")
        pasteAction = menu.addAction("Paste path")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == pasteAction:
            self.onPasteFromClipboard()
        elif action == openAction:
            self.onFileOpen()

    def mouseDoubleClickEvent(self, event):
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', self.filepath))
        elif os.name == 'nt':
            os.startfile(self.filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', self.filepath))

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
        if re_url.match(context):
            self.handle_url(context)
        elif isfile(context):
            self.handle_filepath(context)
        else:
            self.handle_text(context)

    def dragEnterEvent(self, event):
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

class IconWidget(QtGui.QWidget):
    def __init__(self, parent, icon):
        super(IconWidget, self).__init__(parent)
        self.pixmap = QtGui.QPixmap(icon)
        self.setFixedWidth(48)
        self.setFixedHeight(48)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        #painter.translate(event.rect().center());
        #painter.drawPixmap(QtCore.QPoint(-self.pixmap.width() / 2, -self.pixmap.height() / 2), self.pixmap)
        painter.drawPixmap(event.rect(), self.pixmap)

class DirTarget(DropWidget):
    def handle_filepath(self, filepath):
        print "DirTarget.handle_filepath: "+filepath
        dest = join(self.filepath, filepath.split('/').pop())
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

class ScriptTarget(DropWidget):
    def handle_filepath(self, filepath):
        print "ScriptTarget.handle_filepath: "+filepath
        subprocess.call([self.filepath, filepath])

    def handle_text(self, text):
        print "ScriptTarget.handle_text: "+text
        subprocess.call([self.filepath, text])

    def handle_url(self, url):
        print "ScriptTarget.handle_url: "+url
        subprocess.call([self.filepath, url])

