import os
import logging

from droptopus import config, settings

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
)
from PyQt5.QtGui import QPixmap


class EditItemForm(QDialog):
    def __init__(self, item, parent=None):
        super(EditItemForm, self).__init__(parent)
        l1 = QLabel("Name:")
        name = QLineEdit()

        l2 = QLabel("Description:")
        desc = QLineEdit()

        l3 = QLabel("Icon:")
        icon = QLabel()
        btn_icon = QPushButton("...")
        btn_icon.setFixedWidth(50)
        btn_icon.clicked.connect(self.onChangeIcon)

        l4 = QLabel("Target Path:")
        path = QLineEdit()
        path.setReadOnly(True)
        btn_path = QPushButton("...")
        btn_path.setFixedWidth(50)
        btn_path.clicked.connect(self.onChangePath)

        layout = QFormLayout(self)
        layout.addRow(l1, name)
        layout.addRow(l2, desc)
        row = QHBoxLayout()
        row.addWidget(icon)
        row.addWidget(btn_icon)
        layout.addRow(l3, row)
        row = QHBoxLayout()
        row.addWidget(path)
        row.addWidget(btn_path)
        layout.addRow(l4, row)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.icon = icon
        self.name = name
        self.path = path
        self.desc = desc

        self.loadItem(item)

    def loadItem(self, item):
        self.icon.setPixmap(
            QPixmap(item["icon"]).scaled(
                50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.name.setText(item["name"])
        self.desc.setText(item["desc"])
        self.path.setText(item["path"])
        self.item = item

    def onChangeIcon(self):
        icon_filepath, _filter = QFileDialog.getOpenFileName(
            self, "Choose Icon", os.path.dirname(self.item["icon"])
        )
        if icon_filepath:
            icon_size = 15
            self.icon.setPixmap(
                QPixmap(icon_filepath).scaled(
                    icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            self.item["icon"] = icon_filepath

    def onChangePath(self):
        path = self.item["path"] if len(self.item["path"]) else os.path.expanduser("~")
        if self.item["type"] == "dir":
            path = QFileDialog.getExistingDirectory(self, "Choose a directory", path)
            if path:
                self.path.setText(path)
                self.item["path"] = path
        else:
            path, _filter = QFileDialog.getOpenFileName(self, "Open file", path)
            if path:
                self.path.setText(path)
                self.item["path"] = path

    def validate(self):
        return True

    def accept(self):
        if not self.validate():
            QMessageBox.critical(
                self, "Error", "\n".join(self.validation_errors), QMessageBox.Ok
            )
            return

        self.item["name"] = self.name.text()
        self.item["desc"] = self.desc.text()
        settings.writeItem(self.item)
        self.close()
