import sys
import unittest
from PyQt5.QtWidgets import (
        QApplication,
        QWidget
)
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt
from os.path import isfile, isdir, join
from droptopus import settings, config
from droptopus.widgets import FileTarget, DirTarget, CreateTarget

app = QApplication(sys.argv)

class DropTargetTest(unittest.TestCase):
    def setUp(self):
        '''Create the widgets'''
        self.widget = QWidget()
        self.create_target = self.instantiateWidget({"type":"builtin", "name": "Create Action", "path": "", "icon": join(config.ASSETS_DIR, 'plus_white.png')}, 0)
        self.dir_target = self.instantiateWidget({"type":"dir", "name": "Dir Action", "path": "/tmp", "icon": join(config.ASSETS_DIR, 'plus_white.png')}, 1)
        self.file_target = self.instantiateWidget({"type":"file", "name": "File Action", "path": "echo", "icon": join(config.ASSETS_DIR, 'plus_white.png')}, 2)

    def instantiateWidget(self, widget_info, index = None):
        '''Helper method to create the widgets'''
        widget_type = widget_info['type']
        if widget_type == 'dir':
            return DirTarget(self.widget, widget_info['type'], widget_info['name'], index, widget_info['icon'], widget_info['path'])
        elif widget_type == 'file':
            return FileTarget(self.widget, widget_info['type'], widget_info['name'], index, widget_info['icon'], widget_info['path'])
        elif widget_type == 'builtin':
            return CreateTarget(self.widget, widget_info['type'], widget_info['name'], index, widget_info['icon'], widget_info['path'])

    def test_handle_urls(self):
        '''Test URL handling'''
        urls = [
            'https://i.imgur.com/7VEHUX9.jpg',
            u'http://www.example.com/düsseldorf?neighbourhood=Lörick',
        ]
        for url in urls:
            status, dest_file = self.dir_target.handle(url)
            self.assertEqual(0, status)
            self.assertTrue(bool(isfile(dest_file)))

            status, dest_file = self.file_target.handle(url)
            self.assertEqual(0, status)

