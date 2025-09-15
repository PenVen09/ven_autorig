"""
AutoRig Tool
why am i here
to do:
- better UI D:
- guide have rotation value and better placement
- rotation order
- arrow pins
- Convert selected joints to guides
- orient tools(aim, etc)
- Connect to controller script?
- animation or game rig checkbox
- unreal/unity based naming convention changer
"""
from typing import Tuple
from itertools import zip_longest
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
from maya import cmds

from . import naming_config

comments = "This is version 1.0"

class VenAutoRig(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(VenAutoRig, self).__init__(parent)
        self.setMinimumWidth(500)
        self.component_lists = {
            "General": {
                "Joints": {
                    "position": [(0, 0, 0)],
                    "rotation": [(0, 0, 0)],
                    "suffix": ["root"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "Base"},
                        "component_index": {"widget": "float", "value": "0"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Center"
                        },
                        "isBindJoint": {"widget": "bool", "value": True}
                    }
                },
                "FKIKChain": {
                    "position": [(0, 0, 0), (5, 0, 0), (5, 0, 0), (5, 0, 0)],
                    "rotation": [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["loc"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "FKIKChain"},
                        "component_index": {"widget": "float", "value": "0"},
                        "numJoints": {"widget": "float", "value": 3},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Center"
                        },
                    }
                }
            },
            "Limbs": {
                "Shoulder": {
                    "position": [(4, 143, 3), (20, 0, 0)],
                    "rotation": [(0, 12, 0), (0, 0, 0)],
                    "suffix": ["shoulder", "tip"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "arm"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                    },
                },
            },
                "Arm": {
                    "position": [(23.563, 143, -1.158), (0, 0, -6.948), (33.881, 0, 7.7)],
                    "rotation": [(0, 0, -35), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["upperarm", "elbow", "wrist"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "arm"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                        }
                    }
                },
                "Leg": {
                    "position": [(22.495, 75.582, 0), (0, 0, 14.255), (64, 0, -10.644)],
                    "rotation": [(0, 0, -90), (0, 0, 0), (0, 0, 0)],
                    "suffix": ["hips", "knee", "ankle"],
                    "attrs": {
                        "rigType": {"widget": "string", "value": "leg"},
                        "comp_side": {
                            "widget": "enum",
                            "options": ["Right", "Center", "Left"],
                            "value": "Left"
                        }
                    }
                },
                "Foot": {



                }
            }
        }
        self.shapes_lists = {
            "one_arrow": [[4.902264934679079e-16, 0.0, 4.003003101051036], [-1.6012012326718832, 0.0, 2.401801868379153],
                          [-0.8006006163359415, 0.0, 2.4018018683791524], [-0.8006006163359417, 0.0, 1.93713276530616e-08],
                          [0.8006006163359417, 0.0, 1.93713276530616e-08], [0.8006006163359419, 0.0, 2.4018018683791524],
                          [1.6012012326718836, 0.0, 2.4018018683791524], [4.902264934679079e-16, 0.0, 4.003003101051036]]
        }
        self.section_widgets = {}
        self.initialize_ui()

    def initialize_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)


        self.toolbar = QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(24, 24))
        main_layout.addWidget(self.toolbar)

        self.content_area = QtWidgets.QVBoxLayout()
        self.content_area.setContentsMargins(5,5,5,5)
        main_layout.addLayout(self.content_area)
        self.action_main = self.add_toolbar_button("Main", self.build_main_box, default_open=True, icon_name="joint.svg")
        self.action_debug = self.add_toolbar_button("Debug", self.build_debug_box, default_open=True, icon_name="openScript.png")
        self.add_toolbar_button("Three", self.build_section_three)

    def add_toolbar_button(self, name, builder_func, default_open=False, icon_name=None):
        if icon_name:
            icon = QtGui.QIcon(f":/{icon_name}")
        else:
            icon = QtGui.QIcon()

        action = self.toolbar.addAction(icon, name)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.toolbar.setStyleSheet("""
        QToolButton {
            background: none;
            border: none;
        }
        QToolButton:pressed {
            background: none;
        }
        QToolButton:focus {
            outline: none;
        }
        """)

        action.setCheckable(True)
        action.toggled.connect(
            lambda checked, f=builder_func, a=action: self.toggle_section(checked, f, a)
        )

        if default_open:
            action.setChecked(True)

        return action

    def toggle_section(self, checked, builder_func, action):
        if checked:
            widget = builder_func()
            widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

            self.section_widgets[action] = widget
            self.content_area.addWidget(widget, alignment=QtCore.Qt.AlignTop)
        else:
            widget = self.section_widgets.pop(action, None)
            if widget:
                widget.setParent(None)

        self.adjustSize()

    def build_main_box(self):
        w = QtWidgets.QGroupBox("Build")
        w.setMinimumSize(500,450)
        l = QtWidgets.QVBoxLayout(w)

        rig_tab = QtWidgets.QWidget()
        content_area  = QtWidgets.QVBoxLayout(rig_tab)

        rig_content_layout = QtWidgets.QHBoxLayout()
        content_area.addLayout(rig_content_layout)
        l.addWidget(rig_tab)

        # --------------------------------------------------
        # Left side - (components)
        component_layout = QtWidgets.QVBoxLayout()

        component_list_tabs = QtWidgets.QTabWidget()


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
        '''
        side_layout = QtWidgets.QHBoxLayout()
        self.sideCheck = QtWidgets.QCheckBox()
        self.sideCheck.setChecked(False)
        side_layout.addWidget(self.sideCheck)

        self.sideRadioGrp = QtWidgets.QButtonGroup()

        for i, text in enumerate(["Right", "Center", "Left"]):
            rb = QtWidgets.QRadioButton(text)
            side_layout.addWidget(rb)
            self.sideRadioGrp.addButton(rb, i)
        self.sideRadioGrp.buttons()[1].setChecked(True)
        self.sideCheck.toggled.connect(lambda state: self._toggleRadio(self.sideRadioGrp, state))
        self._toggleRadio(self.sideRadioGrp, False)
        '''
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

        component_layout.addWidget(spawn_component_button)
        component_layout.addLayout(utilities_layout)
        component_layout.addWidget(component_list_tabs)
        component_list_tabs.addTab(component_tab_widget, "Component")

        # --------------------------------------------------
        # --- Left side (templates) ---
        '''
        template_tab_widget = QtWidgets.QWidget()
        template_layout = QtWidgets.QVBoxLayout(template_tab_widget)

        component_list_tabs.addTab(template_tab_widget, "Templates")
        '''
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


        self.guide_layout.addWidget(guide_settings_button)
        self.guide_layout.addWidget(group)
        guide_settings_button.clicked.connect(self._populate_module)

        rig_content_layout.addLayout(component_layout,1)
        rig_content_layout.addLayout(self.guide_layout,3)

        #------ build button-----
        build_layout = QtWidgets.QHBoxLayout()
        #build_guide = QtWidgets.QPushButton("Update guide")
        build_selected = QtWidgets.QPushButton("Guides")
        build_selected.clicked.connect(lambda: self.spawn_joint(all=False))
        build_joint = QtWidgets.QPushButton("Joints")
        build_joint.clicked.connect(lambda: self.spawn_joint(all=True))
        build_controller = QtWidgets.QPushButton("Controller")

        build_layout.addWidget(build_selected)
        build_layout.addWidget(build_joint)
        build_layout.addWidget(build_controller)
        content_area.addLayout(build_layout)
        self.populate_treeview(self.component_tree_list)
        self.component_tree_list.expandAll()

        return w

    def build_debug_box(self):
        w = QtWidgets.QGroupBox("Debug")
        w.setMinimumSize(500,130)
        l = QtWidgets.QVBoxLayout(w)
        self.debug_box = QtWidgets.QPlainTextEdit()
        self.debug_box.setReadOnly(True)
        self.debug_box.setFixedHeight(100)
        self.debug_box.appendPlainText(__doc__)
        l.addWidget(self.debug_box)
        return w

    def build_section_three(self):
        w = QtWidgets.QGroupBox("Section Three")
        l = QtWidgets.QVBoxLayout(w)
        l.addWidget(QtWidgets.QLabel("Content of Section THREE"))
        l.addWidget(QtWidgets.QPushButton("Button C"))
        return w


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

            self.useSide = None#self.sideCheck.isChecked()
            side = self.component_lists[tree_selection.parent().text(0)][selected]["attrs"]["comp_side"]["value"]
            if self.useSide:
                side = self.sideRadioGrp.checkedButton().text()


            suffix = self.component_lists[tree_selection.parent().text(0)][selected]["suffix"]
            base = selected
            side_index = 0
            position = self.component_lists[tree_selection.parent().text(0)][selected]["position"]
            rotation = self.component_lists[tree_selection.parent().text(0)][selected]["rotation"]
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
            nodes = []

            for ctx.index, (pos, rot, suffix) in enumerate(zip_longest(position, rotation, suffix, fillvalue=suffix[-1])):
                """ Might need to fix how the enumerate/index work for controlPoints(if index is changeable by user)"""
                ctx.suffix = suffix
                full_name = naming_config.get_unique_name(ctx)
                if ctx.index == 0:
                    parent_node = self.create_guide_controller(True, full_name, None, pos, rot)

                    ctx.suffix = "root"
                    full_name = naming_config.get_unique_name(ctx)
                    root_node = self.create_guide_controller(False, full_name, None, pos, rot, r=0.8)

                    cmds.parent(parent_node, root_node)
                    nodes.append(parent_node)
                    cmds.addAttr(root_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    cmds.addAttr(parent_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    attributes = self.component_lists[tree_selection.parent().text(0)][selected]["attrs"]
                    for atb, item in attributes.items():
                        type = item["widget"]
                        build_fn = ATTR_BUILDERS[type]
                        build_fn(root_node, atb, item, index=ctx.subindex, side=side)

                    self.rename_shape(root_node)

                    if not selection:
                        guide_group = cmds.group(empty=True, world=True, n="guide")#Later need to add variable to name guide
                        cmds.parent(root_node, guide_group, absolute=True)
                        cmds.addAttr(guide_group, longName="isGuide", attributeType="bool", defaultValue=1, keyable=True)
                        cmds.addAttr(guide_group, longName="jointOrder", dt="string")
                        cmds.setAttr(f"{guide_group}.jointOrder", str(naming_config.NAMING_PREFS["order"]), type="string")
                        cmds.addAttr(guide_group, longName="ctrlOrder", dt="string")
                        cmds.setAttr(f"{guide_group}.ctrlOrder", str(naming_config.NAMING_PREFS["order"]), type="string")
                    elif len(selection) > 1:
                        cmds.warning("More than 1 selection detected")
                    else:
                        if cmds.attributeQuery("isVenGuide", node=selection[0], exists=True):
                            cmds.matchTransform(root_node, selection[0], pos=True, rot=False, scl=False)
                            cmds.parent(root_node, selection[0])
                        elif cmds.attributeQuery("isGuide", node=selection[0], exists=True):
                            cmds.parent(root_node, selection[0])

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
                    child_node = self.create_guide_controller(True, full_name, parent_node, pos, rot)
                    nodes.append(child_node)

                    cmds.addAttr(child_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)

                    #Probably will make this below as method soon
                    world_space = cmds.createNode("decomposeMatrix", name=f"{parent_node}" + "_ws")
                    cmds.connectAttr(f"{child_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{ctx.index}]")

                    parent_node = child_node

            if base == "Arm" or base == "Leg":
                primary_vec = self.axis_to_vector("x+")
                up_vec = self.axis_to_vector("y+")
                root = nodes[0]
                elbow = nodes[1]
                wrist = nodes[2]
                '''
                #auto parent for non IK Planar?
                if len(nodes)>3:
                    for node in nodes[3:]:
                        print(nodes[2])
                        print(node)
                        #cmds.parent(node, nodes[2])
                        
                '''

                for node in nodes[1:]:
                    cmds.parent(node, root_node)
                base_name = naming_config.parse_and_build(nodes[0], new_order=("base", "side", "index"))

                # --- Spawn pole vector arrow ---
                ctx.index = 0 #revisit later
                ctx.suffix = "angle"
                full_name = naming_config.get_unique_name(ctx)
                angle_controller = cmds.curve(
                    d=1,
                    p=self.shapes_lists["one_arrow"],
                    n=full_name
                )
                cmds.matchTransform(angle_controller, root_node)
                cmds.parent(angle_controller, root)
                ctx.suffix = "pv_dir"
                full_name = naming_config.get_unique_name(ctx)
                pv_controller = cmds.curve(
                    d=1,
                    p=self.shapes_lists["one_arrow"],
                    n=full_name
                )
                cmds.addAttr(pv_controller, longName="elbowRatio", attributeType="float", defaultValue=0.5, keyable=True)


                # --- Root aim at Elbow --- ##NEED TO DO SMTH SO CAN EASILY CHANGE AXIS
                cmds.aimConstraint(wrist, root, aimVector=primary_vec, upVector=self.axis_to_vector("z+"), worldUpType="object", worldUpObject=elbow)
                cmds.aimConstraint(wrist, elbow, aimVector=primary_vec, upVector=self.axis_to_vector("y+"), worldUpType="objectrotation", worldUpObject=wrist)
                
                # --- Elbow between two points ---
                elbow_offset = cmds.group(empty=True, p=root_node, n=f"{elbow}_offset")
                #cmds.matchTransform(elbow_offset, elbow)
                cmds.parent(elbow, elbow_offset, a=True)

                bc = cmds.createNode("blendColors", name=f"BC_{base_name}")
                cmds.connectAttr(root + ".translate", bc + ".color1", f=True)
                cmds.connectAttr(wrist + ".translate", bc + ".color2", f=True)
                cmds.connectAttr(pv_controller + ".elbowRatio", bc + ".blender", f=True)

                # Drive elbow pos
                cmds.connectAttr(bc + ".output", elbow_offset + ".translate", f=True)



                # --- Pole Vector Position ---
                '''
                def build_auto_pv_nodes(root, elbow, wrist, axis=(0,0,1), offset_len=-10.0):
                    prefix = "{}_pv".format(elbow)

                    # --- Decompose matrices to get world positions ---
                    dm_root = cmds.createNode("decomposeMatrix", name=prefix + "_root_DM")
                    cmds.connectAttr(root + ".worldMatrix[0]", dm_root + ".inputMatrix", f=True)

                    dm_elbow = cmds.createNode("decomposeMatrix", name=prefix + "_elbow_DM")
                    cmds.connectAttr(elbow + ".worldMatrix[0]", dm_elbow + ".inputMatrix", f=True)

                    dm_wrist = cmds.createNode("decomposeMatrix", name=prefix + "_wrist_DM")
                    cmds.connectAttr(wrist + ".worldMatrix[0]", dm_wrist + ".inputMatrix", f=True)

                    # --- v_rm = mid - root ---
                    v_rm = cmds.createNode("plusMinusAverage", name=prefix + "_v_rm_PMA")
                    cmds.setAttr(v_rm + ".operation", 2)  # subtract
                    cmds.connectAttr(dm_elbow + ".outputTranslate", v_rm + ".input3D[0]", f=True)
                    cmds.connectAttr(dm_root + ".outputTranslate",  v_rm + ".input3D[1]", f=True)

                    # --- v_re = end - root ---
                    v_re = cmds.createNode("plusMinusAverage", name=prefix + "_v_re_PMA")
                    cmds.setAttr(v_re + ".operation", 2)
                    cmds.connectAttr(dm_wrist + ".outputTranslate", v_re + ".input3D[0]", f=True)
                    cmds.connectAttr(dm_root + ".outputTranslate",  v_re + ".input3D[1]", f=True)

                    # --- dot = v_rm · v_re ---
                    dot_v = cmds.createNode("vectorProduct", name=prefix + "_dot_VP")
                    cmds.setAttr(dot_v + ".operation", 1)  # dot product
                    cmds.connectAttr(v_rm + ".output3D", dot_v + ".input1", f=True)
                    cmds.connectAttr(v_re + ".output3D", dot_v + ".input2", f=True)

                    # --- len = v_re · v_re ---
                    len = cmds.createNode("vectorProduct", name=prefix + "_lenVP")
                    cmds.setAttr(len + ".operation", 1)  # dot
                    cmds.connectAttr(v_re + ".output3D", len + ".input1", f=True)
                    cmds.connectAttr(v_re + ".output3D", len + ".input2", f=True)

                    # --- scale = dot / len  (scalar) ---
                    scale_md = cmds.createNode("multiplyDivide", name=prefix + "_scale_MD")
                    cmds.setAttr(scale_md + ".operation", 2)  # divide
                    cmds.connectAttr(dot_v + ".outputX", scale_md + ".input1X", f=True)
                    cmds.connectAttr(len + ".outputX", scale_md + ".input2X", f=True)

                    # --- proj = v_re * scale  (vector) ---
                    proj_md = cmds.createNode("multiplyDivide", name=prefix + "_proj_MD")
                    cmds.setAttr(proj_md + ".operation", 1)

                    cmds.connectAttr(v_re + ".output3D", proj_md + ".input1", f=True)

                    cmds.connectAttr(scale_md + ".outputX", proj_md + ".input2X", f=True)
                    cmds.connectAttr(scale_md + ".outputX", proj_md + ".input2Y", f=True)
                    cmds.connectAttr(scale_md + ".outputX", proj_md + ".input2Z", f=True)

                    # --- offset = v_rm - proj ---
                    offset_pma = cmds.createNode("plusMinusAverage", name=prefix + "_offset_PMA")
                    cmds.setAttr(offset_pma + ".operation", 2)  # subtract
                    cmds.connectAttr(v_rm + ".output3D", offset_pma + ".input3D[0]", f=True)
                    cmds.connectAttr(proj_md + ".output", offset_pma + ".input3D[1]", f=True)

                    # --- dotOffsetAxis = offset * ref_axis ---
                    dotOffset = cmds.createNode("vectorProduct", name=prefix + "_dotOffset_VP")
                    cmds.setAttr(dotOffset + ".operation", 1)  # dot product
                    cmds.connectAttr(offset_pma + ".output3D", dotOffset + ".input1", f=True)
                    # set input2 to the chosen axis
                    cmds.setAttr(dotOffset + ".input2", axis[0], axis[1], axis[2], type="double3")

                    # --- condition: if dotOffset < 0 : -1 else 1 ---
                    cond = cmds.createNode("condition", name=prefix + "_flip_COND")
                    cmds.setAttr(cond + ".operation", 2)  # Less Than
                    cmds.connectAttr(dotOffset + ".outputX", cond + ".firstTerm", f=True)
                    cmds.setAttr(cond + ".secondTerm", 0.0)
                    cmds.setAttr(cond + ".colorIfTrueR", -1.0)   # dot < 0 -> -1
                    cmds.setAttr(cond + ".colorIfFalseR", 1.0)   # else -> 1

                    # --- build the offset vector along axis scaled by offset_len ---
                    axis_md = cmds.createNode("multiplyDivide", name=prefix + "_axisScale_MD")
                    cmds.setAttr(axis_md + ".operation", 1)  # multiply
                    cmds.setAttr(axis_md + ".input1", axis[0], axis[1], axis[2], type="double3")
                    cmds.setAttr(axis_md + ".input2", offset_len, offset_len, offset_len)

                    # --- apply flip scalar to axis vector (multiply by -1 or 1) ---
                    flip_md = cmds.createNode("multiplyDivide", name=prefix + "_flipApply_MD")
                    cmds.setAttr(flip_md + ".operation", 1)  # multiply
                    cmds.connectAttr(axis_md + ".output", flip_md + ".input1", f=True)
                    # connect scalar from condition to input2 X/Y/Z
                    cmds.connectAttr(cond + ".outColorR", flip_md + ".input2X", f=True)
                    cmds.connectAttr(cond + ".outColorR", flip_md + ".input2Y", f=True)
                    cmds.connectAttr(cond + ".outColorR", flip_md + ".input2Z", f=True)

                    # --- final PV position in world space = elbow + offset vector ---
                    pv_pma = cmds.createNode("plusMinusAverage", name=prefix + "_pvPos_PMA")
                    cmds.setAttr(pv_pma + ".operation", 1)  # add
                    cmds.connectAttr(dm_elbow + ".outputTranslate", pv_pma + ".input3D[0]", f=True)
                    cmds.connectAttr(flip_md + ".output", pv_pma + ".input3D[1]", f=True)


                    # Convert to root space
                    pv_comp = cmds.createNode("composeMatrix", n=prefix + "_pvPos_CMP")
                    cmds.connectAttr(pv_pma + ".output3D", pv_comp + ".inputTranslate", f=True)
                    pv_mult = cmds.createNode("multMatrix", n=prefix + "_toLocal_MMT")
                    pv_decomp = cmds.createNode("decomposeMatrix", n=prefix + "_toLocal_DCM")

                    cmds.connectAttr(pv_comp + ".outputMatrix", pv_mult + ".matrixIn[0]", f=True)
                    cmds.connectAttr(f"{root}.parentInverseMatrix[0]", pv_mult + ".matrixIn[1]", f=True)

                    # Result local translate
                    cmds.connectAttr(pv_mult + ".matrixSum", pv_decomp + ".inputMatrix", f=True)
                    cmds.connectAttr(pv_decomp + ".outputTranslate", f"{pv_controller}.translate", f=True)
                    #return

                    #cmds.connectAttr(pv_pma + ".output3D", pv_controller+ ".translate", f=True)

                build_auto_pv_nodes(root, elbow, wrist)
                '''
                def get_world_pos(node):
                    """Returns world position as MVector"""
                    mtx = cmds.xform(node, q=True, ws=True, m=True)
                    m = om.MMatrix(mtx)
                    return om.MVector(m[12], m[13], m[14])

                def build_auto_pv(root, elbow, wrist, offset_len=10.0, name="poleVector_LOC"):
                    """
                    Builds a PV locator offset along world Z, with automatic flip.
                    """

                    p_root = get_world_pos(root)
                    p_elbow = get_world_pos(elbow)
                    p_wrist = get_world_pos(wrist)

                    v_root_to_elbow = (p_elbow - p_root).normalize()
                    v_elbow_to_wrist = (p_wrist - p_elbow).normalize()


                    bend_dir = (v_root_to_elbow + v_elbow_to_wrist).normalize()
                    z_axis = om.MVector(0, 0, 1)

                    if bend_dir * z_axis < 0:
                        z_axis *= -1


                    pv_pos = p_elbow + z_axis * offset_len

                    cmds.xform(pv_controller, ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))
                build_auto_pv(root, elbow, wrist, offset_len=15.0)
                cmds.parent(pv_controller, root)
                cmds.pointConstraint(elbow, pv_controller, mo=True)
            cmds.select(clear=True)

    def spawn_joint(self, all=False):
        if all:
            all_descendants = cmds.listRelatives("guide", ad=True, type="transform", fullPath=True)#need to not harcode
            all_descendants.reverse()
            guides = [
                #so short that my brain confused, need to write proper one later
                g for g in all_descendants
                if "_root" in cmds.ls(g, sn=True)[0].lower()
                and cmds.attributeQuery("isVenGuide", node=g, exists=True)
            ]
        else:
            cmds.warning("Still in construction")
            #guides = cmds.ls(selection=True, type="transform", long=True)

        map = {}

        if guides:
            parents = cmds.listRelatives(guides[0], allParents=True) or []
            guide_name = parents[-1] if parents else None

            main_group = cmds.group(empty=True, world=True, n="rig") #Need to connect the name to guide later, need to check if exist
            system_group = cmds.group(parent=main_group, empty=True, n="Do_Not_Touch")
            skeleton_group = cmds.group(parent=system_group, empty=True, n="skeletons")
            cmds.group(parent=system_group, empty=True, n="geometry")
            cmds.group(parent=system_group, empty=True, n="rig_systems")
            cmds.group(parent=main_group, empty=True, n="controls")

            for guide in guides:
                self.build_joints_from_guides(False, guide, skeleton_group)

            cmds.setAttr(f"{guide_name}.visibility", 0)

    def build_joints_from_guides(self, hierarchy=False, root_guide=None, parent=None):
        """
        Build joint based on guides that contain "isVenGuide"
        """
        visited = set()
        joints = {}
        if root_guide in visited:
            return
        visited.add(root_guide)

        if not cmds.attributeQuery("isVenGuide", node=root_guide, exists=True):
            return

        guide_list = []
        # --- CASE 1: follow EP Curve for hierarchy ---
        if hierarchy == False:
            parts = root_guide.split("|")
            curve_name = parts[-1].replace("root", "crv")
            #print(curve_name)
            up_name = parts[-1].replace("root", "angle")
            if cmds.objExists(curve_name):
                curve_shape = cmds.listRelatives(curve_name, s=True, fullPath=True)[0] or []
                num_cvs = cmds.getAttr(curve_shape + ".controlPoints", size=True)

                for i in range(num_cvs):
                    attr = f"{curve_shape}.controlPoints[{i}]"
                    guide = self.find_guide(attr)
                    guide_list.append(guide)
            else:
                cmds.warning(f"No curve found for {root_guide}")
                return

        for guide in guide_list:
            pos = cmds.xform(guide, q=True, ws=True, t=True)
            base_guide = guide.split("|")[-1]
            joint_name = naming_config.parse_and_build(base_guide, prefix="joint")
            jnt = cmds.createNode("joint", name=joint_name)
            cmds.xform(jnt, ws=True, t=pos)
            if not cmds.objExists(up_name):
                up_name = root_guide
            if parent:
                try:
                    if cmds.objectType(parent) == "joint":
                        aim = cmds.aimConstraint(jnt, parent, aimVector=self.axis_to_vector("x+"), upVector=self.axis_to_vector("y+"), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.makeIdentity(parent, apply=True, rotate=True, translate=False, scale=False)

                    cmds.parent(jnt, parent)
                    parent = jnt

                except RuntimeError:
                    cmds.warning(f"{jnt} is already parented under {parent}, skipping...")

    def create_guide_controller(self, isSphere=True, name=None, parent=None, pos=(0,0,0), rot=(0,0,0), r=0.5):
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
            cmds.parent(node, parent, r=True)
            cmds.xform(node, t=pos,  ro=rot)
            print(f"Parent True {node}, {pos}")
        else:
            cmds.xform(node, t=pos)
            cmds.rotate(rot[0], rot[1], rot[2], node, rotateXYZ=True)
        self.rename_shape(node)

        return node

    def rename_shape(self, node):
        """Rename the first shape under a transform to match the transform name"""
        shapes = cmds.listRelatives(node, shapes=True, fullPath=False)
        if shapes:
            new_name = node + "Shape"
            return cmds.rename(shapes[0], new_name)
        return None

    def axis_to_vector(self, axis):
        if axis == "x+": return (1,0,0)
        if axis == "x-": return (-1,0,0)
        if axis == "y+": return (0,1,0)
        if axis == "y-": return (0,-1,0)
        if axis == "z+": return (0,0,1)
        if axis == "z-": return (0,0,-1)
        raise ValueError("Invalid axis: " + axis)

    def find_guide(self, attr):
        """Climb up until a node with 'isVenGuide' is found."""
        nodes = cmds.listConnections(attr, s=True, d=False) or []
        visited = set()

        while nodes:
            node = nodes[0]  # take the first connection?
            if node in visited:
                break
            visited.add(node)
            node_long = cmds.ls(node, long=True)[0]
            if cmds.attributeQuery("isVenGuide", node=node, exists=True):
                return node_long

            # otherwise keep climbing up
            nodes = cmds.listConnections(node, s=True, d=False) or []

        return None

    def add_string(self, obj, name, type, *args, **kwargs):
        cmds.addAttr(obj, ln=name, dt="string")
        cmds.setAttr(f"{obj}.{name}", type.get("value", ""), type="string")

    def add_bool(self,obj, name, type, *args, **kwargs):
        cmds.addAttr(obj, ln=name, at="bool", dv=int(type.get("value", False)))
        cmds.setAttr(f"{obj}.{name}", e=True, k=True)

    def add_enum(self,obj, name, type, side, *args, **kwargs):
        self.useSide = None #self.sideCheck.isChecked()
        value = str(type.get("value", None))

        if self.useSide:
            value = self.sideRadioGrp.checkedButton().text()

        OVERRIDES = {
            "comp_side": value,
            }
        opts = ":".join(type.get("options", []))
        cmds.addAttr(obj, ln=name, at="enum", en=opts)

        value = OVERRIDES.get(name, value)
        if "value" in type:
            idx = type["options"].index(value)
            cmds.setAttr(f"{obj}.{name}", idx)

    def add_float(self, obj, name, type, index, *args, **kwargs):
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
        selection = cmds.ls(select=True)
        self.guide_settings_layout.addWidget(widget)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _toggleRadio(self, radGrp, enabled):
        for rb in radGrp.buttons():
            rb.setEnabled(enabled)
            if enabled:
                rb.setStyleSheet("")
            else:
                rb.setStyleSheet("color: #555555;")  # dark grey color

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
