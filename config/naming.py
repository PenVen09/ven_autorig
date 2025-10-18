from dataclasses import dataclass
from typing import Optional
from maya import cmds
import re

NAMING_PREFS = {
    "order": [("side", "subindex"), "index", "suffix", "stage", "extra"],
    "node_order":["base", "index", "suffix" ],
    "separator": "_",
    "prefixes": {
        "guide": "gd",
        "joint": "bnjnt",
        "ik_rigsystems": "ikjnt",

        "temp": "tmp",
        "controller": "ctrl"
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
    index: Optional[int] = None
    subindex: int = 0
    extra: Optional[str] = ""


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

                if value == None:
                    continue
                parts.append(str(value))

        parts = [p for p in parts if p]#remove whitespace(index)
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
        has_index = False
        for p in parts:
            if p.isdigit():
                has_index = True
                break

        order = list(cls.order)

        if not has_index and "index" in order:
            old_order = [x for x in cls.order if x != "index"]


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

    @classmethod #delete later
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

    def get_name(cls, ctx) -> str:
        pass



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




