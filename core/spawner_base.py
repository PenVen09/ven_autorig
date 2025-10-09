from .utils.maya_utils import one_undo, timer
class SpawnerBase:
    def __init__(self, name="Unnamed", logger=None):
        self.name = name
        self.logger = logger

    def precheck(self) -> bool:
        return True

    def spawn(self) -> None:
        raise NotImplementedError("Spawner must implement spawn()")

    def finalize(self) -> None:
        self.logger.log(f"{self.name} spawn finished", "INFO")

    def execute(self, *args, **kwargs):
        if not self.precheck():
            self.log(f"{self.name} precheck failed!", "ERROR")
            return
        self.spawn()
        self.finalize()

