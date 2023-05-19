import argparse
from pathlib import Path

import phue
import requests
import yaml

from src.hue import MyBridge

# Args:
# - name: The name of the application that will be registered on the bridge.
# - ip: The IP address of the Hue bridge. This can be found in your Hue app.

# Example usage:
# python app_setup.py -a "My Hue App" -b 192.168.x.x

# The script will do the following:
# - User Registration: The script creates a new user that is authorized to access the Hue bridge.
# - Group Selection: You will be prompted to select the light group (room) you want the program to control.
# - Configuration File Generation: The script saves all necessary details (including the new user and light group information) in a configuration file. This file will be used by the main application.


args = argparse.ArgumentParser(description="Create a new user on the hue bridge")
args.add_argument(
    "--name",
    "-n",
    type=str,
    help="The name of the app that will be registered on the bridge",
    required=True,
)
args.add_argument(
    "--ip",
    "-i",
    type=str,
    help="The IP address of the hue bridge",
    required=True,
)

# Optional path for the config file
args.add_argument(
    "--config",
    "-c",
    type=str,
    help="Path to config file",
    default="config.yaml",
)


args = args.parse_args()


print(
    "Creating a new user on bridge...\n IP: "
    + args.ip
    + "\n APP_NAME: "
    + args.name
    + "\n"
)
input("Please press the button on the Hue bridge, then press Enter...")

try:
    # NB: Calling api directly instead of phue to get more control over the process
    # Send a request to the bridge to create a new user
    response = requests.post(f"http://{args.ip}/api", json={"devicetype": args.name})

except requests.exceptions.ConnectionError as e:
    raise Exception(
        "Could not connect to the hue bridge. Check the IP address and try again."
    ) from e
except requests.exceptions.Timeout as e:
    raise Exception(
        "Error: The request to the hue bridge timed out. Check the network and try again."
    ) from e
except Exception as e:
    raise Exception(
        "Error: An unknown error occurred while connecting to the hue bridge."
    ) from e


# Get the response from the bridge
response_json = response.json()

# Check if the response contains a success message
if response_json[0].get("success"):
    # Extract the username from the success message
    username = response_json[0]["success"]["username"]
    print(f"Success! The username for the new user is: {username}")
else:
    # Extract the error message from the response
    error_message = (
        response_json[0].get("error", {}).get("description", "Unknown error")
    )
    raise Exception(f"Error from bridge response: {error_message}")

# Let the user choose the light group to use
bridge = MyBridge(ip=args.ip, username=username)

groups: list[phue.Group] = bridge.groups  # type: ignore

print("Please choose the light group to use:")
for light_group in groups:
    print(f"{light_group.group_id}: {light_group.name}")

group_name = None
while group_name is None:
    group_id = input("Group ID: ")
    group_name = next(
        (group.name for group in groups if group.group_id == int(group_id)), None
    )
    if group_name is None:
        print("Invalid group ID. Please try again.")
    else:
        print(f"Using group: {group_name}")


hue_dict = {}
hue_dict["ip"] = args.ip
hue_dict["username"] = username
hue_dict["group_name"] = group_name
hue_dict["app_name"] = args.name

# Default app settings
POLLING_INTERVAL_SECONDS = 10
BLINK_DURATION_SECONDS = 10
SYNC_DELAY_SECONDS = 10

app_dict = {}
app_dict["polling_interval_seconds"] = POLLING_INTERVAL_SECONDS
app_dict["blink_duration_seconds"] = BLINK_DURATION_SECONDS
app_dict["sync_delay_seconds"] = SYNC_DELAY_SECONDS

config_dict = {}
config_dict["hue_settings"] = hue_dict
config_dict["app_settings"] = app_dict


with open(args.config, "w") as f:
    yaml.dump(config_dict, f)

print("Config file saved to: ", Path(args.config).resolve())
