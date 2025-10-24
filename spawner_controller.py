from maya import cmds
from ..core.spawner_base import SpawnerBase
from ..core.utils import maya_utils, shape_builder
from ..modules.limbsIKFK import LimbsIKFK
from ..modules.foot import Foot
class SpawnerController(SpawnerBase):

    def __init__(self, logger=None, name="Unnamed"):
        super().__init__()
        self.logger = logger
        self.name = name
        self.root = None
        self.controllers = []

    def precheck(self) -> bool:
        if cmds.objExists(self.guide_group_name) and cmds.objExists(self.joint_group_name):
            if all:
                all_descendants = cmds.listRelatives(self.guide_group_name, ad=True, type="transform", fullPath=True)#need to not harcode
                all_descendants.reverse()
                guides = []
                for g in all_descendants:
                    # Get the short name of the node
                    short_name = cmds.ls(g, sn=True)[0].lower()

                    has_root = "root" in short_name
                    has_is_guide = cmds.attributeQuery("isVenGuide", node=g, exists=True)
                    if has_root and has_is_guide:
                        guides.append(g)

                if guides:
                    return guides

            else:
                return False, "Guide/Rig group Missings"

        else:
            return False


    @maya_utils.one_undo
    @maya_utils.timer
    def execute(self, *args, **kwargs):
        pre = self.precheck()
        if isinstance(pre, tuple):
            result, *rest = pre
            message = rest[0] if rest else None
        else:
            result, message = pre, None
        if not result:
            self.logger.log(f"{self.name} precheck failed! {message or ''}", "ERROR")
            return False
        self.create_rigsystems(pre)
        self.finalize()

    def build_root(self):
        """Create global root controller."""

        if not cmds.objExists(self.root_controller_name):
            main_root_ctrl, main_root_group = shape_builder.create_nurbs("Four Arrows", color="green",
                                                                     name=self.root_controller_name,
                                                                     offset=True, parent=self.controller_group_name)
            cmds.matchTransform(main_root_group, self.root_joint_name)

            in_root_ctrl, in_root_group =  shape_builder.create_nurbs("Circle", color="yellow",
                                                                     name = self.inroot_controller_name,
                                                                     offset=True, parent=main_root_ctrl)
            cmds.matchTransform(in_root_group, self.root_joint_name)


            self.controllers.append(main_root_ctrl)
            self.controllers.append(in_root_ctrl)
            print(f"Root controller created: {self.root}")
        else:
            print("Root already exists — skipping.")


    def create_rigsystems(self, names) -> None:
        cmds.setAttr(f"skeletons.visibility", 0)
        self.build_root()
        for name in names:
            datas = self.get_parts(name)

        for module_dict in datas:
            module_name = list(module_dict.keys())[0]
            data = module_dict[module_name]
            module_type = data['type']

        rig_types = {
            "arm": "LimbsIKFK",
            "leg": "LimbsIKFK",
            "spine": "SplineIKFK",
            "shoulder": None,
            "root": None,
            "foot": "Foot"
        }
        #"SplineIKFK": SplineIKFK,
        rig_class_map = {
            "LimbsIKFK": LimbsIKFK,
            "Foot": Foot
        }

        rig_class_name = rig_types.get(module_type)
        rig_class = rig_class_map.get(rig_class_name)

        if rig_class:
            rig_module = rig_class(name=module_name, root_name=names)
            rig_module.create_rigsystems(bn_joint_list=data["guides"])


    def finalize(self) -> None:
        pass
