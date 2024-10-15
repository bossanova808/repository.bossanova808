from bossanova808 import exception_logger
import sys
from resources.lib import kodi_yoctodisplay

if __name__ == "__main__":
    with exception_logger.log_exception():
        kodi_yoctodisplay.run(sys.argv)
