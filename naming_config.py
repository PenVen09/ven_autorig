from dataclasses import dataclass
from maya import cmds

NAMING_PREFS = {
    "order": ["prefix", "base", "side", "index", "suffix"],
    "separator": "_",
    "prefixes": {
        "guide": "g",
        "joint": "jnt",
        "final": "rig",
        "temp": "tmp"
    },
    "side": {"Left": "L", "Right": "R", "Center": "C"}
}

@dataclass
class NamingContext:
    base: str
    side: str
    stage: str
    suffix: str
    index: int = 0
    subindex: int = 0

def build_name(ctx: NamingContext) -> str:
    """Reorder naming based on settings"""
    parts = []
    for token in NAMING_PREFS["order"]:
        if token == "prefix":
            parts.append(NAMING_PREFS["prefixes"][ctx.stage])
        elif token == "base":
            parts.append(ctx.base)
        elif token == "side":
            parts.append(f"{NAMING_PREFS['side'][ctx.side]}{ctx.subindex}")
        elif token == "index":
            parts.append(str(ctx.index))
        elif token == "suffix":
            parts.append(ctx.suffix)

    return NAMING_PREFS["separator"].join(parts)

def get_unique_name(ctx: NamingContext, start_index: int = 0) -> str:
    """Generate and check if name unique or not, keep increment the index"""
    if start_index is not None:
        ctx.subindex = start_index
    while cmds.objExists(build_name(ctx)):
        ctx.subindex += 1
    return build_name(ctx)


def parse_and_build(name, order=None, new_order=None, **overrides):
    """
    Parse a name into parts, then rebuild into a new string.
    """
    if order is None:
        order = NAMING_PREFS["order"]
    if new_order is None:
        new_order = order

    parts = name.split(NAMING_PREFS["separator"])
    ctx = {key: val for key, val in zip(order, parts)}
    for key, value in overrides.items():
        ctx[key] = NAMING_PREFS["prefixes"].get(value, value)

    return NAMING_PREFS["separator"].join(ctx[key] for key in new_order if key in ctx)

