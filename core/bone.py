
#from ..modules.spawner_guide import SpawnerGuide
#from ..modules.spawner_joint import SpawnerJoint


class Bone:
    """Base class for modular rig components."""
    def __init__(self, name: str):
        self._side = "Center"#tmp
        self._name = name
        self._rtype = self.__class__.__name__
        self._scale = 1.0
        self.guide: list[str] = []
        self.jnts: list[str] = []
        self.ctrls: list[str] = []
        self.offsets: list[str] = []

    @property
    def side(self):
        return self._side

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def type(self):
        return self._rtype

    def create_guide(self, tree):
        raise NotImplementedError

    def create_joint(self):
        #joint_spawner = SpawnerJoint()
        #joint_spawner.execute(all=True)#tmp
        pass

    def create_controller(self):
        raise NotImplementedError

    def colorize(self):
        """Color-code guides or controls by side."""
        pass
