from maya import cmds

class AttrBuilder:
    def __init__(self):
        self.attributes = {}
        self.ATTR_BUILDERS = {
            "string": self.add_string,
            "bool": self.add_bool,
            "enum": self.add_enum,
            "float": self.add_float,
            "int": self.add_int
        }

    def add_attr(self, obj, name, type, *args, **kwargs):
        type_attr = type.get("widget", "")
        if type_attr in self.ATTR_BUILDERS:
            return self.ATTR_BUILDERS[type_attr](obj, name, type, *args, **kwargs)
        else:
            raise ValueError(f"Unknown attr type: {type_attr}")

    def add_string(self, obj, name, type, *args, **kwargs):
        cmds.addAttr(obj, ln=name, dt="string")
        cmds.setAttr(f"{obj}.{name}", type.get("value", ""), type="string")

    def add_bool(self,obj, name, type, cb=False, key=False, *args, **kwargs):
        cmds.addAttr(obj, ln=name, at="bool", dv=int(type.get("value", False)), k=key)
        cmds.setAttr(f"{obj}.{name}", e=True, k=True, cb=cb)

    def add_enum(self,obj, name, type, side, cb=False, key=False, *args, **kwargs):
        self.useSide = None #self.sideCheck.isChecked()
        value = str(type.get("value", None))

        if self.useSide:
            value = self.sideRadioGrp.checkedButton().text()

        OVERRIDES = {
            "comp_side": value,
            }
        opts = ":".join(type.get("options", []))
        cmds.addAttr(obj, ln=name, at="enum", en=opts, k=key)

        value = OVERRIDES.get(name, value)
        if "value" in type:
            idx = type["options"].index(value)
            cmds.setAttr(f"{obj}.{name}", idx, cb=cb)

    def add_float(self, obj, name, type, index, cb=False, key=False, *args, **kwargs):
        OVERRIDES = {}
        value = float(type.get("value", 0.0))
        value = OVERRIDES.get(name, value)
        cmds.addAttr(obj, ln=name, at="float", dv=value, k=key)
        cmds.setAttr(f"{obj}.{name}", e=True, k=True, cb=cb)

    def add_int(self, obj, name, type, index, cb=False, key=False, *args, **kwargs):
        """ Maybe will optimize the override stuff later"""
        OVERRIDES = {
                    "comp_index": index,
                    }
        value = float(type.get("value", 0.0))
        value = OVERRIDES.get(name, value)
        cmds.addAttr(obj, ln=name, at="long", dv=value, k=key)
        cmds.setAttr(f"{obj}.{name}", e=True, k=True, cb=cb)
