from maya import cmds
from ..core.base_rigsystem import BaseRigSystems
from ..config import naming
from ..config.naming import GLOBAL_CONFIG

class ChainIKFK(BaseRigSystems):
    def __init__(self, rig, name, joint_chain=None):
        self.rig = rig
        self.name = name
        self.joint_chain = joint_chain

    def build(self):
        #print(self.joint_chain)
        for j in self.joint_chain:
            #ik_joints = self.duplicate_joint(j, "IK")


            #fk_joints = self.duplicate_joint(joint)
            pass



