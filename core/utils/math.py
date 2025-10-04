def axis_to_vector(self, axis):
    if axis == "x+": return (1,0,0)
    if axis == "x-": return (-1,0,0)
    if axis == "y+": return (0,1,0)
    if axis == "y-": return (0,-1,0)
    if axis == "z+": return (0,0,1)
    if axis == "z-": return (0,0,-1)

def flip_axis(self, axis):
    AXIS_FLIP = {"x+": "x-", "x-": "x+",
                "y+": "y-", "y-": "y+",
                "z+": "z-", "z-": "z+"}
    return AXIS_FLIP.get(axis, axis)
