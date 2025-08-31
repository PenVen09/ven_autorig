"""
AutoRig Tool
why am i here
"""
from typing import Tuple
from itertools import zip_longest
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
from maya import cmds

from . import naming_config

comments = "This is version 1.0"

class VenAutoRig(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(VenAutoRig, self).__init__(parent)
        self.resize(500, 550)
        self.component_lists = {
            "General": {
                "Joints": {
                    "position": [(0, 0, 0)],
                    "suffix": ["root"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "Base"},
                        "component_index":{"widget":"float", "value": "0"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Left", "Right", "Center"],
                            "value": "Center"
                        },
                        "isBindJoint": {"widget": "bool", "value": True}
                    }
                },
                "FKIKChain": {
                    "position": [(0, 0, 0), (5, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "suffix": ["loc"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "FKIKChain"},
                        "component_index":{"widget":"float", "value": "0"},
                        "numJoints": {"widget": "float", "value": 3},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Left", "Right", "Center"],
                            "value": "Center"
                        },
                    }
                }
            },
            "Limbs": {
                "Shoulder" :{
                    "position": [(0, 0, 0), (5, 0, 0)],
                    "suffix": ["root", "tip"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "arm"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Left", "Right"],
                            "value": "Left"
                    },
                },
            },
                "Arm": {
                    "position": [(0, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "suffix": ["root", "elbow", "wrist"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "arm"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Left", "Right", "Center"],
                            "value": "Left"
                        }
                    }
                },
                "Leg": {
                    "position": [(0, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "suffix": ["root", "knee", "foot"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "leg"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Left", "Right", "Center"],
                            "value": "Right"
                        }
                    }
                }
            }
        }
        self.initialize_ui()

    def initialize_ui(self):
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        layout = QtWidgets.QVBoxLayout(central_widget)
        self.main_tabs = QtWidgets.QTabWidget()
        layout.addWidget(self.main_tabs)

        # --------------------------------------------------
        # Rig Tab
        rig_tab = QtWidgets.QWidget()
        rig_main_layout = QtWidgets.QVBoxLayout(rig_tab)
        rig_content_layout = QtWidgets.QHBoxLayout()
        rig_main_layout.addLayout(rig_content_layout)

        # --------------------------------------------------
        # Left side - (components)
        component_layout = QtWidgets.QVBoxLayout()

        component_list_tabs = QtWidgets.QTabWidget()
        component_layout.addWidget(component_list_tabs)

        component_tab_widget = QtWidgets.QWidget()
        tab_layout = QtWidgets.QVBoxLayout(component_tab_widget)

        self.component_tree_list = QtWidgets.QTreeWidget()
        self.component_tree_list.setHeaderHidden(True)
        font = self.component_tree_list.font()
        font.setPointSize(9)
        self.component_tree_list.setFont(font)
        self.component_tree_list.setIndentation(10)

        tab_layout.addWidget(self.component_tree_list, 1)

        # --------------------------------------------------
        utilities_layout = QtWidgets.QHBoxLayout()
        duplicate_button =QtWidgets.QPushButton("Duplicate")
        symmetry_button = QtWidgets.QPushButton("Symmetry")
        utilities_layout.addWidget(duplicate_button)
        utilities_layout.addWidget(symmetry_button)

        spawn_component_button = QtWidgets.QPushButton("Spawn Selected")
        spawn_component_button.clicked.connect(self.spawn_guides)

        #component_layout.addLayout(name_layout)
        #component_layout.addLayout(side_layout)
        component_layout.addLayout(utilities_layout)
        component_layout.addWidget(spawn_component_button)

        component_list_tabs.addTab(component_tab_widget, "Component")

        # --------------------------------------------------
        # --- Left side (templates) ---
        template_tab_widget = QtWidgets.QWidget()
        template_layout = QtWidgets.QVBoxLayout(template_tab_widget)

        component_list_tabs.addTab(template_tab_widget, "Templates")

        # --------------------------------------------------
        # --- Right side (Guide) ---
        self.guide_layout = QtWidgets.QVBoxLayout()
        group = QtWidgets.QGroupBox("Module Settings")
        group_layout = QtWidgets.QFormLayout(group)

        guide_settings_scroll = QtWidgets.QScrollArea()
        guide_settings_scroll.setWidgetResizable(True)
        group_layout.addWidget(guide_settings_scroll)

        guide_settings_container = QtWidgets.QWidget()
        guide_settings_scroll.setWidget(guide_settings_container)

        self.guide_settings_layout = QtWidgets.QVBoxLayout(guide_settings_container)
        self.guide_settings_layout.setAlignment(QtCore.Qt.AlignTop)

        guide_settings_button = QtWidgets.QPushButton("Generate Settings")

        self.guide_layout.addWidget(group)
        self.guide_layout.addWidget(guide_settings_button)
        guide_settings_button.clicked.connect(self._populate_module)

        rig_content_layout.addLayout(component_layout,1)
        rig_content_layout.addLayout(self.guide_layout,3)

        # --------------------------------------------------
        # ------debug box-----
        self.debug_box = QtWidgets.QPlainTextEdit()
        self.debug_box.setReadOnly(True)
        self.debug_box.setFixedHeight(100)
        self.debug_box.appendPlainText(__doc__)
        rig_main_layout.addWidget(self.debug_box)

        # --------------------------------------------------
        #------ build button-----
        build_layout = QtWidgets.QHBoxLayout()
        #build_guide = QtWidgets.QPushButton("Update guide")
        build_joint = QtWidgets.QPushButton("Spawn Joints")
        build_controller = QtWidgets.QPushButton("Spawn Controller")

        build_layout.addWidget(build_joint)
        build_layout.addWidget(build_controller)
        rig_main_layout.addLayout(build_layout)

        self.populate_treeview(self.component_tree_list)
        self.component_tree_list.expandAll()
        self.main_tabs.addTab(rig_tab, "Rig")

    def populate_treeview(self, tree_widget):
        self.component_widgets = {}

        for parent, children in self.component_lists.items():
            tree_item = QtWidgets.QTreeWidgetItem(tree_widget,[parent])
            tree_item.setIcon(0, QtGui.QIcon(":folder-closed.png"))

            for child, info in children.items():
                QtWidgets.QTreeWidgetItem(tree_item, [child])

    def spawn_guides(self):
        ATTR_BUILDERS = {
                        "string": self.add_string,
                        "bool": self.add_bool,
                        "enum": self.add_enum,
                        "float": self.add_float,
                        }


        tree_selection = self.component_tree_list.currentItem()
        selection = cmds.ls(selection=True)
        if tree_selection:
            selected = tree_selection.text(0)
            side = self.component_lists[tree_selection.parent().text(0)][selected]["attrs"]["comp_side"]["value"]
            suffix = self.component_lists[tree_selection.parent().text(0)][selected]["suffix"]
            base = selected
            side_index = 0
            position = self.component_lists[tree_selection.parent().text(0)][selected]["position"]

            ctx = naming_config.NamingContext(base, side, "guide", suffix[0])
            full_name = naming_config.get_unique_name(ctx)
            guide_length = len(position)

            if guide_length > 1:
                ctx.suffix = "crv"
                full_name = naming_config.get_unique_name(ctx)
                ep_curve = cmds.curve(d=1, p=position, name=full_name)
                ep_shape = self.rename_shape(ep_curve)
                cmds.setAttr(f"{ep_curve}.template", 1)
                cmds.setAttr(f"{ep_curve}.lineWidth", 1.5)


            else:
                ep_curve = None

            for ctx.index, (pos, suffix) in enumerate(zip_longest(position, suffix, fillvalue=suffix[-1])):
                """ Might need to fix how the enumerate/index work for controlPoints(if index is changeable by user)"""
                ctx.suffix = suffix
                full_name = naming_config.get_unique_name(ctx)

                if ctx.index == 0:
                    parent_node = self.create_guide_controller(False, full_name, None, pos)
                    cmds.addAttr(parent_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)


                    attributes = self.component_lists[tree_selection.parent().text(0)][selected]["attrs"]
                    for atb, item in attributes.items():
                        type = item["widget"]
                        build_fn = ATTR_BUILDERS[type]
                        build_fn(parent_node, atb, item, ctx.subindex)
                    self.rename_shape(parent_node)

                    if not selection:
                        guide_group = cmds.group(parent_node, world=True, n="guide")#Later need to add variable to name guide
                        cmds.addAttr(guide_group, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    elif len(selection) > 1:
                        cmds.warning("More than 1 selection detected")
                    else:
                        if cmds.attributeQuery("isVenGuide", node=selection[0], exists=True):
                            cmds.parent(parent_node, selection[0])
                            cmds.matchTransform(parent_node, selection[0])
                        else:
                            cmds.warning("Parent is not autorig guide")

                    if ep_curve:
                        ep_offset = cmds.group(ep_curve, parent=parent_node, n=f"{ep_curve}_offset",r=True)
                        cmds.connectAttr(f"{parent_node}.worldInverseMatrix", f"{ep_offset}.offsetParentMatrix")

                        #Probably will make this below as method soon
                        world_space = cmds.createNode("decomposeMatrix", name=f"{parent_node}" + "_ws")
                        cmds.connectAttr(f"{parent_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                        cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{ctx.index}]")
                else:
                    child_node = self.create_guide_controller(True, full_name, parent_node, pos)
                    cmds.addAttr(child_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)

                    #Probably will make this below as method soon
                    world_space = cmds.createNode("decomposeMatrix", name=f"{parent_node}" + "_ws")
                    cmds.connectAttr(f"{child_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{ctx.index}]")

                    parent_node = child_node

    def spawn_joint(self):
        '''"attrs": {
                        "rigType": {"widget": "lineedit", "value": "Base"},
                        "comp_side": {
                            "widget": "dropdown",
                            "options": ["Left", "Right", "Center"],
                            "value": "Center"
                        },
                        "isBindJoint": {"widget": "checkbox", "value": True}}'''
        guides = cmds.ls("*_root", type="transform")
        if guides:
            for guide in guides:
                pass
        pass

    def create_guide_controller(self, isSphere=True, name=None, parent=None, pos=(0,0,0), r=0.5):
        if not isSphere:
            node = cmds.curve(
                d=1,
                p=[(-r, -r, -r), (-r, -r, r), (-r, r, r), (-r, r, -r), (-r, -r, -r),
                    (r, -r, -r), (r, -r, r), (-r, -r, r), (r, -r, r),
                    (r, r, r), (-r, r, r), (r, r, r),
                    (r, r, -r), (-r, r, -r), (r, r, -r), (r, -r, -r),
                   ],
                k=list(range(16)),
                name=name
            )
            cmds.setAttr(node + ".overrideEnabled", 1)
            cmds.setAttr(node + ".overrideColor", 13)

        else:
            node = cmds.curve(
                d=1,
                p=[
                    (r, 0, 0), (0, r, 0), (-r, 0, 0), (0, -r, 0), (r, 0, 0),
                    (r, 0, 0), (0, 0, r), (-r, 0, 0), (0, 0, -r), (r, 0, 0),
                    (0, r, 0), (0, 0, r), (0, -r, 0), (0, 0, -r), (0, r, 0),
                ],
                name=name
            )
            cmds.setAttr(node + ".overrideEnabled", 1)
            cmds.setAttr(node + ".overrideColor", 17)
        if parent:
            cmds.parent(node, parent)
        cmds.xform(node, t=pos)
        self.rename_shape(node)

        return node

    def rename_shape(self, node):
        """Rename the first shape under a transform to match the transform name"""
        shapes = cmds.listRelatives(node, shapes=True, fullPath=False)
        if shapes:
            new_name = node + "Shape"
            return cmds.rename(shapes[0], new_name)
        return None

    def add_string(self, obj, name, type, *args):
        cmds.addAttr(obj, ln=name, dt="string")
        cmds.setAttr(f"{obj}.{name}", type.get("value", ""), type="string")

    def add_bool(self,obj, name, type, *args):
        cmds.addAttr(obj, ln=name, at="bool", dv=int(type.get("value", False)))
        cmds.setAttr(f"{obj}.{name}", e=True, k=True)

    def add_enum(self,obj, name, type, *args):
        opts = ":".join(type.get("options", []))
        cmds.addAttr(obj, ln=name, at="enum", en=opts)
        if "value" in type:
            idx = type["options"].index(type["value"])
            cmds.setAttr(f"{obj}.{name}", idx)

    def add_float(self, obj, name, type, index, *args):
        """ Maybe will optimize the override stuff later"""
        OVERRIDES = {
                    "component_index": index,
                    }
        value = float(type.get("value", 0.0))
        value = OVERRIDES.get(name, value)
        cmds.addAttr(obj, ln=name, at="float", dv=value)
        cmds.setAttr(f"{obj}.{name}", e=True, k=True)

    def _separator(self):
        """ Spawn separator based on this style """
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("margin-top: 5px; margin-bottom: 5px;")
        return line

    def _collapsible_button(self, label_text, isVisible=True) -> Tuple[QWidget, QPushButton, QVBoxLayout]:
        """ Spawn a collapsible button widget, return some widget that can be parented under other layout """
        section_widget = QtWidgets.QWidget()
        section_layout = QtWidgets.QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)

        toggle_button = QtWidgets.QToolButton(checkable=True, checked=False)
        toggle_button.setText(label_text)
        toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        toggle_button.setArrowType(QtCore.Qt.DownArrow)

        if not isVisible:
            color = "transparent"
            button_container = QtWidgets.QWidget()
            button_container_layout = QtWidgets.QHBoxLayout(button_container)
            button_container_layout.setContentsMargins(0, 0, 0, 0)
            button_container_layout.setSpacing(5)

            button_container_layout.addWidget(toggle_button)
            button_container_layout.addWidget(self._separator())

            section_layout.addWidget(button_container)

        else:
            color = "#666666"
            toggle_button.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
            section_layout.addWidget(toggle_button)

        toggle_button.setStyleSheet(f"""
            QToolButton {{
                background-color: {color};
                border: none;
                padding: 5px;
                border-radius: 5px;
                color: white;
            }}
        """)

        content_widget = QtWidgets.QWidget()
        content_layout = QtWidgets.QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 0, 5, 5)

        section_layout.addWidget(content_widget)

        toggle_button.clicked.connect(lambda: self._collapsible_on_pressed(toggle_button, content_widget))

        return section_widget, toggle_button, content_layout

    def _collapsible_on_pressed(self, buttons, collapse_widget) -> None:
        """ Complement _collapsible_button """
        checked = buttons.isChecked()
        buttons.setArrowType(QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow)
        collapse_widget.setVisible(not checked)

    def _populate_module(self):
        self._clear_layout(self.guide_settings_layout)
        widget, button, layout = self._collapsible_button("Test")
        self.guide_settings_layout.addWidget(widget)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

def get_maya_window():
    """ Return Maya main window as QMainWindow."""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

def show_ui():
    global win
    try:
        win.close()
    except:
        pass

    win = VenAutoRig(get_maya_window())
    win.show()


show_ui()
