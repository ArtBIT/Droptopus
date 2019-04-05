# coding=utf-8
"""
This is module for testing the most basic functionality of Droptopus
"""
import sys
import unittest
from os.path import isfile, join
from PyQt5.QtWidgets import QWidget, QApplication
from droptopus.widgets import FileTarget, DirTarget, CreateTarget
from droptopus import config


class TestDropTarget(unittest.TestCase):
    """Test for Droptopus URL parsing"""

    def setUp(self):
        """Create the widgets"""
        app = QApplication(sys.argv)
        self.widget = QWidget()
        self.create_target = self.instantiate_widget(
            {
                "desc": "",
                "type": "builtin",
                "name": "Create Action",
                "path": "",
                "icon": join(config.ASSETS_DIR, "plus_white.png"),
                "index": 0,
            }
        )
        self.dir_target = self.instantiate_widget(
            {
                "desc": "",
                "type": "dir",
                "name": "Dir Action",
                "path": "/tmp",
                "icon": join(config.ASSETS_DIR, "plus_white.png"),
                "index": 1,
            }
        )
        self.file_target = self.instantiate_widget(
            {
                "desc": "",
                "type": "file",
                "name": "File Action",
                "path": "echo",
                "icon": join(config.ASSETS_DIR, "plus_white.png"),
                "index": 2,
            }
        )

    def instantiate_widget(self, conf):
        """Helper method to create the widgets"""
        widget_type = conf["type"]

        if widget_type == "dir":
            return DirTarget(self.widget, conf)

        if widget_type == "file":
            return FileTarget(self.widget, conf)

        if widget_type == "builtin":
            return CreateTarget(self.widget, conf)

        return None

    def test_handle_urls(self):
        """Test URL handling"""
        urls = [
            "https://i.imgur.com/7VEHUX9.jpg",
            u"http://www.example.com/düsseldorf?neighbourhood=Lörick",
        ]
        for url in urls:
            status, dest_file = self.dir_target.handle(url)
            self.assertEqual(0, status)
            self.assertTrue(bool(isfile(dest_file)))

            status, dest_file = self.file_target.handle(url)
            self.assertEqual(0, status)

if __name__ == '__main__':
    unittest.main()
