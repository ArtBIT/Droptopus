from droptopus import config
from PyQt5.QtCore import QCoreApplication, QSettings

QCoreApplication.setOrganizationName(config.ORG_NAME);
QCoreApplication.setOrganizationDomain(config.ORG_DOMAIN);
QCoreApplication.setApplicationName(config.APP_NAME);

settings = QSettings()
def writeItems(items):
    s = settings
    s.remove("items")
    size = len(items)
    s.beginWriteArray("items", size)
    for i in range(size):
        s.setArrayIndex(i);
        value = items[i]
        s.setValue("type", value["type"])
        s.setValue("name", value["name"])
        s.setValue("path", value["path"])
        s.setValue("icon", value["icon"])
        s.setValue("desc", value["desc"])
    s.endArray();

def readItems():
    s = settings
    size = s.beginReadArray("items");
    items = []
    for i in range(size):
        s.setArrayIndex(i);
        items.append({
            "index": i,
            "type": str(s.value("type")),
            "name": str(s.value("name")),
            "path": str(s.value("path")),
            "icon": str(s.value("icon")),
            "desc": str(s.value("desc"))
        })
    s.endArray();
    return items

def readItem(index):
    items = readItems()
    return items[index]

def writeItem(item):
    try:
        index = int(item['index'])
        items = readItems()
        items[item['index']] = item
        writeItems(items)
        return True
    except ValueError:
        return pushItem(item)
    return False

def pushItem(item):
    items = readItems()
    items.append(item)
    writeItems(items)
    return len(items) - 1

def removeItem(index):
    items = readItems()
    del items[index]
    writeItems(items)
