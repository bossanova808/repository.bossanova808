from bossanova808.constants import *
from bossanova808.logger import Logger
from bossanova808.utilities import footprints
# noinspection PyPackages
from .store import Store


def run(args):

    footprints()
    Store()

    Logger.info(f"Running plugin with {args}")
    # RUN MODE - DEFAULT - supply the playlist

    Logger.info(Store.switchback_list)
    # if len(args) == 1:
    #     Logger.info("RUN MODE - DEFAULT")
    # # RUN MODE - delete - remove item from playlist
    # elif args[1] == 'action':
    #     pass
    # # SHOULD NEVER HAPPEN
    # else:
    #     Logger.error(f"Couldn't interperet switchback plugin arguments: {args}")

    footprints(startup=False)
