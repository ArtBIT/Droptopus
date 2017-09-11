import os
import config
import settings
from PyQt4 import QtCore, QtGui

class EditItemForm(QtGui.QDialog):
    def __init__(self, item, parent = None):
        super(EditItemForm, self).__init__(parent)
        l1 = QtGui.QLabel("Name:")
        name = QtGui.QLineEdit()

        l2 = QtGui.QLabel("Icon:")
        icon = QtGui.QLabel()
        btn_icon = QtGui.QPushButton("...")
        btn_icon.setFixedWidth(50)
        btn_icon.clicked.connect(self.onChangeIcon)

        l3 = QtGui.QLabel("Target Path:")
        path = QtGui.QLineEdit()
        path.setReadOnly(True)
        btn_path = QtGui.QPushButton("...")
        btn_path.setFixedWidth(50)
        btn_path.clicked.connect(self.onChangePath)

        layout = QtGui.QFormLayout(self)
        layout.addRow(l1, name)
        row = QtGui.QHBoxLayout()
        row.addWidget(icon)
        row.addWidget(btn_icon)
        layout.addRow(l2, row)
        row = QtGui.QHBoxLayout()
        row.addWidget(path)
        row.addWidget(btn_path)
        layout.addRow(l3, row)
        buttons = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.icon = icon
        self.name = name
        self.path = path

        self.loadItem(item)

    def loadItem(self, item):
        self.icon.setPixmap(QtGui.QPixmap(item["icon"]).scaled(50, 50, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.name.setText(item["name"])
        self.path.setText(item["path"])
        self.item = item

    def onChangeIcon(self):
        icon_filepath = QtGui.QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
        if icon_filepath:
            icon_size = 15
            self.icon.setPixmap(QtGui.QPixmap(icon_filepath).scaled(icon_size, icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
            self.item["icon"] = icon_filepath

    def onChangePath(self):
        path = self.item["path"] if len(self.item["path"]) else os.path.expanduser("~")
        if self.item["type"] == "dir":
            path = QtGui.QFileDialog.getExistingDirectory(self, 'Choose a directory', path)
            if path:
                self.path.setText(path)
                self.item["path"] = path
        else:
            path = QtGui.QFileDialog.getOpenFileName(self, 'Open file', path)
            if path:
                self.path.setText(path)
                self.item["path"] = path

    def validate(self):
        return True 

    def hideEvent(self, event):
        if not self.validate():
            QtGui.QMessageBox.critical(self, 'Error', "\n".join(self.validation_errors), QtGui.QMessageBox.Ok)
            event.ignore()
            return

        self.item['name'] = self.name.text()
        settings.writeItem(self.item)
        event.accept()
