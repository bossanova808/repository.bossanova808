from bossanova808 import exception_logger
from resources.lib import starter

if __name__ == "__main__":
    with exception_logger.log_exception():
        starter.run()
