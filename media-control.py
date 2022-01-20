#!/usr/bin/python3
import argparse
import os
import sys
from dasbus.client.proxy import ObjectProxy
from dasbus.connection import SessionMessageBus
from dasbus.error import DBusError


def action(command: str, content: str) -> str:
    return f"%{{A1:{os.path.realpath(__file__)} {args.media} {command}:}}{content}%{{A}}"


def font(number: int, content: str) -> str:
    return f"%{{T{number}}}{content}%{{T-}}"


def truncate(text: str, max_len: int) -> str:
    return text[:max_len] + "..." if len(text) > max_len > 0 else text


parser = argparse.ArgumentParser()
parser.add_argument(
    'media',
    type = str,
    choices = ["spotify", "browser"],
    help = "Media to be controlled, is the only required argument"
)
parser.add_argument(
    '-f',
    '--format',
    type = str,
    default = "{prev} {media} {artist}: {song} {play_pause} {next}",
    help = "Output format, components are {prev} {next} {play_pause} {media} {artist} {song}, default -> {prev} {media} {artist}: {song} {play_pause} {next}",
    dest = "format"
)
parser.add_argument(
    "-i",
    "--icons",
    type = str,
    nargs = 5,
    default = ["\uf04a", "", "\uf04b", "\uf04c", "\uf04e"],
    help = "Icons to display (in order): prev media play pause next, use _ to skip and use the default one"
)
parser.add_argument(
    "--icons-fonts",
    type = str,
    nargs = 5,
    help = "Index of the font to use with the icons (in order): prev media play pause next, use _ to skip and use the default one",
    dest = "icons_fonts"
)
parser.add_argument(
    '-t',
    '--trunclen',
    type = int,
    default = 25,
    help = 'Max length of each label (artist and song)',
    dest = "trunclen"
)
parser.add_argument(
    '-q',
    '--quiet',
    action = 'store_true',
    help = "If set, don't show any output when the current song is paused",
    dest = 'quiet',
)
parser.add_argument(  # Internal argument, do NOT use
    '--play_pause',
    action = "store_true",
    help = argparse.SUPPRESS
)
parser.add_argument(  # Internal argument, do NOT use
    '--next',
    action = "store_true",
    help = argparse.SUPPRESS
)
parser.add_argument(  # Internal argument, do NOT use
    '--prev',
    action = "store_true",
    help = argparse.SUPPRESS
)
args = parser.parse_args()
SERVICE_MAP = {"spotify": "org.mpris.MediaPlayer2.spotify", "browser": "org.kde.plasma.browser_integration"}
MEDIA_ICON_MAP = {"spotify": "\uf1bc", "browser": "\uf16a"}
DEFAULT_ICONS = ["\uf04a", MEDIA_ICON_MAP[args.media], "\uf04b", "\uf04c", "\uf04e"]
bus = SessionMessageBus()
try:
    player: ObjectProxy = bus.get_proxy(  # Get DBus object
        service_name = SERVICE_MAP[args.media],
        object_path = "/org/mpris/MediaPlayer2"
    )
    if args.play_pause:
        player.PlayPause()
        sys.exit()
    if args.next:
        player.Next()
        sys.exit()
    if args.prev:
        player.Previous()
        sys.exit()
    if args.quiet and player.PlaybackStatus != "Playing":
        print("")
        sys.exit()

    if not player.CanGoNext:
        args.format = args.format.replace("{next}", "")
    if not player.CanGoPrevious:
        args.format = args.format.replace("{prev}", "")
    if args.icons[1] == "":
        args.icons = [args.icons if i != '_' else d for i, d in zip(args.icons, DEFAULT_ICONS)]
    if args.icons_fonts is not None:
        args.icons = [font(n, i) if n != '_' else i for n, i in zip(args.icons_fonts, args.icons)]

    artists = eval(str(player.Metadata["xesam:artist"]))
    if type(artists) == list:
        artists = " ".join([str(artist).strip("'") for artist in player.Metadata["xesam:artist"]])
    else:
        artists = str(player.Metadata["xesam:artist"]).strip("'")
    title = str(player.Metadata["xesam:title"]).strip("'")
    print(args.format.format(prev = action("--prev", args.icons[0]),
                             media = args.icons[1],
                             artist = truncate(artists, args.trunclen),
                             song = truncate(title, args.trunclen),
                             play_pause = action("--play_pause", args.icons[3] if player.PlaybackStatus == "Playing" else args.icons[2]),
                             next = action("--next", args.icons[4])))
except (DBusError, KeyError):
    print("")
    sys.exit()  # No player available
