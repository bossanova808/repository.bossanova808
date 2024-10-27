import json
from dataclasses import dataclass


@dataclass
class Playback:
    """
    Stores data about a Kodi Playback
    """
    file:str = ""
    # type:str = ""
    id:int = 0
    title:str = ""
    thumbnail:str = ""
    fanart:str = ""
    year:int = 0
    showtitle:str = ""
    season:int = 0
    episode:int = 0
    # artist:str = ""
    # album:str = ""
    # duration:int = 0
    # streamdetails:str = ""

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)
