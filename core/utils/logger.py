from PySide2 import QtWidgets, QtGui, QtCore
import time

class Logger:
    def __init__(self, table=None):
        self._table = table

    def attach_table(self, table):
        self._table = table

    def log(self, message: str, level: str = "INFO"):
        row = self._table.rowCount()
        self._table.insertRow(row)
        color = {
        "INFO": "white",
        "WARNING": "orange",
        "ERROR": "red",
        "SUCCESS": "green"
        }.get(level, "white")

        ts = time.strftime("%H:%M:%S")
        time_item = QtWidgets.QTableWidgetItem(f'[{ts}]')
        level_item = QtWidgets.QTableWidgetItem(level)
        msg_item = QtWidgets.QTableWidgetItem(message)

        time_item.setForeground(QtGui.QBrush(QtGui.QColor("grey")))
        time_item.setFlags(QtCore.Qt.ItemIsEnabled)

        for item in (level_item, msg_item):
            item.setForeground(QtGui.QBrush(QtGui.QColor(color)))
            item.setFlags(QtCore.Qt.ItemIsEnabled)

        self._table.setItem(row, 0, time_item)
        self._table.setItem(row, 1, level_item)
        self._table.setItem(row, 2, msg_item)
        self._table.scrollToBottom()

