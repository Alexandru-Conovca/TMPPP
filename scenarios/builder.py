"""
Builder pattern for automation scenarios plus Prototype for cloning scenarios.
"""
from abc import ABC, abstractmethod
from typing import List, Optional


class Scenario:

    def __init__(self, name: str) -> None:
        self.name = name
        self.steps: List[str] = []

    def add_step(self, step: str) -> None:
        self.steps.append(step)

    def clone(self) -> "Scenario":
        cloned = Scenario(name=f"{self.name} (clone)")
        for step in self.steps:
            cloned.add_step(step)
        return cloned

    def summary(self) -> str:
        if not self.steps:
            return f"Scenario '{self.name}': no steps"
        steps_text = "; ".join(self.steps)
        return f"Scenario '{self.name}': {steps_text}"

    def __str__(self) -> str:
        return self.summary()


class ScenarioBuilder(ABC):
    """Abstract builder declaring construction steps."""

    @abstractmethod
    def reset(self) -> None:
        pass

    @abstractmethod
    def set_name(self, name: str) -> None:
        pass

    @abstractmethod
    def add_step(self, description: str) -> None:
        pass

    @abstractmethod
    def get_result(self) -> Scenario:
        pass


class StandardScenarioBuilder(ScenarioBuilder):
    """Concrete builder that assembles Scenario objects."""

    def __init__(self) -> None:
        self._scenario: Optional[Scenario] = None
        self.reset()

    def reset(self) -> None:
        self._scenario = Scenario(name="")

    def set_name(self, name: str) -> None:
        if self._scenario is None:
            self.reset()
        self._scenario.name = name

    def add_step(self, description: str) -> None:
        if self._scenario is None:
            self.reset()
        self._scenario.add_step(description)

    def get_result(self) -> Scenario:
        if self._scenario is None:
            self.reset()
        result = self._scenario
        self._scenario = None
        return result


class ScenarioDirector:
    """Director orchestrates building predefined scenarios."""

    def __init__(self, builder: ScenarioBuilder) -> None:
        self._builder = builder

    def create_morning(self) -> Scenario:
        self._builder.reset()
        self._builder.set_name("Morning Scenario")
        self._builder.add_step("Open blinds and turn on lights to 70%")
        self._builder.add_step("Set thermostat to 21C")
        self._builder.add_step("Start camera recording in porch")
        return self._builder.get_result()

    def create_evening(self) -> Scenario:
        self._builder.reset()
        self._builder.set_name("Evening Scenario")
        self._builder.add_step("Dim lights to 40%")
        self._builder.add_step("Set thermostat to 22C")
        self._builder.add_step("Arm alarm for night mode")
        return self._builder.get_result()

    def create_away(self) -> Scenario:
        self._builder.reset()
        self._builder.set_name("Away Scenario")
        self._builder.add_step("Turn off all lights")
        self._builder.add_step("Set thermostat to eco mode 19C")
        self._builder.add_step("Arm alarm and enable all cameras")
        return self._builder.get_result()
