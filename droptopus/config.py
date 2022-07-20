import os
from droptopus.__version__ import __version__

ORG_NAME = "B1T"
ORG_DOMAIN = "bit.co.rs"
APP_NAME = "Droptopus"
APP_DIR = os.path.dirname(os.path.realpath(os.path.join(__file__)))
ASSETS_DIR = os.path.join(APP_DIR, "assets")
VERSION = __version__
