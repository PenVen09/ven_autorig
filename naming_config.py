from dataclasses import dataclass
from maya import cmds
import re
NAMING_PREFS = {
    "order": ["base", ("side", "subindex"), "index", "suffix", "stage"],
    "node_order":["base", "index", "suffix" ],
    "separator": "_",
    "prefixes": {
        "guide": "g",
        "joint": "jnt",
        "final": "rig",
        "temp": "tmp"
    },
    "side": {"Left": "L", "Right": "R", "Center": "C"}
}

AXIS_PREFS = {
    "primary": "x+",
    "secondary": "z+"
}



@dataclass
class NamingContext:
    """Based on NamingConfig name rules, spew out a name string"""
    base: str = ""
    side: str = ""
    stage: str = ""
    suffix: str = ""
    index: int = 0
    subindex: int = 0


    @classmethod
    def build(cls, ctx, new_order=None):
        if new_order is None:
            new_order = NamingConfig.order

        parts = []

        for key in new_order:
            if isinstance(key, tuple):
                # combine if side and subindex in ()
                combined = ""

                for k in key:
                    value = getattr(ctx, k, "")
                    if k == "side":
                        value = NamingConfig.side.get(value, value)
                    combined += str(value)

                parts.append(combined)
            else:
                # Single attribute
                value = getattr(ctx, key, "")
                if key == "stage":
                    value = NamingConfig.prefixes.get(value, value)
                parts.append(str(value))


        full_name = NamingConfig.separator.join(parts)
        return full_name



class NamingConfig:
    """ This class is the global order rules on naming"""
    separator = NAMING_PREFS["separator"]
    order = NAMING_PREFS["order"]
    prefixes = NAMING_PREFS["prefixes"]
    side = NAMING_PREFS["side"]

    @classmethod
    def from_string(cls, name, old_order=None):
        """Parse a name into parts"""
        if old_order is None:
            old_order = cls.order

        parts = name.split(cls.separator)

        ctx_dict = {}
        for key, val in zip(old_order, parts):
            if isinstance(key, tuple):
                # split alphabet and numerical(for side and subindex)
                match = re.match(r"([A-Za-z]+)(\d*)", val)
                if match:
                    for subkey, group in zip(key, match.groups()):
                        ctx_dict[subkey] = group
                else:
                    # fallback: assign whole value to first key
                    ctx_dict[key[0]] = val
                    ctx_dict[key[1]] = "0"
            else:
                ctx_dict[key] = val

        return NamingContext(**ctx_dict)

    @classmethod
    def get_unique_name(cls, ctx, start_index: int = 0) -> str:
        """Generate and check if name unique or not, keep increment the index"""
        attempts = 0
        max_attempts = 5

        if isinstance(ctx, str):#auto parse if ctx somehow is string
            ctx = NamingConfig.from_string(ctx)

        if start_index is not None:
            ctx.subindex = start_index
        while cmds.objExists(ctx.build(ctx)):
            ctx.subindex += 1
            attempts += 1
            if attempts >= max_attempts:
                raise RuntimeError(f"Could not find unique name after {max_attempts} attempts")
        return ctx.build(ctx)



GLOBAL_CONFIG = NamingConfig()
"""
#ctx = NamingConfig.from_string("g_Fingers_L0_0_root")
ctx = NamingContext(base="Fingers", side="L", suffix="root", stage="g", subindex=0)
#name = ctx.build()

unique_name = NamingConfig.get_unique_name(ctx, start_index=0)
print(unique_name)
ctx = NamingConfig.from_string("g_arm_L0_1_jnt")
NamingConfig.get_unique_name()
print(ctx)
print(ctx.base)
print(ctx.suffix)
"""


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


