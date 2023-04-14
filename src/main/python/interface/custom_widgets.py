from PySide2 import QtWidgets, QtCore


class CustomListWidget(QtWidgets.QListWidget):
    """Custom list widget with signal count_changed"""
    count_changed = QtCore.Signal()

    def __init__(self):
        super().__init__()

    def addItem(self, item):
        super().addItem(item)
        self.count_changed.emit()

    def removeItemWidget(self, item):
        super().removeItemWidget(item)
        self.count_changed.emit()

    def clear(self):
        super().clear()
        self.count_changed.emit()
