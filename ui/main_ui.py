"""AutoRig Tool
why am i here
to do:
- reroute errors to debug box, filter
- better UI D:
- Not sure if should combine fk chain with finger?(or should i make a converter?
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
- QA checker
"""
from typing import Tuple
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QWidget, QPushButton, QVBoxLayout
from maya import cmds

from . import widgets

from ..config import naming, guides_list
from ..config.naming import GLOBAL_CONFIG

from ..core.utils import maya_utils, logger

from ..modules import spawner_guide, spawner_joint


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

        self.logger = logger.Logger()

        self.initialize_ui()
        self.logger.attach_table(self.debug_box)
        self.spawn_guides = spawner_guide.SpawnerGuide(logger = self.logger)
        self.spawn_joints = spawner_joint.SpawnerJoint(logger = self.logger)
        self.setup_connections()

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

    def setup_connections(self):
        self.spawn_component_button.clicked.connect(self.on_spawn_clicked)
        self.duplicate_button.clicked.connect(lambda : self.spawn_guides.duplicate_guides(symmetry=False))
        self.symmetry_button.clicked.connect(lambda : self.spawn_guides.duplicate_guides(symmetry=True))
        self.build_joint.clicked.connect(lambda: self.spawn_joints.execute(all=True))

    def on_spawn_clicked(self):
        tree_selection = self.component_tree_list.currentItem()
        selected = tree_selection.text(0)
        #self.spawn_guidess()
        self.spawn_guides.execute(name=selected, tree = tree_selection)

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
        self.duplicate_button =QtWidgets.QPushButton("Duplicate")
        self.symmetry_button = QtWidgets.QPushButton("Symmetry")

        utilities_layout.addWidget(self.duplicate_button)
        utilities_layout.addWidget(self.symmetry_button)

        self.spawn_component_button = QtWidgets.QPushButton("Spawn Selected")


        #component_layout.addLayout(name_layout)
        #component_layout.addLayout(side_layout)

        component_layout.addWidget(self.spawn_component_button)
        component_layout.addLayout(utilities_layout)
        component_layout.addWidget(component_list_tabs)
        component_list_tabs.addTab(component_tab_widget, "Cmpnt")


        # --------------------------------------------------
        # --- Left side (templates) ---
        self.template_tree = QtWidgets.QTreeWidget()


        self.template_tree.setHeaderHidden(True)
        font = self.template_tree.font()
        font.setPointSize(9)
        self.template_tree.setFont(font)
        self.template_tree.setIndentation(10)


        self.template_tree.setHeaderLabel("Template Tree")
        self.template_tab_widget = QtWidgets.QWidget()
        template_layout = QtWidgets.QVBoxLayout(self.template_tab_widget)
        template_layout.addWidget(self.template_tree)
        component_list_tabs.addTab(self.template_tab_widget, "Tmp")

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
        #build_selected.clicked.connect(lambda: spawner_joint.execute(all=False))
        self.build_joint = QtWidgets.QPushButton("Joints")
        #build_joint.clicked.connect(lambda: SpawnerJoint.execute(all=False))
        build_controller = QtWidgets.QPushButton("Controller")

        build_layout.addWidget(build_selected)
        build_layout.addWidget(self.build_joint)
        build_layout.addWidget(build_controller)
        content_area.addLayout(build_layout)
        self.populate_treeview(self.component_tree_list)
        self.populate_treeview(self.template_tree)
        self.component_tree_list.expandAll()
        self.template_tree.expandAll()

        return w

    def build_debug_box(self):
        w = QtWidgets.QGroupBox("Debug")
        w.setMinimumSize(500,130)
        l = QtWidgets.QVBoxLayout(w)

        self.debug_box = QtWidgets.QTableWidget()
        self.debug_box.setColumnCount(3)
        self.debug_box.verticalHeader().setVisible(False)
        self.debug_box.horizontalHeader().setVisible(False)
        self.debug_box.horizontalHeader().setStretchLastSection(True)
        self.debug_box.verticalHeader().setVisible(False)
        self.debug_box.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.debug_box.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.debug_box.setColumnWidth(0, 60)
        self.debug_box.setColumnWidth(1, 50)

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
        list = guides_list.component_lists
        if tree_widget == self.template_tree:
            list = guides_list.Templates
        for parent, children in list.items():
            tree_item = QtWidgets.QTreeWidgetItem(tree_widget,[parent])
            tree_item.setIcon(0, QtGui.QIcon(":folder-closed.png"))
            for child, info in children.items():
                QtWidgets.QTreeWidgetItem(tree_item, [child])

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

            primary_vec = naming.AXIS_PREFS["primary"]
            secondary_vec = naming.AXIS_PREFS["secondary"]
            if ctx.side == "R":
                primary_vec = self.flip_axis(primary_vec)
                secondary_vec = self.flip_axis(secondary_vec)
            if parent:
                try:
                    if cmds.objectType(parent) == "joint":
                        aim = cmds.aimConstraint(jnt, parent, aimVector=self.axis_to_vector(primary_vec), upVector=self.axis_to_vector(secondary_vec), worldUpType="objectrotation", worldUpObject=up_name)
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
                    if cmds.objExists(temp):

                        aim = cmds.aimConstraint(jnt, temp, aimVector=self.axis_to_vector(primary_vec), upVector=self.axis_to_vector(secondary_vec), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.parent(jnt, temp)
                        break
                    # keep climbing up
                    parenta = cmds.listRelatives(guide_parent, parent=True)




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

    def axis_to_vector(self, axis):
        if axis == "x+": return (1,0,0)
        if axis == "x-": return (-1,0,0)
        if axis == "y+": return (0,1,0)
        if axis == "y-": return (0,-1,0)
        if axis == "z+": return (0,0,1)
        if axis == "z-": return (0,0,-1)

    def flip_axis(self, axis):
        AXIS_FLIP = {"x+": "x-", "x-": "x+",
                    "y+": "y-", "y-": "y+",
                    "z+": "z-", "z-": "z+"}
        return AXIS_FLIP.get(axis, axis)
