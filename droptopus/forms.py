import os
import config
import settings
from PyQt4.QtCore import Qt
from PyQt4.QtGui import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPixmap,
    QPushButton,
)

class EditItemForm(QDialog):
    def __init__(self, item, parent = None):
        super(EditItemForm, self).__init__(parent)
        l1 = QLabel("Name:")
        name = QLineEdit()

        l2 = QLabel("Icon:")
        icon = QLabel()
        btn_icon = QPushButton("...")
        btn_icon.setFixedWidth(50)
        btn_icon.clicked.connect(self.onChangeIcon)

        l3 = QLabel("Target Path:")
        path = QLineEdit()
        path.setReadOnly(True)
        btn_path = QPushButton("...")
        btn_path.setFixedWidth(50)
        btn_path.clicked.connect(self.onChangePath)

        layout = QFormLayout(self)
        layout.addRow(l1, name)
        row = QHBoxLayout()
        row.addWidget(icon)
        row.addWidget(btn_icon)
        layout.addRow(l2, row)
        row = QHBoxLayout()
        row.addWidget(path)
        row.addWidget(btn_path)
        layout.addRow(l3, row)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.icon = icon
        self.name = name
        self.path = path

        self.loadItem(item)

    def loadItem(self, item):
        self.icon.setPixmap(QPixmap(item["icon"]).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.name.setText(item["name"])
        self.path.setText(item["path"])
        self.item = item

    def onChangeIcon(self):
        icon_filepath = QFileDialog.getOpenFileName(self, 'Choose Icon', config.ASSETS_DIR)
        if icon_filepath:
            icon_size = 15
            self.icon.setPixmap(QPixmap(icon_filepath).scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.item["icon"] = icon_filepath

    def onChangePath(self):
        path = self.item["path"] if len(self.item["path"]) else os.path.expanduser("~")
        if self.item["type"] == "dir":
            path = QFileDialog.getExistingDirectory(self, 'Choose a directory', path)
            if path:
                self.path.setText(path)
                self.item["path"] = path
        else:
            path = QFileDialog.getOpenFileName(self, 'Open file', path)
            if path:
                self.path.setText(path)
                self.item["path"] = path

    def validate(self):
        return True 

    def hideEvent(self, event):
        if not self.validate():
            QMessageBox.critical(self, 'Error', "\n".join(self.validation_errors), QMessageBox.Ok)
            event.ignore()
            return

        self.item['name'] = self.name.text()
        settings.writeItem(self.item)
        event.accept()
