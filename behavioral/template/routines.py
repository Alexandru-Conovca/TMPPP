from manager.home_manager import HomeManager
from scenarios.builder import ScenarioDirector, StandardScenarioBuilder
from behavioral.template.template import AbstractScenarioTemplate


class BaseRoutine(AbstractScenarioTemplate):

    def __init__(self, keyword: str, title: str) -> None:
        self._keyword = keyword
        self._title = title
        self._manager = HomeManager.get_instance()
        self._director = ScenarioDirector(StandardScenarioBuilder())

    def prepare(self) -> str:
        exists = self._manager.run_scenario(self._keyword)
        if "not found" in exists.lower():
            scenario = self._build_if_missing()
            self._manager.add_scenario(scenario)
            return self._title + ": prepared (scenario created)"
        return self._title + ": prepared (scenario found)"

    def execute_steps(self) -> str:
        return self._title + ": " + self._manager.run_scenario(self._keyword)

    def finish(self) -> str:
        return self._title + ": finished"

    def _build_if_missing(self):
        if self._keyword == "morning":
            return self._director.create_morning()
        if self._keyword == "evening":
            return self._director.create_evening()
        return self._director.create_away()


class MorningRoutine(BaseRoutine):

    def __init__(self) -> None:
        super().__init__(keyword="morning", title="MorningRoutine")


class EveningRoutine(BaseRoutine):

    def __init__(self) -> None:
        super().__init__(keyword="evening", title="EveningRoutine")


class AwayRoutine(BaseRoutine):

    def __init__(self) -> None:
        super().__init__(keyword="away", title="AwayRoutine")
