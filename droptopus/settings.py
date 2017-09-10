import config
from PyQt4 import QtGui, QtCore 
QtCore.QCoreApplication.setOrganizationName(config.ORG_NAME);
QtCore.QCoreApplication.setOrganizationDomain(config.ORG_DOMAIN);
QtCore.QCoreApplication.setApplicationName(config.APP_NAME);

settings = QtCore.QSettings()
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
    s.endArray();

def readItems():
    s = settings
    size = s.beginReadArray("items");
    items = []
    for i in range(size):
        s.setArrayIndex(i);
        items.append({
            "index": i,
            "type": str(s.value("type").toString()),
            "name": str(s.value("name").toString()),
            "path": str(s.value("path").toString()),
            "icon": str(s.value("icon").toString())
        })
    s.endArray();
    return items

def readItem(index):
    items = readItems()
    return items[index]

def writeItem(item):
    items = readItems()
    items[item['index']] = item
    writeItems(items)

def pushItem(item):
    items = readItems()
    items.append(item)
    writeItems(items)
    return len(items) - 1

def removeItem(index):
    items = readItems()
    del items[index]
    writeItems(items)
