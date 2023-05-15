import argparse
import time
from datetime import timedelta

import phue
import yaml
from pkg_resources import require

from src import args
from src.hue import HueLightController, MyBridge
from src.score_event_handler import ScoreChangedEventHandler
from src.score_monitor import ScoreChangeMonitor
from src.score_scraper import ScoreScraper

app_args = args.get_args()

# Load config
with open(app_args.config, "r") as f:
    config_dict = yaml.safe_load(f)

hue_settings = config_dict["hue_settings"]
app_settings = config_dict["app_settings"]

bridge = MyBridge(ip=hue_settings["ip"], username=hue_settings["username"])
bridge.assert_can_connect()

# Ensure group exists
groups: list[phue.Group] = bridge.groups  # type: ignore
light_group = next(
    (group for group in groups if group.name == hue_settings["group_name"]), None
)
if light_group is None:
    raise Exception("Group does not exist: " + hue_settings["group_name"])


score_provider = ScoreScraper(app_args.url)
light_controller = HueLightController(
    light_group,
    blink_duration=timedelta(seconds=app_settings["blink_duration_seconds"]),
    fav_team_name=app_args.fav,
)
handler = ScoreChangedEventHandler(
    fav_team_name=app_args.fav,
    light_controller=light_controller,
    sync_delay=timedelta(seconds=app_settings["sync_delay_seconds"]),
)
score_monitor = ScoreChangeMonitor(
    score_provider,
    polling_interval=timedelta(seconds=app_settings["polling_interval_seconds"]),
    callback=handler.handle,
)
score_monitor.start()
