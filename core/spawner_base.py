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
    ctx = naming.NamingContext("root", "C", "guide", "tmp")
    ctx.suffix = None
    root_guide_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("root", "C", "joint", "tmp")
    ctx.suffix = None
    root_joint_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("root", "C", "controller", "tmp")
    ctx.suffix = None
    root_controller_name = naming.NamingContext.build(ctx)

    ctx = naming.NamingContext("inroot", "C", "controller", "tmp")
    ctx.suffix = None
    inroot_controller_name = naming.NamingContext.build(ctx)

    def __init__(self, name="Unnamed", logger=None):
        self.name = name
        self.logger = logger
        self.guide_group = "guide"


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

            else:
                cmds.warning(f"No curve found for {root_guide}")
                return
        else:
            guide_list.append(root_guide)#for root jnt, but need to expand soon
        return guide_list, type

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

