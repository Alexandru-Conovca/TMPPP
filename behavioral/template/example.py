from behavioral.template.routines import AwayRoutine, EveningRoutine, MorningRoutine


def run_example() -> str:
    return "\n".join([
        MorningRoutine().run(),
        EveningRoutine().run(),
        AwayRoutine().run(),
    ])


if __name__ == "__main__":
    print(run_example())
