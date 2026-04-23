from abc import ABC, abstractmethod


class AbstractScenarioTemplate(ABC):
    """Template Method: fixed algorithm for running a routine."""

    def run(self) -> str:
        parts = [self.prepare(), self.execute_steps(), self.finish()]
        return " | ".join(parts)

    @abstractmethod
    def prepare(self) -> str:
        pass

    @abstractmethod
    def execute_steps(self) -> str:
        pass

    @abstractmethod
    def finish(self) -> str:
        pass
