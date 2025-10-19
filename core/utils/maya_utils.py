from maya import cmds
from functools import wraps
import time
from ...config import naming
from ...config.naming import GLOBAL_CONFIG
#will need to do staticmethod later
def one_undo(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        except Exception as e:
            raise e
        finally:
            cmds.undoInfo(closeChunk=True)
    return wrap

def timer(func):
    @wraps(func)
    def wrap(*args, **kwargs):
        self = args[0]
        start_time = time.time()
        result = func(*args, **kwargs)
        if result is False:
            return result
        end_time = time.time()
        elapsed_time = end_time - start_time
        self.logger.log(f"{self.name} spawned in {elapsed_time:.3f} seconds")
        return result
    return wrap

def find_root(selection=None, name="root"):
    """Keep climbing till find root"""
    if not selection:
        selection = cmds.ls(selection=True)[0]
    if len([selection]) == 1:
        selected = selection
        if not name in selected:
            parent = cmds.listRelatives(selected, parent=True)

            while parent:
                parent = parent[0]
                if name in parent:
                    return parent
                parent = cmds.listRelatives(parent, parent=True)
        else:
            return selected

    else:
        cmds.warning("Select only 1 at this moment, will be updated soon")

def find_guide(attr, name = "isVenGuide"):
    """Climb up until a node with 'isVenGuide' is found."""
    nodes = cmds.listConnections(attr, s=True, d=False) or []
    visited = set()

    while nodes:
        node = nodes[0]  # take the first connection?
        if node in visited:
            break
        visited.add(node)
        node_long = cmds.ls(node, long=True)[0]
        if cmds.attributeQuery(name, node=node, exists=True):
            return node_long

        # otherwise keep climbing up
        nodes = cmds.listConnections(node, s=True, d=False) or []

    return None

def has_attr(node, name = "isVenGuide"):
    if not cmds.objExists(node):
        return False
    return cmds.attributeQuery(name, node=node, exists=True)
def duplicate_joint(joint_name: str, joint_suffix: str) -> str:
    """Duplicate a joint and return the new joint name."""
    ctx = GLOBAL_CONFIG.from_string(joint_name)
    ctx.stage = joint_suffix
    new_joint = naming.NamingContext.build(ctx)
    new_joint = cmds.duplicate(joint_name, name=new_joint, parentOnly=True)[0]
    return new_joint
