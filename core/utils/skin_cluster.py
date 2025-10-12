from maya import cmds
import os
import xml.etree.ElementTree as ET


this_dir = os.path.dirname(__file__)
utils_dir = os.path.dirname(this_dir)
core_dir = os.path.dirname(utils_dir)
weights_dir = os.path.join(core_dir, "data", "weights")


def save_skin(joints):
    if joints:
        skin_clusters = cmds.ls(type='skinCluster') or []
        if not skin_clusters:
            return

        maya_file = cmds.file(q=True, sn=True, shn=True)
        if maya_file:
            base_name = os.path.splitext(maya_file)[0]
        else:
            base_name = "tmp_scene"
        file_name = f"{base_name}_weights"

        if not os.path.exists(weights_dir):
            cmds.warning("This shouldn't be possible")
            #os.makedirs(data_dir)

        skincluster_to_joints = {}
        for sc in skin_clusters:
            influences = cmds.skinCluster(sc, query=True, influence=True) or []
            skincluster_to_joints[sc] = sorted(influences)
            cmds.deformerWeights(f"{file_name}.xml", export=True, deformer=sc, path=weights_dir)

    else:
        return

def find_missing_influences():

    maya_file = cmds.file(q=True, sn=True, shn=True)
    base_name = os.path.splitext(maya_file)[0] if maya_file else "tmp_scene"
    file_name = f"{base_name}_weights.xml"

    full_path = os.path.join(weights_dir, file_name)

    if not os.path.exists(full_path):
        cmds.warning(f"No deformerWeights file found")
        return []

    # Parse XML to extract joint names
    tree = ET.parse(full_path)
    root = tree.getroot()

    xml_influences = set()
    for child in root[1:]:
        if "source" in child.attrib:
            xml_influences.add(child.attrib["source"])

    # Compare against current scene
    missing = [inf for inf in xml_influences if not cmds.objExists(inf)]
    return missing

def load_skin():
    #what if missing obj, probably for later like in d
    missing_list = set()
    missing = find_missing_influences()
    if missing:
        cmds.group(name = "Missing Influence", empty=True)
        for jnt in missing:
            #cmds.node
            pass
    pass
