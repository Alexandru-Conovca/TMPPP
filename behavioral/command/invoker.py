from typing import List, Optional

from behavioral.command.command import Command


class RemoteControl:
    """Invoker that stores command history and can undo last command."""

    def __init__(self) -> None:
        self._slots: List[Command] = []
        self._history: List[Command] = []

    def add_command(self, command: Command) -> None:
        self._slots.append(command)

    def clear_commands(self) -> None:
        self._slots.clear()

    def press_all(self) -> List[str]:
        results: List[str] = []
        for command in self._slots:
            result = command.execute()
            self._history.append(command)
            results.append(result)
        return results

    def press(self, command: Command) -> str:
        result = command.execute()
        self._history.append(command)
        return result

    def undo_last(self) -> str:
        if not self._history:
            return "No commands in history"
        command = self._history.pop()
        return command.undo()

    def last_command(self) -> Optional[Command]:
        if not self._history:
            return None
        return self._history[-1]
