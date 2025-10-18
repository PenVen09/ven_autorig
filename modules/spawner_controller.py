from maya import cmds
from ..core.spawner_base import SpawnerBase
from ..core.utils import maya_utils, shape_builder
from .ChainIKFK import ChainIKFK
from ..core.base_rigsystem import BaseRigSystems
class SpawnerController(SpawnerBase):

    def __init__(self, logger=None, name="Unnamed"):
        super().__init__()
        self.logger = logger
        self.name = name


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
        self.spawn(pre)
        self.finalize()

    def spawn(self, root_guide) -> None:
        for guide in root_guide:
            A = self.get_parts(guide)

        self.rig_system = BaseRigSystems(name="rig", module_data=A)
        self.rig_system.build()

    def finalize(self) -> None:
        pass
