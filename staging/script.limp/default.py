from bossanova808 import exception_logger
from resources.lib import limp

if __name__ == "__main__":
    with exception_logger.log_exception():
        limp.run()
