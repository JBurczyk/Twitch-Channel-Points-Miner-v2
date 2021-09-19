# -*- coding: utf-8 -*-

import logging

from colorama.ansi import Fore
from TwitchChannelPointsMiner.logger import ColorPalette, LoggerSettings
from TwitchChannelPointsMiner.classes.entities.Bet import BetSettings, Condition, DelayMode, FilterCondition, OutcomeKeys, Strategy
from TwitchChannelPointsMiner.classes.entities.Streamer import Streamer, StreamerSettings
from TwitchChannelPointsMiner.classes.Settings import Priority
from TwitchChannelPointsMiner import TwitchChannelPointsMiner
import argparse
import getpass
import yaml


def dict_to_streamer(streamer) -> Streamer:
    if isinstance(streamer, str):
        return streamer
    if isinstance(streamer, dict):
        streamer_name = list(streamer.keys())[0]
        return Streamer(streamer_name, settings=StreamerSettings(**streamer.get(streamer_name, None)))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Insert Twitch credentials either per command line or config file. If both provided command line has priority. If no password provided you will be asked interactively")

    parser.add_argument(
        "-c", "--config", help="Path to Config File", required=True)
    parser.add_argument("-u", "--username", help="Twitch Username")
    parser.add_argument("-p", "--password", help="Twitch Password")

    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    username = (
        args.username
        if args.username not in [None, ""]
        else config.get("username")
    )

    password = (
        args.password
        if args.password not in [None, ""]
        else config.get("password")
        if "password" in config and config.get("password") != ""
        else getpass.getpass(f"Enter Twitch password for {username}: ")
    )

    twitch_miner = TwitchChannelPointsMiner(
        username=username,
        password=password,
        claim_drops_startup=config.get("claim_drops_startup", False),
        priority=list(map(lambda x: Priority[x], config.get("priority", None))) if config.get("priority", None) is not None else [Priority.STREAK, Priority.DROPS, Priority.ORDER],
        streamer_settings=StreamerSettings(**config.get("default", {})),
        logger_settings=LoggerSettings(**config.get("logging", {}))
    )

    if "dashboard" in config:
        dashboard = config.get("dashboard", {})
        if dashboard is None: dashboard = {}
        twitch_miner.analytics(
            host=dashboard.get("host", "127.0.0.1"),
            port=dashboard.get("port", 5000),
            refresh=dashboard.get("refresh", 5),
        )

    twitch_miner.mine(streamers=list(map(dict_to_streamer, config.get("streamers"))),
                      followers=config.get("include_followers", False))
