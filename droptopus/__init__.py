"""
Droptopus
description: Drag'n'drop router that routes the dropped object to the specified action.
author: Djordje Ungar
website: https://github.com/ArtBIT/Droptopus
"""

import sys
from droptopus.app import App

def main():
    app = App()
    sys.exit(app.exec_())
