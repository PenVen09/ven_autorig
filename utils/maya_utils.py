from maya import cmds

def find_root(name="root"):
    """Keep climbing till find root"""
    selection = cmds.ls(selection=True)
    if len(selection) == 1:
        selected = selection[0]
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
