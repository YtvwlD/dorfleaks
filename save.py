#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import dateutil.parser
import json
from os import environ
from sys import argv
from collections import Counter
from mastodon import Mastodon
import typing

@dataclass
class Toot:
    id: str
    author: str
    content: str
    timestamp: datetime

    @classmethod
    def from_api(cls, toot) -> Self:
        return cls(
            toot.uri,
            toot.account.uri,
            toot.content,
            toot.created_at,
        )

    @classmethod
    def from_json(cls, toot: dict[str, object]) -> Self:
        toot["timestamp"] = datetime.fromisoformat(toot["timestamp"])
        return cls(**toot)

    def to_json(self) -> dict[str, object]:
        d = self.__dict__.copy()
        d["timestamp"] = self.timestamp.isoformat()
        return d


# deserialize
saved = None
try:
    with open("dorfleaks-saved.json", "r") as saved_file:
        saved = json.load(saved_file)
        saved["toots"] = {
            id: Toot.from_json(toot)
            for (id, toot) in saved.get("toots", {}).items()
        }
except FileNotFoundError:
    pass

if not saved:
    saved = dict()

mastodon = Mastodon(api_base_url="https://chaos.social/")

if len(argv) == 2:
    id = argv[-1]
    print("Saving the specified toot: {}".format(id))
    raise NotImplementedError()

else:
    # move all twitter data
    if "twitter" not in saved.keys():
        saved = {"twitter": saved}
    
    # the actual logic:
    # get all toots with this hashtag
    # remove all non-relevant data
    toots = map(Toot.from_api, mastodon.timeline_hashtag("dorfleaks"))
    # merge with existing data
    saved["toots"] = saved.get("toots", {})
    for toot in toots:
        if toot.id not in saved["toots"].keys():
            print(f"Saving {toot.id}...")
            saved["toots"][toot.id] = toot

# serialize
saved["toots"] = {id: toot.to_json() for (id, toot) in saved["toots"].items()}
with open("dorfleaks-saved.json", "w") as saved_file:
    json.dump(saved, saved_file)
