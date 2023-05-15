import re
import time
from dataclasses import dataclass
from datetime import timedelta
from math import e
from typing import Callable

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

from src.hue import HueLightController
from src.models import MatchScore, Team


# Scrapes score from a flashscore.com URL
class ScoreScraper:
    def __init__(self, match_url: str) -> None:
        super().__init__()
        # Ensure url follows format (https://www.flashscore.com/match/<ID>/#/match-summary/match-summary)
        match_pattern = re.compile(
            r".*\.flashscore\.com/match/[^/]+/#/match-summary/match-summary$"
        )
        if not match_pattern.match(match_url):
            raise ValueError(
                f"Invalid match url: {match_url}. Does not match pattern: {match_pattern.pattern}"
            )

        self.match_url = match_url
        self.prev_fav_score = None

        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        # Avoid verbose logging, set to warning
        # INFO = 0, WARNING = 1, LOG_ERROR = 2, LOG_FATAL = 3
        options.add_argument("--log-level=1")

        self.driver = webdriver.Chrome(options=options)

        print("Scraper will scrape match scores from: " + match_url)

    def get_current_score(self) -> MatchScore:
        self.driver.get(self.match_url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        try:
            home_team_name = (
                soup.find("div", class_="duelParticipant__home")
                .find("div", class_="participant__participantName")  # type: ignore
                .text  # type: ignore
            )
            away_team_team = (
                soup.find("div", class_="duelParticipant__away")
                .find("div", class_="participant__participantName")  # type: ignore
                .text  # type: ignore
            )

            score = (
                soup.find("div", class_="duelParticipant__score")
                .find("div", class_="detailScore__wrapper")  # type: ignore
                .text  # type: ignore
            )
            home_score, away_score = score.split("-")

            home_team = Team(name=home_team_name, points=int(home_score))
            away_team = Team(name=away_team_team, points=int(away_score))
            match = MatchScore(home_team=home_team, away_team=away_team)

        except AttributeError as e:
            raise RuntimeError(
                "An error occured while scraping the score due to a missing element. Please check the page for changes in the HTML structure, and update the code accordingly."
            )

        return match
