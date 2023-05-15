from datetime import timedelta
from time import sleep

from src.hue import HueLightController
from src.models import MatchScore, Team


class ScoreChangedEventHandler:
    def __init__(
        self,
        fav_team_name: str,
        light_controller: HueLightController,
        sync_delay: timedelta,
    ) -> None:
        super().__init__()
        self._flasher = light_controller
        self._fav_team_name = fav_team_name
        self._sync_delay = sync_delay
        self._flash_time = timedelta(seconds=0)

        print(
            "Event handler will flash lights when selected favorite team score: "
            + fav_team_name
        )

    def handle(self, scoring_team: Team) -> None:
        if scoring_team.name == self._fav_team_name:
            print(
                f"NEW SCORE for favorite team '{self._fav_team_name}', let's flash the lights!"
            )
            print(f"Waiting {self._sync_delay} to sync with user's stream...")
            sleep(self._sync_delay.total_seconds())
            self._flasher.blink_lights()
