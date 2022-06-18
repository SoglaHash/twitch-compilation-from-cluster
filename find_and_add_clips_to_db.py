#!/usr/bin/python3
import argparse
from datetime import timedelta, datetime

from model.mydb import Mydb
from model import twitch_api
from model.clips import Clip
from cfg.data import CLUSTERS
from model.cluster import Creator


twitch_credentials = {
   "client_id": "3v7w9gbeuaz6d6hiwlk448nw7lrsl3",
   "client_secret": "n23yzkko4ewa4oguwx962pkbg55uby"
}


class TwitchSelectorRequests():
    def __init__(self):
        self.twitch_oauth_header = twitch_api.login(twitch_credentials)

    def get_clips_from_id(self, id: str, args):
        started_at=datetime.utcnow() - timedelta(days=int(args.days))
        ended_at=datetime.utcnow() - timedelta(hours=12)
        requests = twitch_api.get_clips_request_by_id(
            self.twitch_oauth_header, id, started_at, ended_at
        )
        def _format_to_clip(request: dict) -> Clip:
            try:
                game = twitch_api.TWITCH_GAME_ID_TO_NAME.id_to_game(request['game_id'])
            except (ValueError, IndexError):
                game = "unknown"
                print(f"Game not found!\n\t{request['game_id']}")
            return Clip(creator=Creator(request['broadcaster_name']),request=request, game=game)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted

    def get_clips_from_clip_id(self, clip_id: str, args):
        requests = twitch_api.get_clips_request_by_clip_id(
            self.twitch_oauth_header, clip_id
        )
        def _format_to_clip(request: dict) -> Clip:
            try:
                game = twitch_api.TWITCH_GAME_ID_TO_NAME.id_to_game(request['game_id'])
            except (ValueError, IndexError):
                game = "unknown"
                print(f"Game not found!\n\t{request['game_id']}")
            return Clip(creator=Creator(request['broadcaster_name']),request=request, game=game)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted

    def get_clips_from_category(self, category_name: str, args):
        started_at=datetime.utcnow() - timedelta(days=int(args.days))
        ended_at=datetime.utcnow() - timedelta(hours=12)
        requests = twitch_api.get_clips_request_by_category(
            self.twitch_oauth_header, category_name, started_at, ended_at
        )
        def _format_to_clip(request: dict) -> Clip:
            return Clip(creator=Creator(request['broadcaster_name']),request=request, game=category_name)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted

    def get_clips_from_creator(self, creator: Creator, args):
        started_at=datetime.utcnow() - timedelta(days=int(args.days))
        ended_at=datetime.utcnow() - timedelta(hours=12)
        try:
            requests = twitch_api.get_clips_request_by_streamer(
                self.twitch_oauth_header, creator.name, started_at, ended_at
            )
        except Exception as e:
            # banned?
            print(creator.name)
            return []

        def _format_to_clip(request: dict) -> Clip:
            try:
                game = twitch_api.TWITCH_GAME_ID_TO_NAME.id_to_game(request['game_id'])
            except (ValueError, IndexError):
                game = "unknown"
                print(f"Game not found!\n\t{request['game_id']}")
            return Clip(creator, request, game)
        clips_formatted = list(map(_format_to_clip, requests))
        return clips_formatted


def write_clips_to_db(clips):
    db = Mydb()
    for c in clips:
        db.add(c)
    db.commit()

def find_and_add_clips_to_db(args):
    twitch_clip_requests = TwitchSelectorRequests()
    if args.game_ids:
        for game_id in args.game_ids:
            clips = twitch_clip_requests.get_clips_from_id(game_id, args)
            print(f"\tFound: {len(clips)} clips!")
            write_clips_to_db(clips)
    if args.categories:
        for category in args.categories:
            if not twitch_api.TWITCH_GAME_ID_TO_NAME.is_valid_game(category):
                print(f'Not valid category name! Check CAPS or USE ID INSTEAD:\n\t{category}')
                continue
            clips = twitch_clip_requests.get_clips_from_category(category, args)
            print(f"\tFound: {len(clips)} clips!")
            write_clips_to_db(clips)
    if args.clip_ids:
        for clip_id in args.clip_ids:
            clips = twitch_clip_requests.get_clips_from_clip_id(clip_id, args)
            print(f"\tFound: {len(clips)} clips!")
            write_clips_to_db(clips)
    if args.creators:
        for creator in creators:
            print(creator.name)
            clips = twitch_clip_requests.get_clips_from_creator(creator, args)
            print(f"\tFound: {len(clips)} clips!")
            write_clips_to_db(clips)
    if args.clusters:
        creators = []
        for c in args.clusters:
            creators += CLUSTERS.by_name(c).creators
        for creator in creators:
            print(creator.name)
            clips = twitch_clip_requests.get_clips_from_creator(creator, args)
            print(f"\tFound: {len(clips)} clips!")
            write_clips_to_db(clips)

def argparser():
    parser = argparse.ArgumentParser()
    # Inputs
    parser.add_argument("--cluster", nargs='+', help="clusterfile with name(s) of twitch channel (creator)")
    parser.add_argument("--creators", nargs='+', help="set if list of creators")
    parser.add_argument("--game_ids", nargs='+', help="set if input are game id ex 12345 ")
    parser.add_argument("--clip_ids", nargs='+', help="set if input are clip id ex AwkardHelpless... ")
    parser.add_argument("--categories", nargs='+', help="set if input is category ex 'Just Chatting'")
    # Options
    parser.add_argument("--days", default="30", help="pick n days")
    return parser.parse_args()

if __name__ == "__main__":
    args = argparser()
    find_and_add_clips_to_db(args)