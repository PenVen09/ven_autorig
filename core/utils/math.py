from maya import cmds
import maya.api.OpenMaya as om
#will need to do staticmethod later
def axis_to_vector(axis):
    if axis == "x+": return (1,0,0)
    if axis == "x-": return (-1,0,0)
    if axis == "y+": return (0,1,0)
    if axis == "y-": return (0,-1,0)
    if axis == "z+": return (0,0,1)
    if axis == "z-": return (0,0,-1)

def flip_axis(axis):
    AXIS_FLIP = {"x+": "x-", "x-": "x+",
                "y+": "y-", "y-": "y+",
                "z+": "z-", "z-": "z+"}
    return AXIS_FLIP.get(axis, axis)

def get_world_pos(node):
    mtx = cmds.xform(node, q=True, ws=True, m=True)
    m = om.MMatrix(mtx)
    return om.MVector(m[12], m[13], m[14])

def local_axis(node, axis='y'):
    mtx = cmds.xform(node, q=True, ws=True, m=True)
    m = om.MMatrix(mtx)

    if axis.lower() == 'x':
        v = om.MVector(m[0], m[4], m[8])
    elif axis.lower() == 'y':
        v = om.MVector(m[1], m[5], m[9])
    else:  # 'z'
        v = om.MVector(m[2], m[6], m[10])
    return v.normalize()
