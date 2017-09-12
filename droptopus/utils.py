import re
import unicodedata
from PyQt5.QtWidgets import QApplication

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    value = unicodedata.normalize('NFKD', unicode(value)).encode('ascii', 'ignore')
    value = str(re.sub('[^\w\s-]', '', value).strip().lower(), 'utf-8')
    value = str(re.sub('[-\s]+', '-', value), 'utf-8')
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
    target = self.parent()
    while target:
        app.sendEvent(target, evt)
        if not evt.isAccepted():
            if hasattr(target, 'parent'):
                target = target.parent()
        else:
            target = None
    return evt.isAccepted()

