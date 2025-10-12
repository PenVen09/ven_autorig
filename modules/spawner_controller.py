from maya import cmds
from ..core.spawner_base import SpawnerBase
from ..core.utils import maya_utils, shape_builder
from .ChainIKFK import ChainIKFK
class SpawnerController(SpawnerBase):
    def precheck(self) -> bool:
        if cmds.objExists(self.guide_group) and cmds.objExists(self.joint_group_name):
            if all:
                all_descendants = cmds.listRelatives(self.guide_group, ad=True, type="transform", fullPath=True)#need to not harcode
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

    def spawn(self, root_guide, hierarchy=False) -> None:
        #root controller
        main_root_ctrl, main_root_group = shape_builder.create_nurbs("Four Arrows", color="green",
                                                                     name=self.root_controller_name,
                                                                     offset=True, parent=self.controller_group_name)

        cmds.matchTransform(main_root_group, self.root_joint_name)
        in_root_ctrl, in_root_group = shape_builder.create_nurbs("Circle", color="yellow",
                                                                 name = self.inroot_controller_name,
                                                                 offset=True, parent=main_root_ctrl)
        cmds.matchTransform(in_root_group, self.root_joint_name)


        guide_dict = {}
        for guide in root_guide:
            guide_list, guide_type = self.get_parts(guide)
            guide_dict = {guide_type: guide_list} #essentials joint

        for type, guide in guide_dict.items():
            self.test(type)
            pass


    def test(self, rig_type):
        rig_types = {
            "arm": ChainIKFK,
            "leg": ChainIKFK, #tmp
            "spine": ChainIKFK #tmp
        }

        rig_class = rig_types[rig_type]
        a = rig_class()
        a.build()
        pass

    def finalize(self) -> None:
        pass
    def place_controller(self):
        pass
