"""AutoRig Tool
why am i here
to do:
- reroute errors to debug box
- better UI D:
-Not sure if should combine fk chain with finger?(or should i make a converter?
- each segment aim at child(mgear) similar to ik stuff
- Custom Marking Menus
- STreSS TeSt
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
import time
from itertools import zip_longest
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
import maya.api.OpenMaya as om
from maya import cmds


from . import widgets

from ..config import naming, guides_list, shapes
from ..config.naming import GLOBAL_CONFIG

from ..utils import maya_utils

from ..core import attrs

comments = "This is version 1.0"

class VenAutoRig(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(VenAutoRig, self).__init__(parent)
        self.setMinimumWidth(500)
        self.setWindowFlags(
            QtCore.Qt.Window |
            QtCore.Qt.WindowTitleHint |
            QtCore.Qt.WindowMinimizeButtonHint |
            QtCore.Qt.WindowMaximizeButtonHint |
            QtCore.Qt.WindowCloseButtonHint
        )
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
        self.guide_settings_layout.setContentsMargins(0, 0, 0, 0)

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
        #self.debug_box.appendPlainText(__doc__)
        #QtCore.QTimer.singleShot(0, lambda: self.debug_box.verticalScrollBar().setValue(0))

        l.addWidget(self.debug_box)
        return w

    def build_section_three(self):
        w = QtWidgets.QGroupBox("group text")
        l = QtWidgets.QVBoxLayout(w)
        l.addWidget(QtWidgets.QLabel("lol"))
        l.addWidget(QtWidgets.QPushButton("idk"))
        return w

    def populate_treeview(self, tree_widget):
        self.component_widgets = {}

        for parent, children in guides_list.component_lists.items():
            tree_item = QtWidgets.QTreeWidgetItem(tree_widget,[parent])
            tree_item.setIcon(0, QtGui.QIcon(":folder-closed.png"))

            for child, info in children.items():
                QtWidgets.QTreeWidgetItem(tree_item, [child])

    def spawn_section_window(self):
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Manage Section")
        dialog.resize(400, 300)
        main_layout = QtWidgets.QVBoxLayout(dialog)


        accept_btn = QtWidgets.QPushButton("Accept")
        cancel_btn =QtWidgets.QPushButton("Cancel")
        main_layout.addWidget(accept_btn)
        main_layout.addWidget(cancel_btn)

        result = dialog.exec_()
        pass


    @maya_utils.one_undo
    def spawn_guides(self):
        tree_selection = self.component_tree_list.currentItem()
        selection = cmds.ls(selection=True)
        if tree_selection:
            selected = tree_selection.text(0)
            add_section_list = ["Fingers", "Spine", "FKIKChain"]
            if selected in add_section_list:
                self.spawn_length_window()
                pass

            self.useSide = None#self.sideCheck.isChecked()
            side = guides_list.component_lists[tree_selection.parent().text(0)][selected]["attrs"]["comp_side"]["value"]
            if self.useSide:
                side = self.sideRadioGrp.checkedButton().text()


            suffix = guides_list.component_lists[tree_selection.parent().text(0)][selected]["suffix"]
            base = selected#should be fine since select from tree
            side_index = 0
            position = guides_list.component_lists[tree_selection.parent().text(0)][selected]["position"]
            rotation = guides_list.component_lists[tree_selection.parent().text(0)][selected]["rotation"]
            ctx = naming.NamingContext(base, side, "guide", suffix[0])

            guide_length = len(position)

            if guide_length > 1:
                ctx.suffix = "crv"
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
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
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                if ctx.index == 0:
                    parent_node = self.create_guide_controller(True, full_name, None, pos, rot)
                    parent_shape = cmds.listRelatives(parent_node, shapes=True, fullPath=True)[0]
                    cmds.setAttr(f"{parent_shape}.visibility", 0)

                    ctx.suffix = "root"
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    root_node = self.create_guide_controller(False, full_name, None, pos, rot, r=0.8)


                    cmds.parent(parent_node, root_node)
                    nodes.append(parent_node)
                    cmds.addAttr(root_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    cmds.addAttr(parent_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    attributes = guides_list.component_lists[tree_selection.parent().text(0)][selected]["attrs"]

                    for atb, item in attributes.items():
                        builder = attrs.AttrBuilder()
                        builder.add_attr(root_node, atb, item, index=ctx.subindex, side=side)

                    self.rename_shape(root_node)

                    if not selection:
                        guide_group = cmds.group(empty=True, world=True, n="guide")#Later need to add variable to name guide
                        cmds.group(empty=True, parent=guide_group, n="controller_guide")
                        cmds.parent(root_node, guide_group, absolute=True)
                        cmds.addAttr(guide_group, longName="isGuide", attributeType="bool", defaultValue=1, keyable=False)
                        cmds.setAttr(f"{guide_group}.isGuide",cb=False)
                        cmds.addAttr(guide_group, longName="jointOrder", dt="string")
                        cmds.setAttr(f"{guide_group}.jointOrder", str(GLOBAL_CONFIG.order), type="string")
                        cmds.addAttr(guide_group, longName="ctrlOrder", dt="string")
                        cmds.setAttr(f"{guide_group}.ctrlOrder", str(GLOBAL_CONFIG.order), type="string")
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

                    cmds.addAttr(child_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=False)
                    cmds.setAttr(f"{child_node}.isVenGuide", cb=False)

                    #Probably will make this below as method soon
                    world_space = cmds.createNode("decomposeMatrix", name=f"{child_node}" + "_ws")
                    cmds.connectAttr(f"{child_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{ctx.index}]")

                    parent_node = child_node

            #type = cmds.getAttr(f"{base}.rigType")
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

                parts = GLOBAL_CONFIG.from_string(nodes[0])
                base_name = naming.NamingContext.build(parts, new_order=naming.NAMING_PREFS["node_order"])

                # --- Spawn pole vector arrow ---
                ctx.index = 0 #revisit later
                ctx.suffix = "angle"
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                angle_controller = cmds.curve(
                    d=1,
                    p=shapes.shapes_lists["one_arrow"],
                    n=full_name
                )
                cmds.matchTransform(angle_controller, root_node)
                cmds.parent(angle_controller, root)
                cmds.rotate(90,0,0, angle_controller)
                ctx.suffix = "pv_dir"
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                pv_controller = cmds.curve(
                    d=1,
                    p=shapes.shapes_lists["one_arrow"],
                    n=full_name
                )
                cmds.addAttr(pv_controller, longName="elbowRatio", attributeType="float", defaultValue=0.5, keyable=True)


                # --- Root aim at Elbow --- ##NEED TO DO SMTH SO CAN EASILY CHANGE AXIS
                cmds.aimConstraint(wrist, root, aimVector=primary_vec, upVector=self.axis_to_vector("y+"), worldUpType="object", worldUpObject=elbow)
                cmds.aimConstraint(wrist, elbow, aimVector=primary_vec, upVector=self.axis_to_vector("y+"), worldUpType="objectrotation", worldUpObject=wrist)
                
                # --- Elbow between two points ---
                elbow_offset = cmds.group(empty=True, p=root_node, n=f"{elbow}_offset")
                cmds.parent(elbow, elbow_offset, a=True)

                bc = cmds.createNode("blendColors", name=f"BC_{base_name}")
                cmds.connectAttr(root + ".translate", bc + ".color1", f=True)
                cmds.connectAttr(wrist + ".translate", bc + ".color2", f=True)
                cmds.connectAttr(pv_controller + ".elbowRatio", bc + ".blender", f=True)

                # Drive elbow pos
                cmds.connectAttr(bc + ".output", elbow_offset + ".translate", f=True)

                # --- Pole Vector Position ---
                def get_world_pos(node):
                    """Returns world position as MVector"""
                    mtx = cmds.xform(node, q=True, ws=True, m=True)
                    m = om.MMatrix(mtx)
                    return om.MVector(m[12], m[13], m[14])

                def get_local_axis_world(node, axis='y'):
                    """
                    Returns the world-space vector of a node's local axis.
                    axis: 'x', 'y', or 'z'
                    """
                    mtx = cmds.xform(node, q=True, ws=True, m=True)
                    m = om.MMatrix(mtx)

                    if axis.lower() == 'x':
                        v = om.MVector(m[0], m[4], m[8])
                    elif axis.lower() == 'y':
                        v = om.MVector(m[1], m[5], m[9])
                    else:  # 'z'
                        v = om.MVector(m[2], m[6], m[10])

                    return v.normalize()

                def build_auto_pv(root, elbow, wrist, up, offset_len=10.0):
                    """
                    Builds a PV locator offset along world Z, with automatic flip.
                    """

                    p_root = get_world_pos(root)
                    p_elbow = get_world_pos(elbow)
                    p_wrist = get_world_pos(wrist)
                    p_up = get_local_axis_world(up, axis='z')
                    #print(p_up)

                    v_root_to_elbow = (p_elbow - p_root).normalize()
                    v_elbow_to_wrist = (p_wrist - p_elbow).normalize()

                    z_axis = om.MVector(0, 0, 1)

                    if p_up[-1] > 0:
                        z_axis *= -1

                    pv_pos = p_elbow + z_axis * offset_len

                    cmds.xform(pv_controller, ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))
                    return pv_pos

                build_auto_pv(root, elbow, wrist, angle_controller, offset_len=15.0)

                cmds.parent(pv_controller, root)
                cmds.pointConstraint(elbow, pv_controller, mo=True)

            elif base == "Foot":
                foot_list = {
                    "heel":(0, -7.829, -3.469),
                    "out":(4.555, -8.734, 9.097),
                    "in":(-3.643, -8.734, 9.097)
                    }
                ctx.index = 0
                for name, pos in foot_list.items():
                    ctx.suffix = f"{name}crv"
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    ep_curve = cmds.curve(d=1, p=[(0,0,0),(0,0,0)], name=full_name)
                    ep_shape = self.rename_shape(ep_curve)

                    cmds.parent(ep_curve, ep_offset)
                    cmds.setAttr(f"{ep_curve}.template", 1)
                    cmds.setAttr(f"{ep_curve}.lineWidth", 1.5)

                    node_name = f"{nodes[0]}_ws"
                    if not cmds.objExists(node_name):
                        cmds.createNode("decomposeMatrix", name=f"{nodes[0]}" + "_ws")
                        cmds.connectAttr(f"{nodes[0]}.worldMatrix[0]", f"{node_name}.inputMatrix", f=True)
                    cmds.connectAttr(f"{node_name}.outputTranslate", f"{ep_shape}.controlPoints[0]")

                    ctx.suffix = name
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    new_node = self.create_guide_controller(True, full_name, nodes[0], pos, (0,0,0), r=0.8)

                    new_space = cmds.createNode("decomposeMatrix", name=f"{new_node}" + "_ws")
                    cmds.connectAttr(f"{new_node}.worldMatrix[0]", f"{new_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{new_space}.outputTranslate", f"{ep_shape}.controlPoints[1]")
            cmds.select(clear=True)

            self.log("Spawned Guides")

    @maya_utils.one_undo
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
            up_name = parts[-1].replace("root", "angle")
            if cmds.objExists(curve_name):
                curve_shape = cmds.listRelatives(curve_name, s=True, fullPath=True)[0] or []
                num_cvs = cmds.getAttr(curve_shape + ".controlPoints", size=True)

                for i in range(num_cvs):
                    attr = f"{curve_shape}.controlPoints[{i}]"
                    guide = maya_utils.find_guide(attr)
                    guide_list.append(guide)


            else:
                cmds.warning(f"No curve found for {root_guide}")
                return

        type = cmds.getAttr(f"{root_guide}.rigType")
        guides = guide_list
        if type == "shoulder" or type ==  "finger":
            guides = guide_list[:-1]
        elif type == "foot" :
            guides = guide_list[1:]

        for guide in guides:
            pos = cmds.xform(guide, q=True, ws=True, t=True)
            base_guide = guide.split("|")[-1]

            ctx = GLOBAL_CONFIG.from_string(base_guide)
            ctx.stage = "joint"
            joint_name = naming.NamingContext.build(ctx)

            jnt = cmds.createNode("joint", name=joint_name)

            cmds.xform(jnt, ws=True, t=pos)

            if not cmds.objExists(up_name):
                up_name = root_guide

            if parent:
                try:
                    if cmds.objectType(parent) == "joint":

                        aim = cmds.aimConstraint(jnt, parent, aimVector=self.axis_to_vector("x+"), upVector=self.axis_to_vector("z+"), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.makeIdentity(parent, apply=True, rotate=True, translate=False, scale=False)


                    cmds.parent(jnt, parent)
                    if guide == guide_list[-1]:
                            cmds.setAttr(jnt + ".jointOrientX", 0)
                            cmds.setAttr(jnt + ".jointOrientY", 0)
                            cmds.setAttr(jnt + ".jointOrientZ", 0)
                    parent = jnt

                except RuntimeError:
                    cmds.warning(f"{jnt} is already parented under {parent}, skipping...")

            if guide == guides[0]:#clean naming later
                parenta = cmds.listRelatives(root_guide, parent=True)
                while parenta:
                    guide_parent = parenta[0]
                    if guide_parent == "guide":
                        break
                    # Convert guide name → joint name (e.g. hips_g → hips_jnt)
                    base_guide = guide_parent.split("|")[-1]
                    ctx = GLOBAL_CONFIG.from_string(base_guide)
                    ctx.stage = "joint"
                    temp = naming.NamingContext.build(ctx)
                    primary_axis = naming.AXIS_PREFS["primary"]
                    if cmds.objExists(temp):
                        aim = cmds.aimConstraint(jnt, temp, aimVector=self.axis_to_vector(primary_axis), upVector=self.axis_to_vector("z+"), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.parent(jnt, temp)
                        break
                    # keep climbing up
                    parenta = cmds.listRelatives(guide_parent, parent=True)

    def create_guide_controller(self, isSphere=True, name=None, parent=None, pos=(0,0,0), rot=(0,0,0), r=0.5, color =None):
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


        if color:
            cmds.setAttr(node + ".overrideColor", color)


        if parent:
            cmds.parent(node, parent, r=True)
            cmds.xform(node, t=pos,  ro=rot)
            #print(f"Parent True {node}, {pos}")
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

    def _populate_module(self):
        self._clear_layout(self.guide_settings_layout)

        root = maya_utils.find_root()
        if root:
            type = cmds.getAttr(f"{root}.rigType")
            side = cmds.getAttr(f"{root}.comp_side")
            temp_side_list = {0:"Right", 1:"Center", 2: "Left"}

            widget, button, layout = self._collapsible_button(f"{type.capitalize()} -> {temp_side_list[side]}")
            layout.setSpacing(0)

            self.attr_wrappers = []

            user_attrs = cmds.listAttr(root, userDefined=True) or []
            for attr in user_attrs[2:]:
                wrapper = widgets.AttrWrapper(root, attr)
                self.attr_wrappers.append(wrapper)
                factory = widgets.QTWidgetFactory()

                widget_fn = factory.BUILDERS.get(wrapper.type, factory.build_string)
                new_widget = widget_fn(wrapper)
                new_widget.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(new_widget)

            self.guide_settings_layout.addWidget(widget)


    def _separator(self):
        """ Spawn separator based on this style """
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("margin-top: 5px; margin-bottom: 5px;")
        return line

    def _chain_length_popup(self):
        """idk window with spinbox, direction, spacing"""
        pass

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
        content_layout.setContentsMargins(0, 0, 0, 0)


        section_layout.addWidget(content_widget)

        toggle_button.clicked.connect(lambda: self._collapsible_on_pressed(toggle_button, content_widget))

        return section_widget, toggle_button, content_layout

    def _collapsible_on_pressed(self, buttons, collapse_widget) -> None:
        """ Complement _collapsible_button """
        checked = buttons.isChecked()
        buttons.setArrowType(QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow)
        collapse_widget.setVisible(not checked)

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


    def log(self, message):
        ts = time.strftime("%H:%M:%S")
        self.debug_box.appendPlainText(f"[{ts}] {message}")
        pass
