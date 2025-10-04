from maya import cmds
from ...config import shape_data
def create_nurbs(shape_name, full_name):
    return cmds.curve(d=1, p=shape_data.shapes_lists[shape_name], n=full_name)
