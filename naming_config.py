from dataclasses import dataclass
from maya import cmds

NAMING_PREFS = {
    "order": ["prefix", "base", "side", "index", "suffix"],
    "separator": "_",
    "prefixes": {
        "guide": "g",
        "bind": "bn",
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

