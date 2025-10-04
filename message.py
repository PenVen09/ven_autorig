'''
Class main.ui
'''
from typing import Tuple
import time
from itertools import zip_longest
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
import maya.OpenMayaUI as omui
from maya import cmds
from shiboken2 import wrapInstance

class qtClassMain_CR(QtWidgets.QWidget):
    def __init__(self, parent_=None):
        global _qtMainNameWidget_
        
        super(qtClassMain_CR, self).__init__(parent=parent_)
        self.setWindowFlags(QtCore.Qt.Window)

        qtMainLayout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("ikannnn")
        qtMainLayout.addWidget(label)

def qtOpenMainWindow_CR():
    global _qtMainWindowsCR_
    
    _qtMainWindowsCR_ = None
    
    if QtWidgets.QApplication.instance():
        for _win in (QtWidgets.QApplication.allWindows()):
            if '_qtMainWindowsCR_' in _win.objectName():
                _win.destroy()

    _qtMainWindowUt = omui.MQtUtil.mainWindow()
    _qtMainWindowWd = wrapInstance(int(_qtMainWindowUt), QtWidgets.QWidget)
    qtClassMain_CR._qtMainWindowsCR_ = qtClassMain_CR(parent_=_qtMainWindowWd)
    qtClassMain_CR._qtMainWindowsCR_.setObjectName('_qtMainWindowsCR_')
    qtClassMain_CR._qtMainWindowsCR_.setWindowTitle('Maya UI Template')
    qtClassMain_CR._qtMainWindowsCR_.show()
    
    _qtMainWindowsCR_ = qtClassMain_CR._qtMainWindowsCR_
