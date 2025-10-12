from maya import cmds
from ...config.shape_data import shapes_lists, shape_colors

def create_nurbs(shape_name, name, offset=False, parent=None, color="red") -> str:

    if shape_name != "Circle":
        curve = cmds.curve(d=1, p=shapes_lists[shape_name], n=name, k=list(range(len(shapes_lists[shape_name]))))
    else:
        curve = cmds.circle(n=name, normal=(0, 1, 0), radius=50.0, ch=False)[0]


    cmds.select(clear=True)
    cmds.setAttr(curve + ".overrideEnabled", 1)
    cmds.setAttr(curve + ".overrideColor", shape_colors[color])

    if offset:
        curve_group = cmds.group(curve, n=f"{name}_offset", parent=parent)#need to use the naming later
        cmds.select(clear=True)
        return curve, curve_group
    if parent:
        cmds.parent(curve, parent)
        cmds.select(clear=True)
        return curve
    return curve

def create_offset(name, child, parent=None):
    #del later
    group = cmds.group(child, n=name, parent=parent)
    #cmds.parent(child, group)
    return group

def parent(child, parent):
    #del later
    pass

def create_guide_controller( isSphere=True, name=None, parent=None, pos=(0,0,0), rot=(0,0,0), r=1.0, color =None):
    if not isSphere:
        node = create_nurbs("box", name)
        cmds.setAttr(node + ".overrideEnabled", 1)
        cmds.setAttr(node + ".overrideColor", shape_colors["red"])

    else:
        node = create_nurbs("sphere", name)
        cmds.setAttr(node + ".overrideEnabled", 1)
        cmds.setAttr(node + ".overrideColor", shape_colors["yellow"])


    if color:
        cmds.setAttr(node + ".overrideColor", shape_colors[color])

    if r != 1.0:
        resize_shape(r, node)

    if parent:
        cmds.parent(node, parent, r=True)
        cmds.xform(node, t=pos,  ro=rot)
        #print(f"Parent True {node}, {pos}")
    else:
        cmds.xform(node, t=pos)
        cmds.rotate(rot[0], rot[1], rot[2], node, rotateXYZ=True)

    rename_shape(node)

    return node

def rename_shape(node):
    """Rename the first shape under a transform to match the transform name"""
    shapes = cmds.listRelatives(node, shapes=True, fullPath=False)
    if shapes:
        new_name = node + "Shape"
        return cmds.rename(shapes[0], new_name)
    return None

def resize_shape(delta, node):
    shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
    offset = 1.0

    if shapes:
        for selected in shapes:
            value = 1.0 + (delta +(offset * delta))
            cmds.scale(value, value, value, selected + ".cv[*]", relative=True)

