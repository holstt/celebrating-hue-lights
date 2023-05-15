import argparse


def get_args():
    args = argparse.ArgumentParser()

    # Match url
    args.add_argument(
        "--url",
        "-m",
        type=str,
        help="URL to the match",
        required=True,
    )

    # Name of the favorite team
    args.add_argument(
        "--fav",
        "-f",
        type=str,
        help="Name of the favorite team",
        required=True,
    )

    # Optional path to config file
    args.add_argument(
        "--config",
        "-c",
        type=str,
        help="Path to config file",
        default="config.yaml",
    )

    args = args.parse_args()
    return args
