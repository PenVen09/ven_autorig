from PySide2 import QtWidgets, QtGui, QtCore
import time

class Logger:
    def __init__(self, table=None):
        self.table = table

    def attach_table(self, table):
        self.table = table

    def log(self, message: str, level: str = "INFO"):
        row = self.table.rowCount()
        self.table.insertRow(row)
        color = {
        "INFO": "white",
        "WARNING": "orange",
        "ERROR": "red",
        "SUCCESS": "green"
        }.get(level, "white")

        ts = time.strftime("%H:%M:%S")
        time_item = QtWidgets.QTableWidgetItem(ts)
        level_item = QtWidgets.QTableWidgetItem(level)
        msg_item = QtWidgets.QTableWidgetItem(message)

        for item in (time_item, level_item, msg_item):
            item.setForeground(QtGui.QBrush(color))
            item.setFlags(QtCore.Qt.ItemIsEnabled)

        self.table.setItem(row, 0, time_item)
        self.table.setItem(row, 1, level_item)
        self.table.setItem(row, 2, msg_item)
        self.table.scrollToBottom()

logger = Logger()
