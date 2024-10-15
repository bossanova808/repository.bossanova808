from bossanova808 import exception_logger
from resources.lib import ozweather_skinpatcher

if __name__ == "__main__":
    with exception_logger.log_exception():
        ozweather_skinpatcher.run()
