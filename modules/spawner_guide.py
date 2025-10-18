from maya import cmds
import maya.api.OpenMaya as om
from itertools import zip_longest

from ..core.spawner_base import SpawnerBase
from ..core.utils import shape_builder, math, maya_utils, attrs

from ..config import naming, guides_list
from ..config.naming import GLOBAL_CONFIG

from ..ui import widgets

class SpawnerGuide(SpawnerBase):
    def precheck(self) -> bool:
        selection = cmds.ls(selection=True)
        if not selection:
            return True
        if len(selection) == 1 and maya_utils.has_attr(selection[0]):
            return True
        else:
            return False

    @maya_utils.one_undo
    @maya_utils.timer
    def execute(self, *args, **kwargs):
        if not self.precheck():
            self.logger.log(f"{self.name} precheck failed!", "ERROR")
            return
        self.name = kwargs.get("name")
        tree = kwargs.get("tree")
        if not self.spawn(tree):
            return False
        self.finalize()

    def spawn(self, tree):
        #ned to fix the basejoint only one
        selection = cmds.ls(selection=True) or []
        guide_exist = cmds.objExists("guide")
        if not selection:
            if not guide_exist:
                self.guide_group = cmds.group(empty=True, world=True, n=self.guide_group_name)#Later need to add variable to name guide
                cmds.group(empty=True, parent=self.guide_group, n="controller_guide")
                cmds.addAttr(self.guide_group, longName="isGuide", attributeType="bool", defaultValue=1, keyable=False)
                cmds.setAttr(f"{self.guide_group}.isGuide",cb=False)
                cmds.addAttr(self.guide_group, longName="jointOrder", dt="string")
                cmds.setAttr(f"{self.guide_group}.jointOrder", str(GLOBAL_CONFIG.order), type="string")
                cmds.addAttr(self.guide_group, longName="ctrlOrder", dt="string")
                cmds.setAttr(f"{self.guide_group}.ctrlOrder", str(GLOBAL_CONFIG.order), type="string")
                cmds.addAttr(self.guide_group, longName="rigGroup", dt="string")
                cmds.setAttr(f"{self.guide_group}.rigGroup", "rig", type="string")

                #Root Joints
                ctx = naming.NamingContext("root", "C", "guide", "root")
                ctx.base = "root"
                #ctx.suffix = None
                #ctx.index = None
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)

                self.root_guide = shape_builder.create_guide_controller(False, full_name, self.guide_group, (0,0,0), (0,0,0), r=0.8)
                cmds.addAttr(self.root_guide, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=False)
                cmds.addAttr(self.root_guide, longName="rigType",dt="string")
                cmds.setAttr(f"{self.root_guide}.rigType", "root", type="string")
            else:
                self.root_guide = self.root_guide_name #fix later
                selection = cmds.ls("guide")

        elif len(selection) > 1:
            cmds.warning("More than 1 selection detected")
        else:
            #iforgotwhatthisis
            """
            if cmds.attributeQuery("isVenGuide", node=selection[0], exists=True):
                cmds.matchTransform(root_node, selection[0], pos=True, rot=False, scl=False)
                cmds.parent(root_node, selection[0])
            elif cmds.attributeQuery("isGuide", node=selection[0], exists=True):
                cmds.parent(root_node, selection[0])

            else:
                #self.logger.log("Parent is not autorig guide", "Warning")
                return #eh? or pass
            """
            pass


        if tree:
            selected = tree.text(0)
            side = guides_list.component_lists[tree.parent().text(0)][selected]["attrs"]["comp_side"]["value"]

            suffix = guides_list.component_lists[tree.parent().text(0)][selected]["suffix"]
            base = selected#should be fine since select from tree
            position = guides_list.component_lists[tree.parent().text(0)][selected]["position"]
            rotation = guides_list.component_lists[tree.parent().text(0)][selected]["rotation"]
            ctx = naming.NamingContext(base, side, "guide", suffix[0])

            guide_length = len(position)
            add_section_list = ["Fingers", "Spine", "FKIKChain"]


            if selected in add_section_list:
                win = widgets.spawn_section_window(guide_length, position, rotation)
                if win == False:
                    return False
                position = win[0]
                rotation = win[1]


            if guide_length > 1:
                ctx.suffix = "crv"
                ctx.index = 0
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                ep_curve = cmds.curve(d=1, p=position, name=full_name)
                ep_shape = shape_builder.rename_shape(ep_curve)
                cmds.setAttr(f"{ep_curve}.template", 1)
                cmds.setAttr(f"{ep_curve}.lineWidth", 1.5)
            else:
                ep_curve = None
            nodes = []

            i = 0
            for i, (pos, rot, suffix) in enumerate(zip_longest(position, rotation, suffix, fillvalue=suffix[-1])):
                """ Might need to fix how the enumerate/index work for controlPoints(if index is changeable by user)"""
                ctx.suffix = suffix
                if selected in add_section_list:
                    ctx.index = i
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                if i == 0:
                    parent_node = shape_builder.create_guide_controller(True, full_name, None, pos, rot, r=0.8)
                    parent_shape = cmds.listRelatives(parent_node, shapes=True, fullPath=True)[0]
                    cmds.setAttr(f"{parent_shape}.visibility", 0)

                    ctx.suffix = "root"
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    root_node = shape_builder.create_guide_controller(False, full_name, None, pos, rot, r=0.8)

                    cmds.parent(parent_node, root_node)
                    nodes.append(parent_node)
                    cmds.addAttr(root_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    cmds.addAttr(parent_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=True)
                    attributes = guides_list.component_lists[tree.parent().text(0)][selected]["attrs"]

                    for atb, item in attributes.items():#move to metadata?
                        builder = attrs.AttrBuilder()
                        builder.add_attr(root_node, atb, item, index=ctx.subindex, side=side)

                    shape_builder.rename_shape(root_node)

                    if not guide_exist:
                        cmds.parent(root_node, self.root_guide)
                        guide_exist=True
                    else:

                        cmds.parent(root_node, self.root_guide, absolute=True)

                    if ep_curve:
                        ctx.suffix = "crvOffset"
                        full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                        ep_offset = cmds.group(ep_curve, parent=parent_node, n=f"{full_name}",r=True)
                        cmds.connectAttr(f"{parent_node}.worldInverseMatrix", f"{ep_offset}.offsetParentMatrix")

                        #Probably will make this below as method soon
                        world_space = cmds.createNode("decomposeMatrix", name=f"{parent_node}" + "_ws")
                        cmds.connectAttr(f"{parent_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                        cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{i}]")

                    ctx.suffix = "angle"
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    angle_controller = shape_builder.create_nurbs("one_arrow", full_name, color="yellow")
                    cmds.matchTransform(angle_controller, root_node)
                    cmds.parent(angle_controller, parent_node)
                    cmds.rotate(90,0,0, angle_controller)



                else:
                    child_node = shape_builder.create_guide_controller(True, full_name, parent_node, pos, rot, r=0.8)
                    nodes.append(child_node)

                    cmds.addAttr(child_node, longName="isVenGuide", attributeType="bool", defaultValue=1, keyable=False)
                    cmds.setAttr(f"{child_node}.isVenGuide", cb=False)

                    #Probably will make this below as method soon
                    world_space = cmds.createNode("decomposeMatrix", name=f"{child_node}" + "_ws")
                    cmds.connectAttr(f"{child_node}.worldMatrix[0]", f"{world_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{world_space}.outputTranslate", f"{ep_shape}.controlPoints[{i}]")

                    parent_node = child_node

            #type = cmds.getAttr(f"{base}.rigType")
            if base == "Arm" or base == "Leg":
                primary_vec = math.axis_to_vector("x+")
                up_vec = math.axis_to_vector("y+")
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

                #ctx.suffix = "angle"
                #full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                #angle_controller = shape_builder.create_nurbs("one_arrow", full_name)
                #cmds.matchTransform(angle_controller, root_node)
                #cmds.parent(angle_controller, root)
                #cmds.rotate(90,0,0, angle_controller)

                ctx.suffix = "pvDir"
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                pv_controller = shape_builder.create_nurbs("one_arrow", full_name)
                cmds.addAttr(pv_controller, longName="elbowRatio", attributeType="float", defaultValue=0.5, keyable=True)


                # --- Root aim at Elbow --- ##NEED TO DO SMTH SO CAN EASILY CHANGE AXIS
                cmds.aimConstraint(wrist, root, aimVector=primary_vec, upVector=up_vec, worldUpType="object", worldUpObject=elbow)
                cmds.aimConstraint(wrist, elbow, aimVector=primary_vec, upVector=up_vec, worldUpType="objectrotation", worldUpObject=wrist)

                # --- Elbow between two points ---
                ctx = GLOBAL_CONFIG.from_string(elbow)
                ctx.suffix = "elbowOffset"
                full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                elbow_offset = cmds.group(empty=True, p=root_node, n=full_name)
                cmds.parent(elbow, elbow_offset, a=True)

                bc = cmds.createNode("blendColors", name=f"BC_{base_name}")
                cmds.connectAttr(root + ".translate", bc + ".color1", f=True)
                cmds.connectAttr(wrist + ".translate", bc + ".color2", f=True)
                cmds.connectAttr(pv_controller + ".elbowRatio", bc + ".blender", f=True)

                # Drive elbow pos
                cmds.connectAttr(bc + ".output", elbow_offset + ".translate", f=True)

                # --- Pole Vector Position ---
                self.build_auto_pv(pv_controller, elbow, angle_controller, offset_len=15.0)

                cmds.parent(pv_controller, root)
                cmds.pointConstraint(elbow, pv_controller, mo=True)

            elif base == "Foot":
                foot_list = {
                    "heel":(0, -7.829, -3.469),
                    "out":(4.555, -8.734, 9.097),
                    "in":(-3.643, -8.734, 9.097)
                    }

                for name, pos in foot_list.items():
                    ctx.suffix = f"{name}crv"
                    full_name = GLOBAL_CONFIG.get_unique_name(ctx)
                    ep_curve = cmds.curve(d=1, p=[(0,0,0),(0,0,0)], name=full_name)
                    ep_shape = shape_builder.rename_shape(ep_curve)

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
                    new_node = shape_builder.create_guide_controller(True, full_name, nodes[0], pos, (0,0,0), r=0.8)

                    new_space = cmds.createNode("decomposeMatrix", name=f"{new_node}" + "_ws")
                    cmds.connectAttr(f"{new_node}.worldMatrix[0]", f"{new_space}.inputMatrix", f=True)
                    cmds.connectAttr(f"{new_space}.outputTranslate", f"{ep_shape}.controlPoints[1]")
            cmds.select(clear=True)
            return True

    def duplicate_guides(self, symmetry=True):
        selected = cmds.ls(selection=True)
        for selection in selected:
            root = maya_utils.find_root(selection)
            side = cmds.getAttr(f"{root}.comp_side")
            duplicated = cmds.duplicate(root, returnRootsOnly=True, ic=True, un=True)[0]
            if symmetry == True:
                if side == 2:#left
                    side_index = 0
                elif side == 1:#center
                    side_index = 1
                else:
                    side_index = 2
                cmds.setAttr(f"{duplicated}.comp_side", side_index)
                parent = cmds.listRelatives(root, parent=True)
                mirror_group = cmds.group(empty=True, name="TMP_MIRROR", world=True)
                cmds.parent(duplicated, mirror_group)
                cmds.scale(-1,1,1, mirror_group)
                cmds.parent(duplicated, parent)
                cmds.delete(mirror_group)

            orig_hierarchy = cmds.ls(root, dag=True, type="transform", long=True) or []
            dup_hierarchy  = cmds.ls(duplicated, dag=True, type="transform", long=True) or []

            for orig, dup in zip(reversed(orig_hierarchy), reversed(dup_hierarchy)):
                base_name = orig.split('|')[-1]
                ctx = GLOBAL_CONFIG.from_string(base_name)
                if symmetry == True:
                    ctx.side = "L" if ctx.side == "R" else "R"
                new_name = GLOBAL_CONFIG.get_unique_name(ctx)
                cmds.rename(dup, new_name)

    def add_metadata(self):
        pass

    def build_auto_pv(self, pv_controller, elbow, up, offset_len=10.0):
        """
        Builds a PV locator offset along world Z, with automatic flip.
        """
        p_elbow = math.get_world_pos(elbow)
        p_up = math.local_axis(up, axis='z')

        z_axis = om.MVector(0, 0, 1)

        if p_up[-1] > 0:
            z_axis *= -1

        pv_pos = p_elbow + z_axis * offset_len

        cmds.xform(pv_controller, ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))
        return pv_pos

    def show_guide(self):
        #need to hide joint later
        vis = cmds.getAttr(f"{self.guide_group}.visibility")
        vis = 1 if vis == 0 else 0
        cmds.setAttr(f"{self.guide_group}.visibility", vis)
        #cmds.setAttr(f"{self.guide_group}.visibility", vis)

    def finalize(self):
        #super().finalize()
        pass



