import re
import os
from os.path import isfile, isdir, join
import sys
import re
import subprocess
import unicodedata
from urllib.parse import urlparse, unquote
from PyQt5.QtWidgets import QApplication

re_url = re.compile(
    r"^(?:(?:http|ftp)s?://)?"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = str(unicodedata.normalize("NFKD", value).encode("ascii", "ignore"))
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value


# Remove all items from the layout
def clearLayout(layout):
    if layout != None:
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())


def propagateEvent(self, evt):
    # QEvent.accepted is True by default
    evt.setAccepted(False)
    app = QApplication.instance()
    target = self
    while target:
        app.sendEvent(target, evt)
        if not evt.isAccepted():
            if hasattr(target, "parent"):
                target = target.parent()
        else:
            target = None
    return evt.isAccepted()

class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def osOpen(target):
    if sys.platform.startswith("darwin"):
        subprocess.call(("open", target))
    elif os.name == "nt":
        os.startfile(target)
    elif os.name == "posix":
        subprocess.call(("xdg-open", target))

def getFilePath(context):
    return unquote(urlparse(context.rstrip()).path)

def isFile(context):
    filecontext = getFilePath(context)
    logging.info("isFile: %s? %s", filecontext, str(isfile(filecontext)))
    return isfile(filecontext)

def isDir(context):
    return isdir(context)

def isUrl(context):
    return re_url.match(context)

def subprocessCall(args):
    cmd = args[0:1]
    filepath = args[1:2]
    ret = 0

    try:
        ret = subprocess.check_call(args)
    except subprocess.CalledProcessError:
        raise Exception("The subprocess failed for the following command " + " ".join(args))
    except OSError:
        raise Exception("Could not find executable " + cmd)

    return ret, filepath

