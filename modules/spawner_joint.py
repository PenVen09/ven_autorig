from maya import cmds
from ..config import naming
from ..config.naming import GLOBAL_CONFIG
from ..core.utils import maya_utils, math, skin_cluster
from ..core.spawner_base import SpawnerBase


class SpawnerJoint(SpawnerBase):
    def precheck(self, all=False) -> bool:
        if cmds.objExists(self.guide_group):
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
                return False, "Guide group Missings"

        else:
            return False

    def spawn(self, guides, group_name="rig") -> None:
        parents = cmds.listRelatives(guides[0], allParents=True) or []
        guide_name = parents[-1] if parents else None

        if not cmds.objExists(group_name):
            main_group = cmds.group(empty=True, world=True, n=group_name)
            system_group = cmds.group(parent=main_group, empty=True, n="Do_Not_Touch")
            skel_groups = cmds.group(parent=system_group, empty=True, n= self.skeleton_group_name)
            cmds.group(parent=system_group, empty=True, n="geometry")
            cmds.group(parent=system_group, empty=True, n="rig_systems")
            cmds.group(parent=main_group, empty=True, n="controls")
            for guide in guides:
                self.build_joints_from_guides(False, guide, self.root_joint_name)#uh need to change skeletons to variable

        else:
            self.respawn()

            for guide in guides:
                self.build_joints_from_guides(False, guide,  self.root_joint_name)
            skin_cluster.load_skin()

        cmds.setAttr(f"{self.guide_group}.visibility", 0)

    def build_joints_from_guides(self, hierarchy=False, root_guide=None, parent=None):


        visited = set()
        joints = {}
        if root_guide in visited:
            return
        visited.add(root_guide)
        if not cmds.attributeQuery("isVenGuide", node=root_guide, exists=True):
            return

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




        guides = guide_list
        if type == "shoulder" or type ==  "finger":
            guides = guide_list[:-1]
        elif type == "foot" :
            guides = guide_list[1:]
        elif type == "root":
            jnt = cmds.createNode("joint", name=self.root_joint_name)
            cmds.parent(jnt, self.skeleton_group_name)
            return

        for guide in guides:
            pos = cmds.xform(guide, q=True, ws=True, t=True)
            base_guide = guide.split("|")[-1]
            ctx = GLOBAL_CONFIG.from_string(base_guide)
            ctx.stage = "joint"
            joint_name = naming.NamingContext.build(ctx)

            jnt = cmds.createNode("joint", name=joint_name)

            cmds.xform(jnt, ws=True, t=pos)

            if not cmds.objExists(up_name):
                up_name = root_guide

            primary_vec = naming.AXIS_PREFS["primary"]
            secondary_vec = naming.AXIS_PREFS["secondary"]
            if ctx.side == "R":
                primary_vec = math.flip_axis(primary_vec)
                secondary_vec = math.flip_axis(secondary_vec)


            if parent:
                try:
                    if cmds.objectType(parent) == "joint" and parent != self.root_joint_name:
                        print(up_name)
                        aim = cmds.aimConstraint(jnt, parent, aimVector=math.axis_to_vector(primary_vec), upVector=math.axis_to_vector(secondary_vec), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.makeIdentity(parent, apply=True, rotate=True, translate=False, scale=False)

                    cmds.parent(jnt, parent)
                    if guide == guide_list[-1]:
                            cmds.setAttr(jnt + ".jointOrientX", 0)
                            cmds.setAttr(jnt + ".jointOrientY", 0)
                            cmds.setAttr(jnt + ".jointOrientZ", 0)
                    parent = jnt

                except RuntimeError:
                    cmds.warning(f"{jnt} is already parented under {parent}, skipping...")

            if guide == guides[0]:#clean naming later
                parenta = cmds.listRelatives(root_guide, parent=True)
                while parenta:
                    guide_parent = parenta[0]
                    if guide_parent == "guide":
                        break
                    # Convert guide name → joint name (e.g. hips_g → hips_jnt)
                    base_guide = guide_parent.split("|")[-1]
                    ctx = GLOBAL_CONFIG.from_string(base_guide)
                    ctx.stage = "joint"
                    temp = naming.NamingContext.build(ctx)
                    if cmds.objExists(temp):
                        aim = cmds.aimConstraint(jnt, temp, aimVector=math.axis_to_vector(primary_vec), upVector=math.axis_to_vector(secondary_vec), worldUpType="objectrotation", worldUpObject=up_name)
                        cmds.delete(aim)
                        cmds.parent(jnt, temp)
                        break
                    # keep climbing up
                    parenta = cmds.listRelatives(guide_parent, parent=True)

    def finalize(self) -> None:
        cmds.select(clear=True)
        pass

    @maya_utils.one_undo
    @maya_utils.timer
    def execute(self, *args, **kwargs):
        all = kwargs.get("all")
        self.name = "Joints"
        pre = self.precheck(all)
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

    def respawn(self):
        all_joints = cmds.listRelatives(self.skeleton_group_name, allDescendents=True, type='joint') or []
        skin_cluster.save_skin(all_joints)
        cmds.delete(all_joints)



