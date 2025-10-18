from maya import cmds
from ..core.spawner_base import SpawnerBase
from ..modules.ChainIKFK import ChainIKFK
from .utils import shape_builder
from ..config import naming
from ..config.naming import GLOBAL_CONFIG

class BaseRigSystems:
    def __init__(self, name="rig", module_data=None):
        self.module_datass = module_data
        self.name = name
        self.spawner = SpawnerBase()
        self.controllers = []
        self.joints = []
        self.root = None

    def build(self) -> None:
        self.build_root()

        for module_dict in self.module_datass:

            module_name = list(module_dict.keys())[0]
            data = module_dict[module_name]
            module_type = data['type']



            rig_types = {
            "arm": "ChainIKFK",
            "leg": "ChainIKFK", #tmp
            "spine": "ChainIKFK", #tmp
            "shoulder": "ChainIKFK",
            "root": "None"
            }
            rig_class = rig_types[module_type]

            if rig_class == "ChainIKFK":
                module = ChainIKFK(
                    rig=self.name,
                    name=module_name,
                    joint_chain=data["guides"]  # or joints
                )
                self.module_datass.append(module)
                module.build()



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

    def build_all(self):

        #self.create_joint()
        #self.set_shape()
        #self.place_controller()
        #self.delete_guide()
        #self.delete_shape()
        #self.color_controller()
        #self.add_constraint()
        #self.lock_controller()
        pass
    def add_module(self, module):
        """Register a rig module (e.g. ChainIKFK)."""
        self.module_datass.append(module)


    def duplicate_joint(self, joint_name: str, joint_suffix: str) -> str:
        """Duplicate a joint and return the new joint name."""
        ctx = GLOBAL_CONFIG.from_string(joint_name)
        ctx.prefixes = "ik_rigsystems"
        new_joint = naming.NamingContext.build(ctx)
        new_joint = cmds.duplicate(joint_name, name=new_joint, parentOnly=True)[0]
        return new_joint
