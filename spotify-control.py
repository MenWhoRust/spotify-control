#!/usr/bin/python3

import requests
import sys
import os

clientId = os.getenv("SPOTIFY_CLIENT_ID")
secret = os.getenv("SPOTIFY_CLIENT_SECRET")


def get_access_token() -> str:
    grant_type = {'grant_type': 'client_credentials'}

    r = requests.post("https://accounts.spotify.com/api/token", auth=(clientId, secret), data=grant_type)

    access_token_json = r.json()
    return access_token_json["access_token"]


def search_spotify(query, query_type):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {get_access_token()}'
    }
    params = {
        'q': query,
        'type': query_type
    }

    search_results = requests.get("https://api.spotify.com/v1/search", params=params, headers=headers).json()
    top_result = search_results[query_type + 's']["items"][0]["uri"]
    return top_result


def query_type_dict(type_string):
    switcher = {
        'p': 'playlist',
        'play': 'playlist',
        'playlist': 'playlist',
        't': 'track',
        'track': 'track',
    }
    return switcher.get(type_string, 'track')


def command_dict(command_string):
    switcher = {
        'p': 'Previous',
        'prev': 'Previous',
        'previous': 'Previous',
        'n': 'Next',
        'next': 'Next',
        'pp': 'PlayPause',
        't': 'PlayPause',
        'pa': "Pause"
    }
    return switcher.get(command_string, None)


def run_dbus_command(command, command_args=''):
    os.system(f'dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 '
              f'org.mpris.MediaPlayer2.Player.{command} {command_args} > /dev/null ')


def open_uri(uri):
    run_dbus_command('OpenUri', f'"string:{uri}"')


def main(argv):
    query_arr = ' '.join(argv).split(":")

    if len(query_arr) == 1:
        command = command_dict(query_arr[0])
        if command is None:
            return
        else:
            run_dbus_command(command)
            return

    query = query_arr[1]
    query_type = query_type_dict(query_arr[0].lower())

    open_uri(search_spotify(query, query_type))


if __name__ == '__main__':
    main(sys.argv[1:])
