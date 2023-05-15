import threading
import time
from datetime import timedelta
from typing import Callable

from src.models import Team
from src.score_scraper import ScoreScraper


# Monitors a match and notifies the observer when the score changes
class ScoreChangeMonitor:
    def __init__(
        self,
        score_scraper: ScoreScraper,
        polling_interval: timedelta,
        callback: Callable[[Team], None],
    ) -> None:
        super().__init__()
        self._scraper = score_scraper
        self._wait_time = polling_interval
        self._callback = callback

    def start(self):
        print("Checking initial score...")
        prev_score = self._scraper.get_current_score()
        print(prev_score)

        while True:
            print("Checking current score...")
            current_score = self._scraper.get_current_score()
            print(current_score)

            self.notify_if_score_changed(prev_score.home_team, current_score.home_team)
            self.notify_if_score_changed(prev_score.away_team, current_score.away_team)
            prev_score = current_score

            # Delay before checking again
            print(
                f"Waiting {self._wait_time.total_seconds()} seconds before checking again..."
            )
            time.sleep(self._wait_time.total_seconds())

    def notify_if_score_changed(self, prev_team: Team, current_team: Team) -> None:
        if prev_team.points != current_team.points:
            print(
                f"{current_team.name} score changed from {prev_team.points} to {current_team.points}"
            )
            # Notify in a new thread so we don't have to wait for the callback to finish
            threading.Thread(target=lambda: self._callback(current_team)).start()
