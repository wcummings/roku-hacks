from dataclasses import dataclass


@dataclass
class ShowDefintition:

    name: str
    provider: str
    no_seasons: int
    no_episodes_per_season: int
