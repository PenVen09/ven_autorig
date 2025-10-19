from maya import cmds
from ..config import naming
from ..config.naming import GLOBAL_CONFIG
from ..core.bone import Bone
from ..core.utils import shape_builder, math, maya_utils, attrs

from ..config import naming, guides_list
import maya.api.OpenMaya as om

class ChainIKFK(Bone):
    """IK/FK chain rig component.
    Inherits common behavior from Bone and adds IK/FK-specific logic.
    """
    def __init__(self, name):
        self.name = name
        #self.joint_chain = None

    def build(self, joint_chain=None):
        ctx = GLOBAL_CONFIG.from_string(self.name)

        ctx.stage = "group"
        group_name = naming.NamingContext.build(ctx)


        group = cmds.group(n=group_name, empty=True, parent= "rig_systems")

        joint_lists= ["ik_rigsystems", "fk_rigsystems", "ikfk_rigsystems"]
        ik_joints_list, fk_joints_list, ikfk_joints_list = [], [], []

        for i1, list in enumerate(joint_lists):
            parent_list = []
            for i2, j in enumerate(joint_chain):
                joints = maya_utils.duplicate_joint(j, list)
                if i2 > 0:
                    # Parent the new joint to the previous one
                    cmds.parent(joints, parent_list[i2-1])
                else:
                    cmds.parent(joints, group)#temp

                parent_list.append(joints)
                if i1 == 0:
                    ik_joints_list.append(joints)
                elif i1 == 1:
                    fk_joints_list.append(joints)
                else:
                    ikfk_joints_list.append(joints)

    def create_guide(self, nodes, root_node, ctx, angle_controller, ep_offset):
        #spawner = SpawnerGuide()
        #nodes, root_node, ctx, angle_controller, kwargs = spawner.spawn(tree)
        if self.name == "Arm" or self.name == "Leg":
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

    def create_joint(self):
        """add twist bone if arm/leg"""
        pass

    def create_controller(self):
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
