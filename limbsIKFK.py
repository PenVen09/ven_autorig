from maya import cmds
from ..config import naming
from ..config.naming import GLOBAL_CONFIG
from ..core.bone import Bone
from ..core.utils import shape_builder, math, maya_utils

from ..config import naming, guides_list
import maya.api.OpenMaya as om

class LimbsIKFK(Bone):
    """IK/FK chain rig component.
    Inherits common behavior from Bone and adds IK/FK-specific logic.
    """
    def __init__(self, name, root_name):
        self.name = name
        self.root_name = root_name
        #self.joint_chain = None

    def create_rigsystems(self, bn_joint_list=None):

        ik, fk, ikfk, stretch, switch, reverse = maya_utils.duplicate_chain(self.name, bn_joint_list)
        self.create_controller(ik, fk, ikfk, stretch, switch, reverse)

    def create_guide(self, nodes, root_node, ctx, angle_controller, ep_offset):
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

    def create_joint(self, bn_joint_list=None):
        """add twist bone if arm/leg"""
        twist = cmds.getAttr(f"{self.root_name}.twist")
        if twist > 0:
            pass
        pass

    def create_controller(self, ik_joints_list, fk_joints_list, ikfk_joints_list, stretch_joints_list, switch_ctrl, reverse_node):
        parent="controls"
        offset_list = []
        for fk in fk_joints_list:
            ctx = GLOBAL_CONFIG.from_string(fk)
            ctx.stage = "fk_controller"
            new_ctrl = naming.NamingContext.build(ctx)

            ctrl, ctrl_offset = shape_builder.create_nurbs("Circle",name=new_ctrl, offset=True, parent=parent, color="green")

            shape_builder.resize_shape(-0.4, ctrl)
            shape_builder.rotate_shape((0,0,90), ctrl)
            cmds.matchTransform(ctrl_offset, fk)

            parent = ctrl
            cmds.parentConstraint(ctrl, fk, mo=True)

            offset_list.append(ctrl_offset)

        cmds.connectAttr(switch_ctrl + ".ikFkSwitch", offset_list[0] + ".visibility")

        # ======== IK Ctrl ======== #
        parent="controls"
        ctx = GLOBAL_CONFIG.from_string(fk)
        ctx.stage = "ikctrl"
        new_ctrl = naming.NamingContext.build(ctx)

        ctrl, ctrl_offset = shape_builder.create_nurbs("box",name=new_ctrl, offset=True, parent=parent, color="red")


        cmds.addAttr(ctrl, ln="FOLLOW", at="enum", en="----------", k=True)
        cmds.addAttr(ctrl, ln="follow", at="enum", en="world:limb:COG:shoulder", k=True)

        cmds.addAttr(ctrl, ln="STRETCH", at="enum", en="----------", k=True)
        cmds.addAttr(ctrl, longName='stretchiness', attributeType='float', min=0, max=1, defaultValue=1, keyable=True)
        cmds.addAttr(ctrl, ln="stretchType", at="enum", en="Both:Stretch:Squash", k=True)


        cmds.connectAttr(reverse_node + ".outputX", ctrl_offset + ".visibility")
        shape_builder.resize_shape(8.0, ctrl)
        cmds.matchTransform(ctrl_offset, ik_joints_list[-1], position=True)
        ikhandle = cmds.ikHandle(sj=ik_joints_list[0], ee=ik_joints_list[-1])[0]

        # ======== IK Pole Vector Ctrl ======== #
        ctx.stage = "ikpv"
        new_pvctrl = naming.NamingContext.build(ctx)
        pv_ctrl , pv_offset = shape_builder.create_nurbs("diamond", name=new_pvctrl, offset=True, parent=parent, color="red")
        cmds.addAttr(pv_ctrl, ln="follow", at="enum", en="world:limb", k=True)
        cmds.addAttr(pv_ctrl, longName='lock', attributeType='float', min=0, max=1, defaultValue=0, keyable=True)

        cmds.connectAttr(reverse_node + ".outputX", pv_offset + ".visibility")


        ctx.stage = "guide"
        ctx.suffix = "pvDir"
        pv_guide_name =  naming.NamingContext.build(ctx)
        cmds.matchTransform(pv_offset, pv_guide_name, position=True)


        cmds.poleVectorConstraint(pv_ctrl, ikhandle)
        cmds.orientConstraint(ctrl, ik_joints_list[-1])
        cmds.parent(ikhandle, ctrl)


        maya_utils.create_stretch(ik_joints_list, stretch_joints_list, ctrl, switch_ctrl, ikfk_joints_list)

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
