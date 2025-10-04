from .utils import logger


class SpawnerBase:
    def __init__(self, name="Unnamed"):
        self.name = name
        self.log = logger.log

    def precheck(self) -> bool:
        return True

    def spawn(self) -> None:
        raise NotImplementedError("Spawner must implement spawn()")

    def finalize(self) -> None:
        self.log(f"{self.name} spawn finished", "INFO")

    def execute(self) -> None:
        if not self.precheck():
            self.log(f"{self.name} precheck failed!", "ERROR")
            return
        self.spawn()
        self.finalize()

