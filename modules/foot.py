from maya import cmds
from ..config.naming import GLOBAL_CONFIG
from ..core.bone import Bone
from ..core.utils import shape_builder


class Foot(Bone):
    """Feets, will add sdk"""
    def __init__(self, name, joint_chain=None):
        pass

    def create_guide(self, nodes, root_node, ctx, angle_controller, ep_offset):
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

    def create_joint(self):
        pass

    def create_controller(self):
        pass

