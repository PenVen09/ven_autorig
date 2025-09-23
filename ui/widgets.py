"""Use later?, idk feel not so important cause only 1 window"""
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from maya import cmds

class QTWidgetFactory:
    def __init__(self):
        self.BUILDERS = {
            "double": self.build_float,
            "float": self.build_float,
            "long": self.build_int,
            "short": self.build_int,
            "byte": self.build_int,
            "int": self.build_int,
            "bool": self.build_bool,
            "enum": self.build_enum,
            "string": self.build_string,
        }

    def build_enum(self, wrapper):
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(5, 5, 5, 5)
        container = QtWidgets.QWidget()
        container.setLayout(row)
        label = QtWidgets.QLabel(f"{wrapper.attr} :")
        row.addWidget(label)
        dropdown = QtWidgets.QComboBox()
        enum_names = cmds.attributeQuery(wrapper.attr, node=wrapper.node, listEnum=True)[0].split(":")

        for enum in enum_names:
            dropdown.addItem(enum)


        dropdown.setCurrentIndex(wrapper.get()-1)

        row.addWidget(dropdown)

        return container

    def build_float(self, wrapper):
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(5, 5, 5, 5)
        container = QtWidgets.QWidget()
        container.setLayout(row)
        label = QtWidgets.QLabel(f"{wrapper.attr} :")
        row.addWidget(label)

        spin = QtWidgets.QDoubleSpinBox()
        spin.setValue(wrapper.get())
        spin.valueChanged.connect(lambda val, w=wrapper: w.set(val))
        row.addWidget(spin)

        return container

    def build_int(self, wrapper):
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(5, 5, 5, 5)
        container = QtWidgets.QWidget()
        container.setLayout(row)
        label = QtWidgets.QLabel(f"{wrapper.attr} :")
        row.addWidget(label)

        spin = QtWidgets.QSpinBox()
        spin.setMaximumWidth(50)
        spin.setValue(wrapper.get())
        spin.valueChanged.connect(lambda val, w=wrapper: w.set(val))
        row.addWidget(spin)

        return container

    def build_bool(self, wrapper):
        check = QtWidgets.QCheckBox()
        check.setChecked(wrapper.get())
        check.stateChanged.connect(lambda state, w=wrapper: w.set(bool(state)))
        return check

    def build_string(self, wrapper):
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(5, 5, 5, 5)
        container = QtWidgets.QWidget()
        container.setLayout(row)
        label = QtWidgets.QLabel(f"{wrapper.attr} :")
        row.addWidget(label)

        field = QtWidgets.QLineEdit(str(wrapper.get()))
        field.editingFinished.connect(lambda f=field, w=wrapper: w.set(f.text()))
        row.addWidget(field)
        return container


class AttrWrapper:
    def __init__(self, node, attr):
        self.node = node
        self.attr = attr
        self.full_attr = f"{node}.{attr}"
        self.type = cmds.getAttr(self.full_attr, type=True)

    def get(self):
        return cmds.getAttr(self.full_attr)

    def set(self, value):
        try:
            cmds.setAttr(self.full_attr, value)
        except:
            cmds.warning("cant")


