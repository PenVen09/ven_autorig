from maya import cmds
from .utils import maya_utils
from ..config import naming
from ..config.naming import GLOBAL_CONFIG
class SpawnerBase:
    #naming
    guide_group_name = "guide"
    joint_group_name = "rig"
    skeleton_group_name = "skeletons"
    controller_group_name = "controls"

    #Root Joints
    ctx = naming.NamingContext("root", "C", "guide", "root")
    #ctx.suffix = None
    root_guide_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("root", "C", "joint", "root")
    #ctx.suffix = None
    root_joint_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("root", "C", "controller", "root")
    #ctx.suffix = None
    root_controller_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("inroot", "C", "controller", "inroot")
    #ctx.suffix = None
    inroot_controller_name = naming.NamingContext.build(ctx)

    def __init__(self, name="Unnamed", logger=None):
        self.name = name
        self.logger = logger
        self.guide_group = "guide"
        self.modules_data = []



    def precheck(self) -> bool:
        return True, None

    def spawn(self) -> None:
        raise NotImplementedError("Spawner must implement spawn()")

    def get_parts(self, root_guide, hierarchy=False):
        guide_list = []
        # --- CASE 1: follow EP Curve for hierarchy ---
        parts = root_guide.split("|")
        type = cmds.getAttr(f"{root_guide}.rigType")
        if hierarchy == False and type != "root":
            curve_name = parts[-1].replace("root", "crv")
            up_name = parts[-1].replace("root", "angle")
            if cmds.objExists(curve_name):
                curve_shape = cmds.listRelatives(curve_name, s=True, fullPath=True)[0] or []
                num_cvs = cmds.getAttr(curve_shape + ".controlPoints", size=True)

                for i in range(num_cvs):
                    attr = f"{curve_shape}.controlPoints[{i}]"
                    guide = maya_utils.find_guide(attr)
                    guide_list.append(guide)

                self.modules_data.append(self.add_module(type, parts[-1], guide_list))
            else:
                cmds.warning(f"No curve found for {root_guide}")
                return
        else:
            self.modules_data.append(self.add_module(type, parts[-1], root_guide))

        return self.modules_data


    def get_modules_data(self):
        return self.modules_data

    def add_module(self, module_type, module_name, guide_list):
        module_data = {
            module_name: {
                'type': module_type,
                'guides': guide_list
            }
        }
        return module_data

    def finalize(self) -> None:
        self.logger.log(f"{self.name} spawn finished", "INFO")

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
        self.spawn()
        self.finalize()

