import json
from dataclasses import dataclass


@dataclass
class Playback:
    """
    Stores data about a Kodi Playback
    """
    file:str = ""
    type:str = ""
    source:str = ""
    dbid:int = None
    title:str = ""
    thumbnail:str = ""
    fanart:str = ""
    poster:str = ""
    year:int = 0
    showtitle:str = ""
    season:int = 0
    episode:int = 0
    resumetime:float = 0
    totaltime:float = 0
    artist:str = ""
    album:str = ""
    duration:int = 0

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)

