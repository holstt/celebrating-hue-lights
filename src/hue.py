import colorsys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

import phue
import webcolors
from phue import Bridge


def color_to_hsb(color_name):
    # Convert the color name to RGB
    rgb = webcolors.name_to_rgb(color_name)

    # Convert the RGB values to the range [0, 1]
    rgb_normalized = [x / 255.0 for x in rgb]

    # Convert the RGB color to HSL
    h, l, s = colorsys.rgb_to_hls(*rgb_normalized)

    # Convert the HSL values to the range expected by the Philips Hue API:
    # H: [0, 65535]
    # S: [0, 254]
    # B: [0, 254]
    h = int(h * 65535)
    s = int(s * 254)
    b = int(l * 254)

    return h, s, b


class MyBridge(Bridge):
    # Check if we can connect to the bridge. phue library does not complain if we can't connect, so we need to check manually
    def assert_can_connect(self):
        api = self.get_api()
        # Raise an exception if api object contains an error
        if type(api) == list and "error" in api[0]:
            error_message = api[0]["error"]["description"]
            raise Exception(error_message)


# Loads all JSON files in the folder and checks if they contain the key
# Returns none if no file contains the key
def find_key_in_folder(folder_path, key_to_find):
    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]

    for json_file in json_files:
        with open(os.path.join(folder_path, json_file), "r") as f:
            data = json.load(f)

            if key_to_find in data:
                return data[key_to_find]

    return None


# Responsible for managing the Hue lights
# Blinks the lights in colors of the team
class HueLightController:
    def __init__(
        self, light_group: phue.Group, blink_duration: timedelta, fav_team_name: str
    ) -> None:
        super().__init__()
        self.group = light_group
        self._blink_duration = blink_duration
        team_colors_dir = Path("./team_colors")

        # Get the colors for the team
        self.colors = find_key_in_folder(team_colors_dir, fav_team_name)
        if self.colors is None:
            raise RuntimeError(f"No colors found for team: {fav_team_name}")
        print(
            f"Light controller will use the following colors for '{fav_team_name}': "
            + ", ".join(self.colors)
        )

        # Convert the color names to HSB values
        self.colors = [color_to_hsb(color) for color in self.colors]

    def blink_lights(self) -> None:
        print(f"Flashing lights for duration {self._blink_duration}!")
        start_time = datetime.now()

        # Save the current state of the lights
        light_states = [
            (light.hue, light.saturation, light.brightness)
            for light in self.group.lights
        ]

        while datetime.now() - start_time < self._blink_duration:
            for hue, saturation, brightness in self.colors:  # type: ignore
                for light in self.group.lights:
                    light.hue = hue
                    light.saturation = saturation
                    light.brightness = brightness
                    light.alert = "select"  # Make light blink in its current color
                sleep(0.5)  # Wait for blink to finish

        # Restore the lights to their original state
        for light, (hue, saturation, brightness) in zip(
            self.group.lights, light_states
        ):
            light.hue = hue
            light.saturation = saturation
            light.brightness = brightness
