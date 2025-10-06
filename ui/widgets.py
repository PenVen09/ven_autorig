"""Use later?, idk feel not so important cause only 1 window"""
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from maya import cmds

from ..core.utils import math

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



def spawn_section_window(guide_length, position_offset, rotation_offset):
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle("Guide Properties")
    dialog.resize(100, 100)
    main_layout = QtWidgets.QVBoxLayout(dialog)


    sub_layout = QtWidgets.QHBoxLayout()
    sub_label = QtWidgets.QLabel("Subdividsion: ")
    sub_spin = QtWidgets.QSpinBox()

    sub_spin.setValue(guide_length)

    sub_layout.addWidget(sub_label)
    sub_layout.addWidget(sub_spin)
    main_layout.addLayout(sub_layout)


    rotate_layout = QtWidgets.QHBoxLayout()
    rotate_label = QtWidgets.QLabel("Rotate Offset: ")
    rotate_spin = QtWidgets.QDoubleSpinBox()
    rotate_spin.setValue(rotation_offset[1][0])#placeholder
    rotate_layout.addWidget(rotate_label)
    rotate_layout.addWidget(rotate_spin)
    main_layout.addLayout(rotate_layout)

    spacing_layout = QtWidgets.QHBoxLayout()
    spacing_label = QtWidgets.QLabel("Spacing: ")
    spacing_spin = QtWidgets.QDoubleSpinBox()

    spacing_spin.setValue(position_offset[1][0])#placeholder

    spacing_layout.addWidget(spacing_label)
    spacing_layout.addWidget(spacing_spin)
    main_layout.addLayout(spacing_layout)

    button_layout = QtWidgets.QHBoxLayout()
    accept_btn = QtWidgets.QPushButton("Accept")
    accept_btn.clicked.connect(dialog.accept)
    cancel_btn =QtWidgets.QPushButton("Cancel")
    cancel_btn.clicked.connect(dialog.reject)
    button_layout.addWidget(accept_btn)
    button_layout.addWidget(cancel_btn)

    main_layout.addLayout(button_layout)

    result = dialog.exec_()


    if result == QtWidgets.QDialog.Accepted:
        position = []
        rotation = []
        axis = math.axis_to_vector("z+")
        position.append(position_offset[0])
        rotation.append(rotation_offset[0])


        for i in range(sub_spin.value() - 1):
            x = axis[0] * spacing_spin.value()
            y = axis[1] * spacing_spin.value()
            z = axis[2] * spacing_spin.value()
            position.append((x,y,z))
            rotation.append((0,0,0)) #later fix
        return position, rotation
    else:
        return False
