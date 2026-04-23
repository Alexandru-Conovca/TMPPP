from abc import ABC, abstractmethod


class Command(ABC):

    @abstractmethod
    def execute(self) -> str:
        pass

    def undo(self) -> str:
        return "Undo not supported for this command"
