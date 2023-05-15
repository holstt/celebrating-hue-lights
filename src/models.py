from dataclasses import dataclass


@dataclass(frozen=True)
class Team:
    name: str
    points: int


@dataclass(frozen=True)
class MatchScore:
    home_team: Team
    away_team: Team
