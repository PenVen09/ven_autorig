from maya import cmds
from ..core.spawner_base import SpawnerBase
from ..modules.ChainIKFK import ChainIKFK
from .utils import shape_builder


class BaseRigSystems:
    """Manage all rig components."""
    def __init__(self, name="rig", module_data=None):
        self.module_datass = module_data
        self.name = name
        self.spawner = SpawnerBase()
        self.controllers = []
        self.joints = []
        self.root = None

    def build(self) -> None:
        cmds.setAttr(f"skeletons.visibility", 0)
        self.build_root()

        for module_dict in self.module_datass:
            module_name = list(module_dict.keys())[0]
            data = module_dict[module_name]
            module_type = data['type']

            rig_types = {
            "arm": "ChainIKFK",
            "leg": "ChainIKFK", #tmp
            "spine": "ChainIKFK", #tmp
            "shoulder": "None",
            "root": "None",
            "foot": "Foot"
            }
            rig_class = rig_types[module_type]

            if rig_class == "ChainIKFK":
                rig_module = ChainIKFK(
                    name=module_name,
                )
                rig_module.build(joint_chain=data["guides"])
            elif rig_class == "Foot":
                print("foot")
                pass

    def build_root(self):
        """Create global root controller."""

        if not self.root:  # Only build once
            main_root_ctrl, main_root_group = shape_builder.create_nurbs("Four Arrows", color="green",
                                                                     name=self.spawner.root_controller_name,
                                                                     offset=True, parent=self.spawner.controller_group_name)
            cmds.matchTransform(main_root_group, self.spawner.root_joint_name)

            in_root_ctrl, in_root_group =  shape_builder.create_nurbs("Circle", color="yellow",
                                                                     name = self.spawner.inroot_controller_name,
                                                                     offset=True, parent=main_root_ctrl)
            cmds.matchTransform(in_root_group, self.spawner.root_joint_name)

            #self.root = self.spawner.create_controller("root", shape="circle", color="yellow")
            #self.controllers.append(self.root)
            self.root = main_root_ctrl
            self.controllers.append(self.root)
            self.controllers.append(in_root_ctrl)
            print(f"Root controller created: {self.root}")
        else:
            print("Root already exists — skipping.")
        return self.root


    def add_module(self, module):
        """Register a rig module (e.g. ChainIKFK)."""
        self.module_datass.append(module)


    def cleanup(self):
        """Delete temp nodes, guides, etc."""
        pass
